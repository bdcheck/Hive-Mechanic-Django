# pylint: disable=line-too-long, no-member
# -*- coding: utf-8 -*-

from builtins import str # pylint: disable=redefined-builtin

import json
import re

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

from builder.models import Game, Player, Session

INTEGRATION_TYPES = (
    ('twilio', 'Twilio'),
    ('http', 'HTTP'),
    ('other', 'Other'),
)

class Integration(models.Model):
    name = models.CharField(max_length=1024, unique=True)
    url_slug = models.SlugField(max_length=1024, unique=True)
    type = models.CharField(max_length=1024, choices=INTEGRATION_TYPES, default='twilio')

    game = models.ForeignKey(Game, related_name='integrations', on_delete=models.CASCADE)

    create_new_players = models.BooleanField(default=True)

    configuration = JSONField(default=dict)

    def __unicode__(self):
        return self.name

    def process_incoming(self, payload):
        if self.type == 'twilio': # pylint: disable=no-else-return
            from twilio_support.models import process_incoming as twilio_incoming # pylint: disable=import-outside-toplevel

            return twilio_incoming(self, payload) # pylint: disable=no-value-for-parameter
        elif self.type == 'http':
            from http_support.models import process_incoming as http_incoming # pylint: disable=import-outside-toplevel

            return http_incoming(self, payload) # pylint: disable=no-value-for-parameter
        else:
            raise Exception('No "' + self.type + '" method implemented to process payload: ' + json.dumps(payload, indent=2))

    def is_interrupt(self, pattern, value): # pylint: disable=no-self-use
        # TODO: Implement support-specific interrupts here... # pylint: disable=fixme

        if pattern == '':
            return False

        if isinstance(pattern, str) and isinstance(value, str):
            if re.match(pattern, value) is not None:
                return True

        return False

    def process_player_incoming(self, player_lookup_key, player_lookup_value, payload, extras=None):
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

                if processed is False:
                    processed = execute_action(self, session, action)

                if processed is False:
                    settings.FETCH_LOGGER().warn('TODO: Process %', action)

    def translate_value(self, value, session, scope='session'):
        translated_value = value

        while '[ME]' in translated_value:
            translated_value = translated_value.replace('[ME]', session.player.identifier)

        while '[SCOPE:' in translated_value:
            start = translated_value.find('[SCOPE:')

            end = translated_value.find(']', start)

            if end != -1:
                tag = translated_value[start:(end + 1)]

                variable = tag[7:-1]

                variable_value = session.fetch_variable(variable)

                if variable_value is None:
                    variable_value = '???'

                translated_value = translated_value.replace(tag, variable_value)

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

        return translated_value

def execute_action(integration, session, action): # pylint: disable=unused-argument
    if action['type'] == 'set-variable': # pylint: disable=no-else-return
        scope = 'session'

        if 'scope' in action:
            scope = action['scope']

            action['translated_value'] = integration.translate_value(action['value'], session, scope)

            if scope == 'session':
                session.set_variable(action['variable'], action['translated_value'])
            elif scope == 'player':
                session.player.set_variable(action['variable'], action['translated_value'])
            elif scope == 'game':
                session.game_version.game.set_variable(action['variable'], action['translated_value'])
        else:
            action['translated_value'] = integration.translate_variable(action['variable'], session)

            session.set_variable(action['variable'], action['translated_value'])

        return True
    elif action['type'] == 'continue':
        return True
    elif action['type'] == 'go-to':
        if 'destination' in action:
            session.advance_to(action['destination'])

            return True
    elif action['type'] == 'trigger-interrupt':
        if 'interrupt' in action:
            return session.game_version.interrupt(action['interrupt'], session)
    elif action['type'] == 'end-activity':
        session.completed = timezone.now()
        session.save()

        return True

    return False
