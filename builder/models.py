# pylint: disable=no-member, line-too-long, too-many-lines
# -*- coding: utf-8 -*-

from __future__ import print_function

from builtins import str # pylint: disable=redefined-builtin

import difflib
import hashlib
import json
import os
import pkgutil
import traceback

from future import standard_library

import requests

from six import python_2_unicode_compatible

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.postgres.fields import JSONField
from django.core.checks import Warning, register # pylint: disable=redefined-builtin
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction
from django.db.models.signals import post_delete, pre_save
from django.db.utils import ProgrammingError
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from django_dialog_engine.models import Dialog, DialogStateTransition
from passive_data_kit.models import DataPoint

from activity_logger.models import log

from . import card_issues
from .utils import fetch_cytoscape_node as fetch_cytoscape

standard_library.install_aliases()

CYTOSCAPE_DIALOG_PLACEHOLDER = [{
    'data': {
        'id': 'dialog-start',
        'name': 'dialog-start',
    },
    'group': 'nodes'
}, {
    'data': {
        'id': 'dialog-middle',
        'name': 'dialog-middle',
    },
    'group': 'nodes'
}, {
    'data': {
        'id': 'dialog-end',
        'name': 'dialog-end',
    },
    'group': 'nodes'
}, {
    'data': {
        'id': 'dialog-sm',
        'source': 'dialog-start',
        'target': 'dialog-middle',
    },
    'group': 'edges'
}, {
    'data': {
        'id': 'dialog-me',
        'source': 'dialog-start',
        'target': 'dialog-end',
    },
    'group': 'edges'
}]

@register()
def permissions_check(app_configs, **kwargs): # pylint: disable=unused-argument
    warnings = []

    try:
        if Group.objects.filter(name='Hive Mechanic Reader').count() == 0:
            warnings.append(Warning(
                'Missing required Hive Mechanic groups',
                hint='Run the "initialize_permissions" command to set up required permissions',
                id='builder.W001',
            ))
    except ProgrammingError: # Thrown before migration happens.
        pass

    return warnings

@register()
def inactive_cards_enabled_check(app_configs, **kwargs): # pylint: disable=unused-argument
    warnings = []

    try:
        for game in Game.objects.all():
            for card in game.cards.filter(enabled=False):
                warnings.append(Warning(
                    'Activity "%s" is configured to use disabled card "%s"' % (game, card),
                    hint='Enable the card or remove it from the game configuration to continue.',
                    id='builder.W002',
                ))
    except ProgrammingError: # Thrown before migration happens.
        pass

    return warnings

@register()
def site_settings_check(app_configs, **kwargs): # pylint: disable=unused-argument
    warnings = []

    try:
        if SiteSettings.objects.count() == 0:
            warnings.append(Warning(
                'Missing site settings',
                hint='Add a site settings object in the administration interface',
                id='builder.W003',
            ))
    except ProgrammingError: # Thrown before migration happens.
        pass

    return warnings

def file_cleanup(sender, **kwargs):
    '''
    File cleanup callback used to emulate the old delete
    behavior using signals. Initially django deleted linked
    files when an object containing a File/ImageField was deleted.

    Usage:
    >>> from django.db.models.signals import post_delete
    >>> post_delete.connect(file_cleanup, sender=MyModel, dispatch_uid='mymodel.file_cleanup')

    Adapted from https://timonweb.com/django/cleanup-files-and-images-on-model-delete-in-django/
    '''

    do_cleanup = True

    try:
        do_cleanup = settings.HIVE_DELETE_CLIENT_IMPLEMENTATION_JS
    except AttributeError:
        pass

    if do_cleanup:
        fieldnames = [model_field.name for model_field in sender._meta.get_fields()] # pylint: disable=protected-access

        for fieldname in fieldnames:
            try:
                field = sender._meta.get_field(fieldname) # pylint: disable=protected-access
            except: # pylint: disable=bare-except
                field = None

            if field and isinstance(field, models.FileField):
                inst = kwargs['instance']
                file_field = getattr(inst, fieldname)
                field_manager = inst.__class__._default_manager # pylint: disable=protected-access
                if (hasattr(file_field, 'path') and os.path.exists(file_field.path) and not field_manager.filter(**{'%s__exact' % fieldname: getattr(inst, fieldname)}).exclude(pk=inst._get_pk_val())): # pylint: disable=protected-access
                    default_storage.delete(file_field.path)


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
        verbose_name_plural = 'Remote Repositories'

    name = models.CharField(max_length=4096, unique=True)
    url = models.URLField(max_length=4096, unique=True)

    priority = models.IntegerField(default=0)

    repository_definition = models.TextField(max_length=1048576, null=True, blank=True)

    last_updated = models.DateTimeField(null=True, blank=True)

