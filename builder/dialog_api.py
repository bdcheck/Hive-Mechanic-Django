# pylint: disable=line-too-long, no-member

import json
import os
import traceback

from django.utils import timezone
from django.utils.text import slugify

from django_dialog_engine.models import Dialog

from .models import Game, GameVersion


def create_dialog_from_path(file_path):
    try:
        definition = json.load(open(file_path))

        if isinstance(definition, dict) and 'sequences' in definition:
            base_name = os.path.basename(os.path.normpath(file_path))

            game_slug = slugify(base_name)

            game = Game.objects.filter(slug=game_slug).first()

            if game is None:
                game = Game.objects.create(slug=game_slug, name=base_name + ' Botium Test Game')


            new_version = GameVersion.objects.create(game=game, created=timezone.now(), definition=json.dumps(definition, indent=2))

            dialog_snapshot = new_version.dialog_snapshot()

            new_dialog = Dialog.objects.create(key=game_slug, dialog_snapshot=dialog_snapshot, started=timezone.now())

            return new_dialog
    except: # pylint: disable=bare-except
        traceback.print_exc()

    return None
