# pylint: disable=line-too-long, no-member
# -*- coding: utf-8 -*-

from __future__ import print_function

from builtins import str # pylint: disable=redefined-builtin

import json
import re

from future.utils import python_2_unicode_compatible

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from passive_data_kit.models import DataPoint

from builder.models import Game, Player, Session

INTEGRATION_TYPES = (
    ('twilio', 'Twilio'),
    ('http', 'HTTP'),
    ('command_line', 'Command Line'),
    ('other', 'Other'),
)

class PermissionsSupport(models.Model):
    class Meta: # pylint: disable=old-style-class, no-init, too-few-public-methods
        managed = False
        default_permissions = ()

        permissions = (
            ('integration_access_view', 'View integration information'),
            ('integration_access_edit', 'Edit integration information'),
        )

@python_2_unicode_compatible
class Integration(models.Model):
    name = models.CharField(max_length=1024, unique=True)
    url_slug = models.SlugField(max_length=1024, unique=True)
    type = models.CharField(max_length=1024, choices=INTEGRATION_TYPES, default='twilio')

    game = models.ForeignKey(Game, related_name='integrations', on_delete=models.CASCADE)

    create_new_players = models.BooleanField(default=True)

    configuration = JSONField(default=dict, help_text=_('configuration_help_text'), blank=True, null=True)

    editors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='integration_editables', blank=True)
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='integration_viewables', blank=True)

    def __str__(self):
        return self.name + ' (' + self.game.slug + ')'

    def process_incoming(self, payload):
        print('process_incoming: ' + json.dumps(payload, indent=2))
        if self.type == 'twilio': # pylint: disable=no-else-return
            from twilio_support.models import process_incoming as twilio_incoming # pylint: disable=import-outside-toplevel

            return twilio_incoming(self, payload) # pylint: disable=no-value-for-parameter
        elif self.type == 'http':
            from http_support.models import process_incoming as http_incoming # pylint: disable=import-outside-toplevel

            return http_incoming(self, payload) # pylint: disable=no-value-for-parameter
        elif self.type == 'command_line':
            from cli_support.models import process_incoming as cli_incoming # pylint: disable=import-outside-toplevel

            return cli_incoming(self, payload) # pylint: disable=no-value-for-parameter
        else:
            raise Exception('No "' + self.type + '" method implemented to process payload: ' + json.dumps(payload, indent=2))

    def is_interrupt(self, pattern, value): # pylint: disable=no-self-use
        # TODO: Implement support-specific interrupts here... # pylint: disable=fixme

        if pattern == '':
            return False

        if isinstance(pattern, str) and isinstance(value, str):
            if re.match(pattern, value, re.IGNORECASE) is not None:
                return True

        return False

    def process_player_incoming(self, player_lookup_key, player_lookup_value, payload, extras=None):
        print('process_player_incoming: ' + str(payload) + ' -- ' + json.dumps(extras, indent=2))
        player_match = None

        for player in Player.objects.all():
            if player_lookup_key in player.player_state:
                if player.player_state[player_lookup_key] == player_lookup_value:
                    player_match = player

        if player_match is None and self.create_new_players:
            player_match = Player(identifier=(player_lookup_key + ':' + player_lookup_value))
            player_match.player_state[player_lookup_key] = player_lookup_value # pylint: disable=unsupported-assignment-operation

            player_match.save()

        if player_match is not None:
            session = self.game.current_active_session(player=player_match)

            if session is None:
                session = Session(game_version=self.game.versions.order_by('-created').first(), player=player_match, started=timezone.now())
                session.save()

                if extras is not None and 'last_message' in extras:
                    del extras['last_message']

                session.process_incoming(self, None, extras)

            if isinstance(payload, list):
                actions = payload

                payload = None

                self.execute_actions(session, actions)

            session.process_incoming(self, payload, extras)

    def execute_actions(self, session, actions): # pylint: disable=no-self-use, unused-argument
        if actions is not None:
            for action in actions:
                processed = False

                if self.type == 'twilio':
                    from twilio_support.models import execute_action as twilio_execute # pylint: disable=import-outside-toplevel

                    processed = twilio_execute(self, session, action)
                elif self.type == 'http':
                    from http_support.models import execute_action as http_execute # pylint: disable=import-outside-toplevel

                    processed = http_execute(self, session, action)
                elif self.type == 'command_line':
                    from cli_support.models import execute_action as cli_execute # pylint: disable=import-outside-toplevel

                    processed = cli_execute(self, session, action)

                if processed is False:
                    processed = execute_action(self, session, action)

                if processed is False:
                    settings.FETCH_LOGGER().warn('TODO: Process', action)

    def translate_value(self, value, session, scope='session'): # pylint: disable=unused-argument, no-self-use, too-many-branches
        translated_value = value

        try:
            while '[ME]' in translated_value:
                translated_value = translated_value.replace('[ME]', session.player.identifier)

            while '[LAST-MESSAGE]' in translated_value:
                translated_value = translated_value.replace('[LAST-MESSAGE]', session.last_message())

            while '[LAST-MESSAGE-TYPE]' in translated_value:
                translated_value = translated_value.replace('[LAST-MESSAGE-TYPE]', session.last_message_type())

            while '[SESSION:' in translated_value:
                start = translated_value.find('[SESSION:')

                end = translated_value.find(']', start)

                if end != -1:
                    tag = translated_value[start:(end + 1)]

                    variable = tag[9:-1]

                    variable_value = session.fetch_variable(variable)

                    if variable_value is None:
                        variable_value = '???'

                    translated_value = translated_value.replace(tag, str(variable_value))

            while '[GAME:' in translated_value:
                start = translated_value.find('[GAME:')

                end = translated_value.find(']', start)

                if end != -1:
                    tag = translated_value[start:(end + 1)]

                    variable = tag[6:-1]

                    variable_value = session.game_version.game.fetch_variable(variable)

                    if variable_value is None:
                        variable_value = '???'

                    translated_value = translated_value.replace(tag, variable_value)

            while '[PLAYER:' in translated_value:
                start = translated_value.find('[PLAYER:')

                end = translated_value.find(']', start)

                if end != -1:
                    tag = translated_value[start:(end + 1)]

                    variable = tag[8:-1]

                    variable_value = session.player.fetch_variable(variable)

                    if variable_value is None:
                        variable_value = '???'

                    translated_value = translated_value.replace(tag, variable_value)
        except TypeError:
            pass # Attempting to translate non-string

        return translated_value

    def last_message_for_player(self, player):
        if self.type == 'twilio':
            from twilio_support.models import last_message_for_player # pylint: disable=import-outside-toplevel

            return last_message_for_player(self.game, player)

        return None

    def fetch_statistics(self):
        statistics = {
            'name': self.name,
            'type': self.type,
            'game': self.game,
            'details': []
        }

        if self.type == 'twilio':
            from twilio_support.models import annotate_statistics # pylint: disable=import-outside-toplevel

            annotate_statistics(self, statistics)
        elif self.type == 'http':
            from http_support.models import annotate_statistics # pylint: disable=import-outside-toplevel

            annotate_statistics(self, statistics)
        elif self.type == 'command_line':
            from cli_support.models import annotate_statistics # pylint: disable=import-outside-toplevel

            annotate_statistics(self, statistics)

        return statistics