@python_2_unicode_compatible
class InteractionCardCategory(models.Model):
    name = models.CharField(max_length=4096, unique=True)
    priority = models.IntegerField(default=1)

    def __str__(self):
        return '%s (%d)' % (self.name, int(self.priority))

@python_2_unicode_compatible
class InteractionCard(models.Model):
    name = models.CharField(max_length=4096, unique=True)
    identifier = models.SlugField(max_length=4096, unique=True)
    category = models.ForeignKey(InteractionCardCategory, null=True, blank=True, on_delete=models.SET_NULL)

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

        prefix = card_issues.__name__ + '.'

        for importer, modname, ispkg in pkgutil.iter_modules(card_issues.__path__, prefix): # pylint: disable=unused-variable
            module = __import__(modname, fromlist='dummy')

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

    def update_card(self, force=False):
        messages = []

        if force or self.available_update() is not None:
            try:
                card_metadata = json.loads(self.repository_definition)

                versions = sorted(card_metadata['versions'], key=lambda version: version['version'])

                latest_version = versions[-1]

                entry_content = requests.get(latest_version['entry-actions'], timeout=120).content
                evaluate_content = requests.get(latest_version['evaluate-function'], timeout=120).content
                client_content = requests.get(latest_version['client-implementation'], timeout=120).content

                card_name = card_metadata['name']

                computed_hash = hashlib.sha512()

                computed_hash.update(entry_content)
                computed_hash.update(evaluate_content)
                computed_hash.update(client_content)

                local_hash = computed_hash.hexdigest()

                if local_hash == latest_version['sha512-hash']:
                    self.name = card_name

                    self.entry_actions = entry_content.decode('utf-8')
                    self.entry_actions = entry_content.decode('utf-8')
                    self.evaluate_function = evaluate_content.decode('utf-8')

                    self.version = latest_version['version']

                    self.save()

                    self.client_implementation.save(self.identifier + '.js', ContentFile(client_content))

                    messages.append('[Success] ' + self.identifier + ': Updated to latest version.')
                else:
                    messages.append('[Error] ' + self.identifier + ': Unable to update to latest version. Remote hash does not match file contents.')
            except TypeError:
                messages.append('[Error] ' + self.identifier + ': Unable to parse update information.')
            except json.decoder.JSONDecodeError:
                print('No repository definition for ' + self.name + ' ('' + self.identifier + ''). [1]')

        return messages

    def refresh_card(self):
        return self.update_card(force=True)

    def print_repository_diffs(self):
        try:
            repo_metadata = json.loads(self.repository_definition)

            if 'versions' in repo_metadata:
                versions = list(repo_metadata['versions'])

                versions.sort(key=lambda version: version['version'], reverse=True)

                if versions:
                    latest_version = versions[0]

                    repo_entry = requests.get(latest_version['entry-actions'], timeout=120).text
                    repo_evaluate = requests.get(latest_version['evaluate-function'], timeout=120).text
                    repo_client = requests.get(latest_version['client-implementation'], timeout=120).text

                    with open(self.client_implementation.path, encoding='utf-8') as client_file:
                        local_client = client_file.read()

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
                    print('No repository definition for ' + self.name + ' ('' + self.identifier + ''). [3]')
            else:
                print('No repository definition for ' + self.name + ' ('' + self.identifier + ''). [2]')
        except json.decoder.JSONDecodeError:
            print('No repository definition for ' + self.name + ' ('' + self.identifier + ''). [1]')

