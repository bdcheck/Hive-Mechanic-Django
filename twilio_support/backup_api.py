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

from .models import IncomingMessageMedia

def incremental_backup(parameters):
    to_transmit = []

    # Dump full content of these models. No incremental backup here.

    dumpdata_apps = (
        'twilio_support.OutgoingMessage',
        'twilio_support.IncomingMessage',
        'twilio_support.IncomingMessageMedia',
        'twilio_support.OutgoingCall',
        'twilio_support.IncomingCallResponse',
    )

    prefix = 'twilio_support_backup_' + settings.ALLOWED_HOSTS[0]

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
        print('[twilio_support] Backing up ' + app + '...')
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

    for media in IncomingMessageMedia.objects.all():
        try:
            if media.content_file is not None:
                path = os.path.join(backup_staging, 'incoming_message_media_%d_%s' % (media.pk, os.path.basename(media.content_file.name)))

                with io.open(path, 'wb') as fixture_file:
                    fixture_file.write(media.content_file.open('rb').read())

                to_transmit.append(path)
        except ValueError:
            pass
        except TypeError:
            pass

    return to_transmit