def execute_action(integration, session, action): # pylint: disable=unused-argument, too-many-branches, too-many-return-statements
    if action['type'] == 'set-variable': # pylint: disable=no-else-return
        scope = 'session'

        payload = {
            'variable': action['variable'],
            'original_value': action['value'],
            'scope': 'session',
            'session': 'session-' + str(session.pk),
            'game': str(session.game_version.game.slug),
            'player': str(session.player.identifier),
        }

        if 'scope' in action:
            scope = action['scope']

            payload['scope'] = scope

            action['translated_value'] = integration.translate_value(action['value'], session, scope)

            if scope == 'session':
                session.set_variable(action['variable'], action['translated_value'])
            elif scope == 'player':
                session.player.set_variable(action['variable'], action['translated_value'])
            elif scope == 'game':
                session.game_version.game.set_variable(action['variable'], action['translated_value'])
        else:
            action['translated_value'] = integration.translate_value(action['variable'], session)

            session.set_variable(action['value'], action['translated_value'])

        payload['value'] = action['translated_value']

        point = DataPoint.objects.create_data_point('hive-set-variable', session.player.identifier, payload, user_agent='Hive Mechanic')
        point.secondary_identifier = payload['variable']
        point.save()

        return True
    elif action['type'] == 'continue':
        return True
    elif action['type'] == 'go-to':
        if 'destination' in action:
            if ('#' in action['destination']) is False:
                action['destination'] = session.complete_identifier(action['destination'])

            session.advance_to(action['destination'])

            return True
    elif action['type'] == 'trigger-interrupt':
        if 'interrupt' in action:
            return session.game_version.interrupt(action['interrupt'], session)
    elif action['type'] == 'end-activity':
        session.complete()

        return True
    elif action['type'] == 'echo': # pylint: disable=no-else-return
        print(integration.translate_value(action['message'], session))

        return True
    elif action['type'] == 'echo-image':
        print(action['image-url'])

        return True

    return False
