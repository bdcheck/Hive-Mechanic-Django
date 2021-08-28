# pylint: disable=no-member, line-too-long
# -*- coding: utf-8 -*-

from __future__ import print_function

from builtins import str # pylint: disable=redefined-builtin

import difflib
import hashlib
import json
import pkgutil

from future import standard_library

import requests

from six import python_2_unicode_compatible

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from django_dialog_engine.models import Dialog, DialogStateTransition

from . import card_issues

standard_library.install_aliases()

class PermissionsSupport(models.Model):
    class Meta: # pylint: disable=old-style-class, no-init, too-few-public-methods
        managed = False
        default_permissions = ()

        permissions = (
            ('builder_login', 'Access Hive Mechanic game builder'),
            ('builder_auth_access_view', 'View user account information'),
            ('builder_auth_access_edit', 'Edit user account information'),
            ('builder_access_view', 'View game builder information'),
            ('builder_access_edit', 'Edit game builder information'),
            ('builder_db_logging_view', 'View database logging entries'),
            ('builder_db_logging_edit', 'Edit database logging entries'),
        )

class RemoteRepository(models.Model):
    class Meta: # pylint: disable=old-style-class, no-init, too-few-public-methods
        verbose_name_plural = "Remote Repositories"

    name = models.CharField(max_length=4096, unique=True)
    url = models.URLField(max_length=4096, unique=True)

    priority = models.IntegerField(default=0)

    repository_definition = models.TextField(max_length=1048576, null=True, blank=True)

    last_updated = models.DateTimeField(null=True, blank=True)