post_delete.connect(file_cleanup, sender=InteractionCard, dispatch_uid='builder.interaction_card.file_cleanup')

def reset_game_metadata(sender, instance, *args, **kwargs): # pylint: disable=unused-argument
    instance.metadata_updated = None

@python_2_unicode_compatible  # pylint: disable=too-many-public-methods
class Game(models.Model):
    name = models.CharField(max_length=1024, db_index=True)
    slug = models.SlugField(max_length=1024, db_index=True, unique=True)

    cards = models.ManyToManyField(InteractionCard, related_name='games')

    game_state = JSONField(default=dict, blank=True)

    editors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='builder_game_editables', blank=True)
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='builder_game_viewables', blank=True)

    icon = models.ImageField(null=True, blank=True, upload_to='activity_icons')
    is_template = models.BooleanField(default=False)

    metadata = JSONField(default=dict, blank=True)
    metadata_updated = models.DateTimeField(null=True, blank=True)

    def log_id(self):
        return 'game_version:%d' % self.pk

    def __str__(self):
        return str(self.name)

    def definition_json(self):
        return reverse('builder_game_definition_json', args=[self.slug])

    def fetch_metadata(self, force=False):
        now = timezone.now()

        if force or self.metadata_updated is None or (now - self.metadata_updated).total_seconds() > 300:
            self.metadata = {}

            self.metadata['name'] = self.name
            self.metadata['slug'] = self.slug
            self.metadata['creator'] = self.creator_name()
            self.metadata['versions_count'] = self.versions.count()

            latest_version = self.latest_version()

            if latest_version is not None:
                self.metadata['last_saved'] = latest_version.created

                if latest_version.creator is not None:
                    self.metadata['last_saved_by'] = latest_version.creator.get_full_name()

            last_session = self.last_session_started()

            if last_session is not None:
                self.metadata['last_session_started'] = last_session.started

            self.metadata.update(self.participation_data())

            integrations = []

            for integration in self.integrations.all():
                integration_stats = {}

                integration_stats.update(integration.fetch_statistics())

                if 'game' in integration_stats:
                    del integration_stats['game']

                integrations.append(integration_stats)

            self.metadata['integrations'] = integrations

            clean_metadata = json.dumps(self.metadata, cls=DjangoJSONEncoder)

            self.metadata = json.loads(clean_metadata)

            self.metadata_updated = now

            pre_save.disconnect(reset_game_metadata, sender=Game, dispatch_uid='builder.game.reset_game_metadata')

            self.save()

            pre_save.connect(reset_game_metadata, sender=Game, dispatch_uid='builder.game.reset_game_metadata')

        return self.metadata

    def interaction_card_modules_json(self):
        modules = []

        for card in self.cards.filter(enabled=True):
            modules.append(reverse('builder_interaction_card', args=[card.identifier]))

        return mark_safe(json.dumps(modules)) # nosec

    def interaction_card_categories_json(self): # pylint: disable=invalid-name
        categories = {}

        for card in self.cards.filter(enabled=True):
            category_name = 'Hive Mechanic Card'
            category_priority = 0

            if card.category is not None:
                category_name = card.category.name
                category_priority = card.category.priority

            if (category_name in categories) is False:
                categories[category_name] = {
                    'name': category_name,
                    'priority': category_priority,
                    'cards': []
                }

            categories[category_name]['cards'].append(card.identifier)

        cat_list = list(categories.values())

        cat_list.sort(key=lambda category: category['priority'], reverse=True)

        return mark_safe(json.dumps(cat_list)) # nosec

    def current_active_session(self, player):
        session = None

        for version in self.versions.order_by('-created'):
            if session is None:
                session = version.sessions.filter(player=player, completed=None).order_by('-started').first()

        return session

    @transaction.atomic
    def reset_active_session_variables(self):
        for version in self.versions.all():
            for session in version.sessions.all():
                if session.completed is None:
                    session.session_state = {}
                    session.save()

    @transaction.atomic
    def close_active_sessions(self):
        for version in self.versions.all():
            for session in version.sessions.all():
                if session.completed is None:
                    session.complete()

    @transaction.atomic
    def reset_variables(self):
        self.game_state = {} # pylint: disable=unsupported-assignment-operation
        self.save()

        self.refresh_from_db()

    @transaction.atomic
    def set_variable(self, variable, value):
        old_value = self.game_state.get(variable, None)

        self.game_state[variable] = value # pylint: disable=unsupported-assignment-operation
        self.save()

        self.refresh_from_db()

        metadata = {
            'variable_name': variable,
            'old_value': old_value,
            'new_value': value
        }

        version = self.versions.order_by('-created').first()

        log(self.log_id(), 'Set game variable (%s = %s).' % (variable, value), tags=['game', 'variable'], metadata=metadata, player=None, session=None, game_version=version)

    @transaction.atomic
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

    def active_player_count(self):
        players = []

        for version in self.versions.all():
            for session in version.sessions.filter(completed=None):
                if (session.player.pk in players) is False:
                    players.append(session.player.pk)

        return len(players)

    def total_player_count(self):
        players = []

        for version in self.versions.all():
            for session in version.sessions.all():
                if (session.player.pk in players) is False:
                    players.append(session.player.pk)

        return len(players)

    def last_session_started(self):
        last_session = None

        for version in self.versions.all():
            last_started = version.sessions.all().order_by('-started').first()

            if last_started is not None:
                if last_session is None or last_started.started > last_session.started:
                    last_session = last_started

        return last_session

    def participant_counts(self):
        players = []
        active_players = []

        for version in self.versions.all():
            for session in version.sessions.all():
                if (session.player.pk in players) is False:
                    players.append(session.player.pk)

                if session.completed is None and (session.player.pk in active_players) is False:
                    active_players.append(session.player.pk)

        return (len(players), len(active_players),)

    def participation_data(self):
        players = []
        active_players = []
        sessions = []
        active_sessions = []

        for version in self.versions.all():
            for session in version.sessions.all():
                sessions.append(session.pk)

                if (session.player.pk in players) is False:
                    players.append(session.player.pk)

                if session.completed is None and (session.player.pk in active_players) is False:
                    active_sessions.append(session.pk)
                    active_players.append(session.player.pk)

        cached_info = {
            'active_sessions': len(active_sessions),
            'inactive_sessions': len(sessions) - len(active_sessions),
            'all_sessions': len(sessions),
            'active_players': len(active_players),
            'all_players': len(players),
        }

        return cached_info

    def can_view(self, user):
        if user.is_authenticated is False:
            return False

        if self.can_edit(user):
            return True

        if self.viewers.count() == 0 or self.viewers.filter(pk=user.pk).count() > 0:
            return True

        return False

    def can_edit(self, user):
        if user.is_authenticated is False:
            return False

        if (self.editors.count() == 0 and self.viewers.count() == 0) or self.editors.filter(pk=user.pk).count() > 0:
            return True

        return False

    def cytoscape_json_simple(self, indent=0):
        return self.cytoscape_json(indent=indent, simplify=True)

    def cytoscape_json(self, indent=0, simplify=False):
        version = self.versions.order_by('-created').first()

        if version is not None:
            version_cyto = version.cytoscape_json(indent=indent, simplify=simplify)

            if version_cyto is not None:
                return version_cyto

        if indent > 0:
            return json.dumps(CYTOSCAPE_DIALOG_PLACEHOLDER, indent=indent)

        return json.dumps(CYTOSCAPE_DIALOG_PLACEHOLDER)

    def latest_version(self):
        return self.versions.order_by('-created').first()

    def creator_name(self):
        first_version = self.versions.exclude(creator=None).order_by('created').first()

        if first_version is not None:
            return first_version.creator.get_full_name()

        return 'Unknown'

    def disabled_integrations(self):
        disabled = []

        for integration in self.integrations.all():
            if integration.is_enabled() is False:
                disabled.append(integration)

        return disabled

