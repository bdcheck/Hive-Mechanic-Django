# pylint: disable=line-too-long, no-member

from __future__ import print_function

import bz2
import datetime
import gc
import io
import os
import sys
import tempfile

from django.conf import settings
from django.core import management
from django.utils.text import slugify

from .models import InteractionCard, Game, SiteSettings

def incremental_backup(parameters): # pylint: disable=too-many-branches, too-many-statements
    to_transmit = []

    # Dump full content of these models. No incremental backup here.

    dumpdata_apps = (
        'builder.RemoteRepository',
        'builder.InteractionCardCategory',
        'builder.InteractionCard',
        'builder.Game',
        'builder.GameVersion',
        'builder.Player',
        'builder.Session',
        'builder.DataProcessor',
        'builder.SiteSettings',
    )

    prefix = 'builder_backup_' + settings.ALLOWED_HOSTS[0]

    if 'start_date' in parameters:
        prefix += '_' + parameters['start_date'].date().isoformat()

    if 'end_date' in parameters:
        prefix += '_' + (parameters['end_date'].date() - datetime.timedelta(days=1)).isoformat()

    backup_staging = tempfile.gettempdir()

    try:
        backup_staging = settings.SIMPLE_BACKUP_STAGING_DESTINATION
    except AttributeError:
        pass

    for app in dumpdata_apps:
        print('[builder] Backing up ' + app + '...')
        sys.stdout.flush()

        buf = io.StringIO()
        management.call_command('dumpdata', app, stdout=buf)
        buf.seek(0)

        database_dump = buf.read()

        buf = None

        gc.collect()

        compressed_str = bz2.compress(database_dump.encode('utf-8'))

        database_dump = None

        gc.collect()

        filename = prefix + '_' + slugify(app) + '.json-dumpdata.bz2'

        path = os.path.join(backup_staging, filename)

        with io.open(path, 'wb') as fixture_file:
            fixture_file.write(compressed_str)

        to_transmit.append(path)

    for card in InteractionCard.objects.all():
        try:
            if card.client_implementation is not None:
                path = os.path.join(backup_staging, 'interaction_card_%s_%s' % (card.identifier, os.path.basename(card.client_implementation.name)))

                with io.open(path, 'wb') as fixture_file:
                    fixture_file.write(card.client_implementation.open('rb').read())

                to_transmit.append(path)
        except ValueError:
            pass

    for game in Game.objects.all():
        try:
            if game.icon is not None:
                path = os.path.join(backup_staging, 'game_icon_%s_%s' % (game.slug, os.path.basename(game.icon.name)))

                with io.open(path, 'wb') as fixture_file:
                    fixture_file.write(game.icon.open('rb').read())

                to_transmit.append(path)
        except ValueError:
            pass

    for site_settings in SiteSettings.objects.all():
        try:
            if site_settings.banner is not None:
                path = os.path.join(backup_staging, 'site_settings_banner_%d_%s' % (site_settings.pk, os.path.basename(site_settings.banner.name)))

                with io.open(path, 'wb') as fixture_file:
                    fixture_file.write(site_settings.banner.open('rb').read())

                to_transmit.append(path)
        except ValueError:
            pass

    return to_transmit