@python_2_unicode_compatible
class InteractionCard(models.Model):
    name = models.CharField(max_length=4096, unique=True)
    identifier = models.SlugField(max_length=4096, unique=True)

    description = models.TextField(max_length=16384, null=True, blank=True)

    enabled = models.BooleanField(default=True)

    evaluate_function = models.TextField(max_length=1048576, default='return None, [], None')
    entry_actions = models.TextField(max_length=1048576, default='return []')

    client_implementation = models.FileField(upload_to='interaction_cards/', null=True, blank=True)

    metadata = models.TextField(max_length=1048576, null=True, blank=True)
    repository_definition = models.TextField(max_length=1048576, null=True, blank=True)

    version = models.FloatField(default=0.0)

    def __str__(self):
        return self.name + ' (' + self.identifier + ')'

    def issues(self):
        identified_issues = []

        prefix = card_issues.__name__ + "."

        for importer, modname, ispkg in pkgutil.iter_modules(card_issues.__path__, prefix): # pylint: disable=unused-variable
            module = __import__(modname, fromlist="dummy")

            if self.entry_actions is not None:
                for issue in module.evaluate(self.entry_actions):
                    identified_issues.append('Entry Actions: ' + issue)

            if self.evaluate_function is not None:
                for issue in module.evaluate(self.evaluate_function):
                    identified_issues.append('Evaluate Function: ' + issue)

        if identified_issues:
            return mark_safe('<br />'.join(identified_issues)) # nosec

        return None

    def available_update(self):
        try:
            try:
                card_metadata = json.loads(self.repository_definition)

                if 'versions' in card_metadata:
                    versions = sorted(card_metadata['versions'], key=lambda version: version.get('version', ''))

                    if versions and 'version' in versions[-1]:
                        if self.version >= versions[-1]['version']:
                            return None

                        return versions[-1]['version']
            except json.JSONDecodeError:
                pass

            return None
        except TypeError:
            pass

        return None

    def update_card(self):
        messages = []

        if self.available_update() is not None:
            try:
                card_metadata = json.loads(self.repository_definition)

                versions = sorted(card_metadata['versions'], key=lambda version: version['version'])

                latest_version = versions[-1]

                entry_content = requests.get(latest_version['entry-actions']).content
                evaluate_content = requests.get(latest_version['evaluate-function']).content
                client_content = requests.get(latest_version['client-implementation']).content

                computed_hash = hashlib.sha512()

                computed_hash.update(entry_content)
                computed_hash.update(evaluate_content)
                computed_hash.update(client_content)

                local_hash = computed_hash.hexdigest()

                if local_hash == latest_version['sha512-hash']:
                    self.entry_actions = entry_content.decode("utf-8")
                    self.evaluate_function = evaluate_content.decode("utf-8")

                    self.version = latest_version['version']

                    self.save()

                    self.client_implementation.save(self.identifier + '.js', ContentFile(client_content))

                    messages.append('[Success] ' + self.identifier + ': Updated to latest version.')
                else:
                    messages.append('[Error] ' + self.identifier + ': Unable to update to latest version. Remote hash does not match file contents.')
            except TypeError:
                messages.append('[Error] ' + self.identifier + ': Unable to parse update information.')

        return messages

    def print_repository_diffs(self):
        try:
            repo_metadata = json.loads(self.repository_definition)

            if 'versions' in repo_metadata:
                versions = list(repo_metadata['versions'])

                versions.sort(key=lambda version: version['version'], reverse=True)

                if versions:
                    latest_version = versions[0]

                    repo_entry = requests.get(latest_version['entry-actions']).text
                    repo_evaluate = requests.get(latest_version['evaluate-function']).text
                    repo_client = requests.get(latest_version['client-implementation']).text

                    local_client = open(self.client_implementation.path).read()

                    entry_diff = list(difflib.unified_diff(repo_entry.splitlines(), self.entry_actions.splitlines(), lineterm=''))
                    eval_diff = list(difflib.unified_diff(repo_evaluate.splitlines(), self.evaluate_function.splitlines(), lineterm=''))
                    client_diff = list(difflib.unified_diff(repo_client.splitlines(), local_client.splitlines(), lineterm=''))

                    if entry_diff:
                        print('--- Entry Actions: ' + self.identifier + '[' + str(latest_version['version']) + '] ---')
                        print('    ' + '\n    '.join(entry_diff))

                    if eval_diff:
                        print('--- Evaluation Function: ' + self.identifier + '[' + str(latest_version['version']) + '] ---')
                        print('    ' + '\n    '.join(eval_diff))

                    if client_diff:
                        print('--- Client Implementation: ' + self.identifier + '[' + str(latest_version['version']) + '] ---')
                        print('    ' + '\n    '.join(client_diff))
                else:
                    print('No repository definition for ' + self.name + ' ("' + self.identifier + '"). [3]')
            else:
                print('No repository definition for ' + self.name + ' ("' + self.identifier + '"). [2]')
        except json.decoder.JSONDecodeError:
            print('No repository definition for ' + self.name + ' ("' + self.identifier + '"). [1]')

@python_2_unicode_compatible
class Game(models.Model):
    name = models.CharField(max_length=1024, db_index=True)
    slug = models.SlugField(max_length=1024, db_index=True, unique=True)

    cards = models.ManyToManyField(InteractionCard, related_name='games')

    game_state = JSONField(default=dict)

    editors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='builder_game_editables')
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='builder_game_viewables')

    def __str__(self):
        return str(self.name)

    def definition_json(self):
        return reverse('builder_game_definition_json', args=[self.slug])

    def interaction_card_modules_json(self):
        modules = []

        for card in self.cards.all():
            modules.append(reverse('builder_interaction_card', args=[card.identifier]))

        return mark_safe(json.dumps(modules)) # nosec

    def current_active_session(self, player):
        session = None

        for version in self.versions.order_by('-created'):
            if session is None:
                session = version.sessions.filter(player=player, completed=None).order_by('-started').first()

        return session

    def set_variable(self, variable, value):
        self.game_state[variable] = value # pylint: disable=unsupported-assignment-operation
        self.save()

    def fetch_variable(self, variable):
        if variable in self.game_state: # pylint: disable=unsupported-membership-test
            return self.game_state[variable] # pylint: disable=unsubscriptable-object

        return None

    def active_session_count(self):
        count = 0

        for version in self.versions.all():
            for session in version.sessions.all():
                if session.completed is None:
                    count += 1

        return count

    def inactive_session_count(self):
        count = 0

        for version in self.versions.all():
            for session in version.sessions.all():
                if session.completed is not None:
                    count += 1

        return count

    def can_view(self, user):
        if user.is_authenticated is False:
            return False

        if self.can_edit(user):
            return True

        if (self.editors.count() == 0 and self.viewers.count() == 0) or self.viewers.filter(pk=user.pk).count() > 0:
            return True

        return False

    def can_edit(self, user):
        if user.is_authenticated is False:
            return False

        if (self.editors.count() == 0 and self.viewers.count() == 0) or self.editors.filter(pk=user.pk).count() > 0:
            return True

        return False

