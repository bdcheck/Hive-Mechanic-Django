# pylint: disable=no-member, line-too-long
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import re

from builder.models import Player, Session

def process_incoming(integration, payload): # pylint: disable=too-many-branches
    issues = []

    commands = None
    players = None

    if 'commands' in payload:
        commands = json.loads(payload['commands'])
    else:
        issues.append('Missing "commands" parameter in request.')

    if 'players' in payload:
        players = json.loads(payload['players'])
    else:
        issues.append('Missing "players" parameter in request.')

    if commands is not None and players is not None:
        player_pks = []

        for player in players:
            for existing_player in Player.objects.all():
                to_add = False

                if existing_player.identifier == player:
                    to_add = True
                elif re.match(player, existing_player.identifier) is not None:
                    to_add = True

                if to_add and (existing_player.pk in player_pks) is False:
                    player_pks.append(existing_player.pk)

        for player_pk in player_pks:
            player = Player.objects.get(pk=player_pk)

            for game_version in integration.game.versions.order_by('-created'):
                session = Session.objects.filter(player=player, game_version=game_version, completed=None).first()

                if session is not None:
                    integration.execute_actions(session, commands)

    return issues
