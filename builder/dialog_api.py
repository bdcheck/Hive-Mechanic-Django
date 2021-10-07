# pylint: disable=line-too-long, no-member

from __future__ import print_function

import json
import os
import traceback

from django.utils import timezone
from django.utils.text import slugify

from django_dialog_engine.models import Dialog

from integrations.models import Integration

from .models import Game, GameVersion, Player, Session


def create_dialog_from_path(file_path, dialog_key=None):
    try:
        definition = json.load(open(file_path))

        if isinstance(definition, dict) and 'sequences' in definition:
            base_name = os.path.basename(os.path.normpath(file_path))

            game_slug = slugify(base_name)

            if dialog_key is not None:
                game_slug = dialog_key

            game = Game.objects.filter(slug=game_slug).first()

            if game is None:
                game = Game.objects.create(slug=game_slug, name=base_name + ' Botium Test Game')

            test_dialog = Dialog.objects.filter(key=game_slug, finished=None).order_by('-started').first()

            if test_dialog is None:
                version = GameVersion.objects.filter(game=game).order_by('-created').first()

                if version is None:
                    version = GameVersion.objects.create(game=game, created=timezone.now(), definition=json.dumps(definition, indent=2))

                dialog_snapshot = version.dialog_snapshot()

                test_dialog = Dialog.objects.create(key=game_slug, dialog_snapshot=dialog_snapshot, started=timezone.now())

            return test_dialog
    except: # pylint: disable=bare-except
        traceback.print_exc()

    return None

def process(dialog, response, extras):
    game = Game.objects.filter(slug=dialog.key).first()

    integration = Integration.objects.filter(game=game).first()

    if integration is None:
        integration = Integration.objects.create(url_slug=dialog.key, name=dialog.key + ' Botium Integration', type='other', game=game)

    player_match = Player.objects.filter(identifier=extras['player']).first()

    if player_match is None:
        player_match = Player.objects.create(identifier=extras['player'], player_state=extras)

    session = game.current_active_session(player=player_match)

    if session is None:
        session = Session(game_version=game.versions.order_by('-created').first(), player=player_match, started=timezone.now())
        session.session_state['is_testing'] = True # pylint: disable=unsupported-assignment-operation
        session.session_state['dialog_key'] = dialog.key # pylint: disable=unsupported-assignment-operation
        session.save()

        if extras is not None and 'last_message' in extras:
            del extras['last_message']

    return session.process_incoming(integration, response, extras)