@python_2_unicode_compatible
class GameVersion(models.Model):
    game = models.ForeignKey(Game, related_name='versions', on_delete=models.CASCADE)
    created = models.DateTimeField()

    definition = models.TextField(max_length=(1024 * 1024 * 1024))

    def __str__(self):
        return self.game.name + ' (' + str(self.created) + ')'

    def process_incoming(self, session, payload, extras=None):
        actions = []

        if self.interrupt(payload, session) is False:
            dialog = session.dialog()

            new_actions = dialog.process(payload, extras={'session': session, 'extras': extras})

            while new_actions is not None and len(new_actions) > 0: # pylint: disable=len-as-condition
                actions.extend(new_actions)

                new_actions = dialog.process(None, extras={'session': session, 'extras': extras})

            if dialog.finished is not None:
                session.completed = dialog.finished
                session.save()

        return actions

    def interrupt(self, payload, session):
        definition = json.loads(self.definition)

        if 'interrupts' in definition:
            for interrupt in definition['interrupts']:
                for integration in self.game.integrations.all():
                    if integration.is_interrupt(interrupt['pattern'], payload):
                        session.set_variable('hive_interrupted_location', session.current_node())

                        session.advance_to(interrupt['action'])

                        return True

        return False

    def dialog_snapshot(self):
        snapshot = []

        definition = json.loads(self.definition)

        sequences = []

        initial_card = None

        if 'sequences' in definition:
            sequences = definition['sequences']

            if 'initial-card' in definition:
                initial_card = definition['initial-card']
        else:
            sequences = definition

        for sequence in sequences:
            for item in sequence['items']:
                item_id = item['id']

                if ((sequence['id'] + '#') in item_id) is False:
                    item_id = sequence['id'] + '#' + item_id

                if len(snapshot) == 0: # pylint: disable=len-as-condition
                    if initial_card is not None:
                        snapshot.append({
                            'type': 'begin',
                            'id': 'dialog-start',
                            'next_id': initial_card
                        })
                    else:
                        snapshot.append({
                            'type': 'begin',
                            'id': 'dialog-start',
                            'next_id': item_id
                        })

                interaction_card = InteractionCard.objects.filter(identifier=item['type']).first()

                item['sequence_id'] = sequence['id']

                if interaction_card is not None:
                    snapshot.append({
                        'type': 'custom',
                        'id': item_id,
                        'definition': item,
                        'evaluate': interaction_card.evaluate_function,
                        'actions': interaction_card.entry_actions
                    })
                else:
                    snapshot.append({
                        'type': 'echo',
                        'id': item_id,
                        'next_id': 'dialog-end',
                        'message': 'Unknown interaction type "' + item['type'] + '".'
                    })

        snapshot.append({
            'type': 'end',
            'id': 'dialog-end'
        })

        return snapshot

    def complete_identifier(self, incomplete_id, dialog):
        if '#' in incomplete_id:
            return incomplete_id

        last_transition = DialogStateTransition.objects.filter(dialog=dialog).order_by('-when').first()

        dialog_definition = json.loads(self.definition)

        # Look in last transition for partial ID...

        if last_transition is not None: # pylint: disable=too-many-nested-blocks
            last_state_id = last_transition.state_id

            if '#' in last_state_id and last_state_id.startswith('#') is False:
                tokens = last_state_id.split('#', 1)

                for sequence in dialog_definition['sequences']:
                    if sequence['id'] == tokens[0]:
                        for item in sequence['items']:
                            if item['id'] == incomplete_id:
                                return sequence['id'] + '#' + incomplete_id

        # Look in other sequences for partial ID...

        for sequence in dialog_definition['sequences']:
            for item in sequence['items']:
                if item['id'] == incomplete_id:
                    return sequence['id'] + '#' + incomplete_id

        return incomplete_id