pre_save.connect(reset_game_metadata, sender=Game, dispatch_uid='builder.game.reset_game_metadata')

@python_2_unicode_compatible
class GameVersion(models.Model):
    game = models.ForeignKey(Game, related_name='versions', on_delete=models.CASCADE)
    created = models.DateTimeField()

    definition = models.TextField(max_length=(1024 * 1024 * 1024), null=True, blank=True)
    cached_cytoscape = models.TextField(max_length=(1024 * 1024 * 1024), null=True, blank=True)

    creator = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)

    def log_id(self):
        return 'game_version:%d' % self.pk

    def __str__(self):
        return self.game.name + ' (' + str(self.created) + ')'

    def process_incoming(self, session, payload, extras=None): # pylint: disable=too-many-branches
        if extras is None:
            extras = {}

        if extras.get('last_message', None) is None:
            last_message = session.player.last_message()

            if last_message is not None:
                extras['last_message'] = {
                    'raw_object': last_message,
                    'message': last_message.message
                }

        actions = []

        if self.interrupt(payload, session, extras) is False: # pylint: disable=too-many-nested-blocks
            dialog = session.dialog()

            if dialog.finished is None:
                new_actions = dialog.process(payload, extras={'session': session, 'extras': extras})

                while new_actions is not None and len(new_actions) > 0: # pylint: disable=len-as-condition
                    added_new_action = False

                    for new_action in new_actions:
                        if (new_action in actions) is False:
                            if new_action.get('type', None) == 'set-variable':
                                for game_integration in self.game.integrations.all():
                                    game_integration.execute_actions(session, [new_action])
                            else:
                                actions.append(new_action)

                                added_new_action = True

                    if added_new_action:
                        new_actions = dialog.process(None, extras={'session': session, 'extras': extras})
                    else:
                        new_actions = [] # Break out of likely endless loop

                if dialog.finished is not None:
                    session.complete(dialog)
            else:
                session.complete(dialog)

        return actions

    def interrupt(self, payload, session, extras):
        if extras is None:
            extras = {}

        definition = json.loads(self.definition)

        if 'message_type' in extras and extras['message_type'] == 'call':
            if 'payload' in extras and 'CallStatus' in extras['payload']:
                if extras['payload']['CallStatus'] == 'ringing':
                    if 'incoming_call_interrupt' in definition:
                        payload = {
                            'variable': 'hive_interrupted_location',
                            'value': session.current_node(),
                            'original_value': session.current_node(),
                            'scope': 'session',
                            'session': 'session-' + str(session.pk),
                            'game': str(session.game_version.game.slug),
                            'player': str(session.player.identifier),
                        }

                        point = DataPoint.objects.create_data_point('hive-incoming-call', session.player.identifier, payload, user_agent='Hive Mechanic')
                        point.save()

                        session.advance_to(definition['incoming_call_interrupt'])

                        session.nudge()

                        return True

        if 'interrupts' in definition:
            for interrupt in definition['interrupts']:
                for integration in self.game.integrations.all():
                    if integration.is_interrupt(interrupt['pattern'], payload):
                        session.set_variable('hive_interrupted_location', session.current_node())

                        payload = {
                            'variable': 'hive_interrupted_location',
                            'value': session.current_node(),
                            'original_value': session.current_node(),
                            'scope': 'session',
                            'session': 'session-' + str(session.pk),
                            'game': str(session.game_version.game.slug),
                            'player': str(session.player.identifier),
                        }

                        point = DataPoint.objects.create_data_point('hive-set-variable', session.player.identifier, payload, user_agent='Hive Mechanic')
                        point.secondary_identifier = payload['variable']
                        point.save()

                        session.advance_to(interrupt['action'])

                        session.nudge()

                        return True
        return False

    def dialog_snapshot(self): # pylint: disable=too-many-branches
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

        if initial_card is None and len(sequences) > 0: # pylint: disable=len-as-condition
            for sequence in sequences:
                items = sequence.get('items', [])

                if len(items) > 0: # pylint: disable=len-as-condition
                    initial_card = items[0]['id']

                    if ('#' in initial_card) is False:
                        initial_card = '%s#%s' % (sequence['id'], initial_card)

                    break

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

    def cytoscape_json(self, indent=0, simplify=False, compute=False):
        if self.cached_cytoscape == 'null':
            self.cached_cytoscape = None

        if compute is False or self.cached_cytoscape is not None:
            return self.cached_cytoscape

        try:
            cytoscape_json = fetch_cytoscape(json.loads(self.definition), simplify=simplify)

            if cytoscape_json is None:
                self.cached_cytoscape = '{}'
            elif indent > 0:
                self.cached_cytoscape = json.dumps(cytoscape_json, indent=indent)
            else:
                self.cached_cytoscape = json.dumps(cytoscape_json)

            if self.cached_cytoscape == 'null':
                self.cached_cytoscape = None

            self.save()

            return self.cached_cytoscape
        except: # nosec # pylint: disable=bare-except
            traceback.print_exc()

        return None

    def initialize_variables(self, session):
        definition = json.loads(self.definition)

        for variable in definition.get('variables', []):
            if variable['scope'] == 'session':
                session.set_variable(variable['name'], variable['value'])
            elif variable['scope'] == 'player':
                session.player.set_variable(variable['name'], variable['value'])
            else:
                self.game.set_variable(variable['name'], variable['value'])

