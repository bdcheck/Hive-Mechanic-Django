# pylint: disable=line-too-long, no-member
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

from twilio_support.models import process_incoming as twilio_incoming

from builder.models import Game, Player, Session

INTEGRATION_TYPES = (
    ('twilio', 'Twilio'),
    ('other', 'Other'),
)

class Integration(models.Model):
    name = models.CharField(max_length=1024, unique=True)
    url_slug = models.SlugField(max_length=1024, unique=True)
    type = models.CharField(max_length=1024, choices=INTEGRATION_TYPES, default='twilio')

    game = models.ForeignKey(Game, related_name='integrations')

    create_new_players = models.BooleanField(default=True)

    configuration = JSONField(default=dict)

    def process_incoming(self, payload):
        if self.type == 'twilio':
            twilio_incoming(payload) # pylint: disable=no-value-for-parameter
        else:
            raise Exception('No "' + self.type + '" method implemented to process payload: ' + json.dumps(payload, indent=2))

    def process_player_incoming(self, player_lookup_key, player_lookup_value, payload):
        player_match = None

        for player in Player.objects.all():
            if player_lookup_key in player.player_state:
                if player.player_state[player_lookup_key] == player_lookup_value:
                    player_match = player

        if player_match is None and self.create_new_players:
            player_match = Player(identifier=(player_lookup_key + ':' + player_lookup_key))
            player_match.player_state[player_lookup_key] = player_lookup_value # pylint: disable=unsupported-assignment-operation

            player_match.save()

        if player_match is not None:
            session = self.game.sessions.filter(player=player_match, completed=None).first()

            if session is None:
                session = Session(game_version=self.game.versions.order_by('-created').first(), player=player_match, started=timezone.now())
                session.save()

            session.process_incoming(self, payload)

    def execute_actions(self, session, actions): # pylint: disable=no-self-use, unused-argument
        print 'TODO: Process actions: ' + json.dumps(actions, indent=2)