@python_2_unicode_compatible
class Player(models.Model):
    identifier = models.CharField(max_length=4096, unique=True)

    player_state = JSONField(default=dict)

    def set_variable(self, variable, value):
        self.player_state[variable] = value # pylint: disable=unsupported-assignment-operation
        self.save()

    def fetch_variable(self, variable):
        if variable in self.player_state: # pylint: disable=unsupported-membership-test
            return self.player_state[variable] # pylint: disable=unsubscriptable-object

        return None

    def __str__(self):
        return self.identifier.split(':')[-1]

    def most_recent_game(self):
        latest = self.sessions.order_by('-started').first()

        if latest is not None:
            return latest.game_version.game

        return None

    def earliest_session(self):
        return self.sessions.order_by('started').first()

    def active_session_count(self):
        return self.sessions.filter(completed=None).count()

    def inactive_session_count(self):
        return self.sessions.exclude(completed=None).count()

class Session(models.Model):
    player = models.ForeignKey(Player, related_name='sessions', on_delete=models.CASCADE)
    game_version = models.ForeignKey(GameVersion, related_name='sessions', on_delete=models.CASCADE)

    started = models.DateTimeField()
    completed = models.DateTimeField(null=True, blank=True)

    session_state = JSONField(default=dict)

    def complete_identifier(self, incomplete_id):
        return self.game_version.complete_identifier(incomplete_id, self.dialog())

    def process_incoming(self, integration, payload, extras=None):
        current_node = None # pylint: disable=unused-variable

        if 'session_current_node' in self.session_state: # pylint: disable=unsupported-membership-test
            current_node = self.session_state['session_current_node'] # pylint: disable=unsubscriptable-object

        actions = self.game_version.process_incoming(self, payload, extras)

        if integration is not None:
            integration.execute_actions(self, actions)
        else:
            for game_integration in self.game_version.game.integrations.all():
                game_integration.execute_actions(self, actions)

    def nudge(self):
        self.process_incoming(None, None)

    def set_variable(self, variable, value):
        self.session_state[variable] = value # pylint: disable=unsupported-assignment-operation
        self.save()

    def fetch_variable(self, variable):
        if variable.startswith('[') and variable.endswith(']'):
            value = None

            for game_integration in self.game_version.game.integrations.all():
                if value is None:
                    value = game_integration.translate_value(variable, self)

            return value

        if variable in self.session_state: # pylint: disable=unsupported-membership-test
            return self.session_state[variable]  # pylint: disable=unsubscriptable-object

        if variable in self.player.player_state:
            return self.player.player_state[variable]

        if variable in self.game_version.game.game_state:
            return self.game_version.game.game_state[variable]

        return None

    def dialog(self):
        dialog_key = 'session-' + str(self.pk)

        dialog = Dialog.objects.filter(key=dialog_key, finished=None).order_by('-started').first()

        if dialog is None:
            dialog = Dialog(key=dialog_key, started=timezone.now())
            dialog.dialog_snapshot = self.game_version.dialog_snapshot()
            dialog.save()

        return dialog

    def current_node(self):
        return self.dialog().current_node()

    def complete(self):
        self.dialog().finish()

        self.completed = timezone.now()
        self.save()

    def last_message(self):
        last_message = None

        for integration in self.game_version.game.integrations.all():
            last_integration_message = integration.last_message_for_player(self.player)

            if last_integration_message is not None:
                if last_message is None or last_message['date'] < last_integration_message['date']: # pylint: disable=unsubscriptable-object
                    last_message = last_integration_message

        if last_message is not None:
            return last_message['message']

        return None

    def last_message_type(self):
        last_message = None

        for integration in self.game_version.game.integrations.all():
            last_integration_message = integration.last_message_for_player(self.player)

            if last_integration_message is not None:
                if last_message is None or last_message['date'] < last_integration_message['date']: # pylint: disable=unsubscriptable-object
                    last_message = last_integration_message

        if last_message is not None:
            return last_message['type']

        return None

    def advance_to(self, destination):
        actions = self.dialog().advance_to(destination)

        print('ACTIONS: ' + str(actions))

        for game_integration in self.game_version.game.integrations.all():
            game_integration.execute_actions(self, actions)

    def fetch_session_context(self):
        return self.session_state.copy()

    def fetch_player_context(self):
        return self.player.player_state.copy()

    def fetch_game_context(self):
        return self.game_version.game.game_state.copy()