@receiver(pre_save, sender=GameVersion)
def reset_game_version_metadata(sender, instance, *args, **kwargs): # pylint: disable=unused-argument
    if instance.game is not None:
        instance.game.metadata_updated = None
        instance.game.save()

@python_2_unicode_compatible
class Player(models.Model):
    identifier = models.CharField(max_length=4096, unique=True)

    player_state = JSONField(default=dict, blank=True)

    def log_id(self):
        return 'player:%d' % self.pk

    @transaction.atomic
    def set_variable(self, variable, value):
        old_value = self.player_state.get(variable, None)

        self.player_state[variable] = value # pylint: disable=unsupported-assignment-operation
        self.save()

        self.refresh_from_db()

        metadata = {
            'variable_name': variable,
            'old_value': old_value,
            'new_value': value
        }

        log(self.log_id(), 'Set player variable (%s = %s).' % (variable, value), tags=['player', 'variable'], metadata=metadata, player=self, session=None, game_version=None)

    @transaction.atomic
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

    def last_message(self, direction='incoming'):
        from twilio_support.models import IncomingMessage # pylint: disable=import-outside-toplevel

        source_id = self.identifier.split(':')[-1]

        if direction == 'incoming':
            return IncomingMessage.objects.filter(source=source_id).order_by('-receive_date').first()

        return None

