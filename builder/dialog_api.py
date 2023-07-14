# pylint: disable=line-too-long, no-member

from __future__ import print_function

import json
import io
import mimetypes
import os
import tempfile
import traceback

import requests

from filer.models import filemodels
from six.moves.urllib.parse import urlparse

from django.core.files import File
from django.utils import timezone
from django.utils.text import slugify

from django_dialog_engine.models import Dialog

from integrations.models import Integration

from .models import Game, GameVersion, Player, Session

def cache_url(original_url):
    description = 'Retrieved originally from %s.' % original_url

    cache_file = filemodels.File.objects.filter(description=description).first()

    if cache_file is None:
        response = requests.get(original_url)

        if response.status_code >= 200 and response.status_code < 300:
            content_type = response.headers.get('content-type')

            content_type = content_type.split(';')[0]

            extension = mimetypes.guess_extension(content_type)

            if extension is None:
                extension = content_type.split('/')[-1]

            if extension.startswith('.') is False:
                extension = '.%s' % extension

            parsed_url = urlparse(original_url)

            filename = parsed_url.path.split('/')[-1]

            if len(filename) == 0:
                filename = parsed_url.netloc

            if filename.endswith(extension) is False:
                filename = '%s%s' % (filename, extension)

            tokens = filename.split('.', 1)

            with tempfile.NamedTemporaryFile(delete=False, prefix=tokens[0], suffix=('%s' % tokens[1])) as temp_file:
                temp_file.write(response.content)

            cache_file = filemodels.File.objects.create(description=description, mime_type=content_type)
            cache_file.original_filename = filename
            cache_file.save()

            cache_file.file.save(filename, File(open(temp_file.name, 'rb')))
        else:
            return None

    return cache_file.url


def update_custom_node_environment(custom_env):
    custom_env['cache_url'] = cache_url

def create_dialog_from_path(file_path, dialog_key=None):
    try:
        with io.open(file_path, encoding='utf-8') as definition_file:
            definition = json.load(definition_file)

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
