# pylint: disable=line-too-long, no-member
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

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

    game = models.ForeignKey(Game, related_name='integrations')

    create_new_players = models.BooleanField(default=True)

    configuration = JSONField(default=dict)

    def __unicode__(self):
        return self.name

    def process_incoming(self, payload):
        if self.type == 'twilio':
            from twilio_support.models import process_incoming as twilio_incoming

            twilio_incoming(self, payload) # pylint: disable=no-value-for-parameter
        elif self.type == 'http':
            from http_support.models import process_incoming as http_incoming

            http_incoming(self, payload) # pylint: disable=no-value-for-parameter
        else:
            raise Exception('No "' + self.type + '" method implemented to process payload: ' + json.dumps(payload, indent=2))

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

                session.process_incoming(self, payload, extras)

            session.process_incoming(self, payload, extras)

    def execute_actions(self, session, actions): # pylint: disable=no-self-use, unused-argument
        if actions is not None:
            for action in actions:
                processed = False

                if self.type == 'twilio':
                    from twilio_support.models import execute_action as twilio_execute

                    processed = twilio_execute(self, session, action)

                if processed is False:
                    processed = execute_action(self, session, action)

                if processed is False:
                    print 'TODO: Process ' + str(action)

def execute_action(integration, session, action): # pylint: disable=unused-argument
    if action['type'] == 'set-cookie':
        scope = 'session'

        if 'scope' in action:
            scope = action['scope']

            if scope == 'session':
                session.set_cookie(action['cookie'], action['value'])
            elif scope == 'player':
                session.player.set_cookie(action['cookie'], action['value'])
            elif scope == 'game':
                session.game_version.game.set_cookie(action['cookie'], action['value'])

        return True
    elif action['type'] == 'continue':
        return True
    elif action['type'] == 'end-activity':
        session.completed = timezone.now()
        session.save()

        return True

    return False