class Session(models.Model):
    player = models.ForeignKey(Player, related_name='sessions', on_delete=models.CASCADE)
    game_version = models.ForeignKey(GameVersion, related_name='sessions', on_delete=models.CASCADE)

    started = models.DateTimeField()
    completed = models.DateTimeField(null=True, blank=True)

    session_state = JSONField(default=dict, blank=True)

    def log_id(self):
        return 'session:%d' % self.pk

    def complete_identifier(self, incomplete_id):
        return self.game_version.complete_identifier(incomplete_id, self.dialog())

    def process_incoming(self, integration, payload, extras=None):
        # ??? Log event here?

        if extras is None:
            extras = {}

        extras['__integration'] = integration

        actions = self.game_version.process_incoming(self, payload, extras)

        if integration is not None:
            integration.execute_actions(self, actions)
        else:
            for game_integration in self.game_version.game.integrations.all():
                game_integration.execute_actions(self, actions)

    def nudge(self):
        self.process_incoming(None, None)

    @transaction.atomic
    def set_variable(self, variable, value):
        old_value = self.session_state.get(variable, None)

        self.session_state[variable] = value # pylint: disable=unsupported-assignment-operation
        self.save()

        self.refresh_from_db()

        metadata = {
            'variable_name': variable,
            'old_value': old_value,
            'new_value': value
        }

        log(self.log_id(), 'Set session variable (%s = %s).' % (variable, value), tags=['session', 'variable'], metadata=metadata, player=self.player, session=self, game_version=self.game_version)

    @transaction.atomic
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

        if 'dialog_key' in self.session_state: # pylint: disable=unsupported-membership-test
            dialog_key = self.session_state['dialog_key'] # pylint: disable=unsubscriptable-object

        dialog = Dialog.objects.filter(key=dialog_key, finished=None).order_by('-started').first()

        if dialog is None:
            dialog = Dialog(key=dialog_key, started=timezone.now())
            dialog.dialog_snapshot = self.game_version.dialog_snapshot()
            dialog.save()

            self.game_version.initialize_variables(self)

        return dialog

    def current_node(self):
        return self.dialog().current_state_id()

    @transaction.atomic
    def complete(self, dialog=None):
        dialog_key = 'session-' + str(self.pk)

        last_dialog = None

        if dialog is not None:
            dialog.finish()

            last_dialog = dialog
        else:
            for session_dialog in Dialog.objects.filter(key=dialog_key, finished=None):
                session_dialog.finish()

                last_dialog = session_dialog

        self.completed = timezone.now()
        self.save()

        metadata = {}

        if last_dialog is not None:
            metadata['dialog'] = 'dialog:%d' % last_dialog.pk
        elif dialog is not None:
            metadata['dialog'] = 'dialog:%d' % dialog.pk

        log(self.log_id(), 'Completed dialog.', tags=['session', 'dialog'], metadata=metadata, player=self.player, session=self, game_version=self.game_version)

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

        for game_integration in self.game_version.game.integrations.all():
            game_integration.execute_actions(self, actions)

    def fetch_session_context(self):
        return self.session_state.copy()

    def fetch_player_context(self):
        return self.player.player_state.copy()

    def terms_key(self):
        return '__accepted_terms__%d' % self.game_version.game.pk

    def fetch_game_context(self):
        return self.game_version.game.game_state.copy()

    def accept_terms(self):
        key = self.terms_key()

        self.player.set_variable(key, timezone.now().isoformat())

    def accepted_terms(self):
        key = self.terms_key()

        accepted = self.player.fetch_variable(key)

        if accepted is not None:
            return True

        game_def = json.loads(self.game_version.definition)

        if game_def.get('terms_interrupt', None) in [None, '']:
            return True

        return False

    def visited_terms(self):
        key = '%s__visited' % self.terms_key()

        visited = self.fetch_variable(key)

        if visited is not None:
            return True

        return False

    def advance_to_terms(self, payload=None):
        game_def = json.loads(self.game_version.definition)

        terms_interrupt = game_def.get('terms_interrupt', None)

        if terms_interrupt is None or terms_interrupt == '':
            visit_key = '%s__visited' % 'no-terms-available'

            self.set_variable(visit_key, timezone.now().isoformat())

            return

        visit_key = '%s__visited' % self.terms_key()

        self.set_variable(visit_key, timezone.now().isoformat())

        if payload is not None:
            payload_str = json.dumps(payload)

            terms_payload_key = '%s__payload_key' % self.terms_key()

            self.set_variable(terms_payload_key, payload_str)

        self.advance_to(terms_interrupt)

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

                implementation_content = requests.get(latest_version['implementation'], timeout=120).content

                computed_hash = hashlib.sha512()

                computed_hash.update(implementation_content)

                local_hash = computed_hash.hexdigest()

                if local_hash == latest_version['sha512-hash']:
                    self.processor_function = implementation_content.decode('utf-8')

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

                    repo_implementation = requests.get(latest_version['implementation'], timeout=120).text

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

class SiteSettings(models.Model):
    name = models.CharField(max_length=1024)
    message_of_the_day = models.TextField(max_length=(1024 * 1024), default='Welcome to Hive Mechanic. You may customize this message in the site settings.')
    banner = models.ImageField(upload_to='site_banners', null=True, blank=True)
    created = models.DateTimeField()
    last_updated = models.DateTimeField()

    total_message_limit = models.IntegerField(null=True, blank=True, help_text='Total of incoming and outgoing messages, plus voice calls')
    count_messages_since = models.DateTimeField(null=True, blank=True)
