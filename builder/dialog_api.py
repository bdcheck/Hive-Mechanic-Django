# pylint: disable=line-too-long, no-member

import json
import io
import mimetypes
import os
import tempfile
import traceback

import requests
import six

from filer.models import filemodels
from six.moves import urllib

from django.conf import settings

from django.core.files import File
from django.utils import timezone
from django.utils.text import slugify

from django_dialog_engine.models import Dialog

from integrations.models import Integration

from .models import Game, GameVersion, Player, Session, CachedFile

def cache_url(original_url, description=None):
    description_str = 'Retrieved originally from %s.' % original_url

    if description is not None:
        description_str = '%s -- %s' % (description, description_str)

    cache_file = filemodels.File.objects.filter(description=description_str).first()

    if cache_file is None:
        response = requests.get(original_url, timeout=60)

        if response.status_code >= 200 and response.status_code < 300:
            content_type = response.headers.get('content-type')

            content_type = content_type.split(';')[0]

            extension = mimetypes.guess_extension(content_type)

            if extension is None:
                extension = content_type.split('/')[-1]

            if extension.startswith('.') is False:
                extension = '.%s' % extension

            parsed_url = urllib.parse.urlparse(original_url)

            filename = parsed_url.path.split('/')[-1]

            if len(filename) == 0: # pylint: disable=len-as-condition
                filename = parsed_url.netloc

            if filename.endswith(extension) is False:
                filename = '%s%s' % (filename, extension)

            tokens = filename.split('.', 1)

            with tempfile.NamedTemporaryFile(delete=False, prefix=tokens[0], suffix=('%s' % tokens[1])) as temp_file:
                temp_file.write(response.content)

            cache_file = CachedFile.objects.create(description=description_str, mime_type=content_type, original_url=original_url)
            cache_file.original_filename = filename
            cache_file.save()

            with open(temp_file.name, 'rb') as destination:
                cache_file.file.save(filename, File(destination))
        else:
            return None

    return 'https://%s%s' % (settings.ALLOWED_HOSTS[0], cache_file.url)


def update_custom_node_environment(custom_env):
    custom_env['cache_url'] = cache_url

    processor_env = custom_env.get('data_processor_environment', {})

    processor_env['cache_url'] = cache_url

    custom_env['data_processor_environment'] = processor_env


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
        traceback.six.print__exc()

    return None

def process(dialog, response, extras):
    game = Game.objects.filter(slug=dialog.key).first()

    integration = Integration.objects.filter(game=game).first()

    if integration is None:
        integration = Integration.objects.create(url_slug=dialog.key, name=dialog.key + ' Botium Integration', type='command_line', game=game)

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