class DataProcessor(models.Model):
    name = models.CharField(max_length=4096, unique=True)
    identifier = models.SlugField(max_length=4096, unique=True)

    description = models.TextField(max_length=16384, null=True, blank=True)

    enabled = models.BooleanField(default=True)

    processor_function = models.TextField(max_length=1048576, default='return None, [], None')

    metadata = models.TextField(max_length=1048576, null=True, blank=True)
    repository_definition = models.TextField(max_length=1048576, null=True, blank=True)

    version = models.FloatField(default=0.0)

    def __unicode__(self):
        return self.name + ' (' + self.identifier + ')'

    def issues(self): # pylint: disable=no-self-use
        return 'TODO'

    def available_update(self):
        try:
            try:
                repo_metadata = json.loads(self.repository_definition)

                if 'versions' in repo_metadata:
                    versions = sorted(repo_metadata['versions'], key=lambda version: version.get('version', ''))

                    if versions and 'version' in versions[-1]:
                        if self.version >= versions[-1]['version']:
                            return None

                        return versions[-1]['version']
            except json.JSONDecodeError:
                pass

            return None
        except TypeError:
            pass

        return None

    def update_data_processor(self):
        messages = []

        if self.available_update() is not None: # pylint: disable=too-many-nested-blocks
            try:
                processor_metadata = json.loads(self.repository_definition)

                versions = sorted(processor_metadata['versions'], key=lambda version: version['version'])

                latest_version = versions[-1]

                implementation_content = requests.get(latest_version['implementation']).content

                computed_hash = hashlib.sha512()

                computed_hash.update(implementation_content)

                local_hash = computed_hash.hexdigest()

                if local_hash == latest_version['sha512-hash']:
                    self.processor_function = implementation_content.decode("utf-8")

                    self.version = latest_version['version']

                    if 'required-metadata-keys' in latest_version:
                        metadata = {}

                        if self.metadata is not None:
                            metadata = json.loads(self.metadata)

                        for key in latest_version['required-metadata-keys']:
                            if (key in metadata) is False:
                                metadata[key] = ''

                        self.metadata = json.dumps(metadata, indent=2)

                    self.save()
                else:
                    messages.append('[Error] ' + self.identifier + ': Unable to update to latest version. Remote hash does not match file contents.')
            except TypeError:
                messages.append('[Error] ' + self.identifier + ': Unable to parse update information.')

        return messages

    def print_repository_diffs(self):
        try:
            repo_metadata = json.loads(self.repository_definition)

            if 'versions' in repo_metadata:
                versions = list(repo_metadata['versions'])

                versions.sort(key=lambda version: version['version'], reverse=True)

                if versions:
                    latest_version = versions[0]

                    repo_implementation = requests.get(latest_version['implementation']).text

                    implementation_diff = list(difflib.unified_diff(repo_implementation.splitlines(), self.processor_function.splitlines(), lineterm=''))

                    if implementation_diff:
                        print('--- Implementation: ' + self.identifier + '[' + str(latest_version['version']) + '] ---')
                        print('    ' + '\n    '.join(implementation_diff))
                else:
                    print('No repository definition for ' + self.name + ' ("' + self.identifier + '"). [3]')
            else:
                print('No repository definition for ' + self.name + ' ("' + self.identifier + '"). [2]')
        except json.decoder.JSONDecodeError:
            print('No repository definition for ' + self.name + ' ("' + self.identifier + '"). [1]')
