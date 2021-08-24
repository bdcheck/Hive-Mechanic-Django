from __future__ import print_function

import bz2
import gc
import io
import os
import sys
import tempfile

from django.conf import settings
from django.core import management
from django.utils.text import slugify

def load_backup(filename, content):
    prefix = 'hive_twilio_support_backup_' + settings.ALLOWED_HOSTS[0]

    if filename.startswith(prefix) is False:
        return

    if 'json-dumpdata' in filename:
        filename = filename.replace('.json-dumpdata.bz2.encrypted', '.json')

        path = os.path.join(tempfile.gettempdir(), filename)

        with open(path, 'wb') as fixture_file:
            fixture_file.write(content)

        management.call_command('loaddata', path)

        os.remove(path)
    else:
        print('[hive_twilio_support.pdk_api.load_backup] Unknown file type: ' + filename)

def incremental_backup(parameters): # pylint: disable=too-many-locals, too-many-statements
    to_transmit = []
    to_clear = []

    # Dump full content of these models. No incremental backup here.

    dumpdata_apps = (
        'twilio_support.IncomingCallResponse',
        'twilio_support.IncomingMessageMedia',
        'twilio_support.IncomingMessage',
        'twilio_support.OutgoingCall',
        'twilio_support.OutgoingMessage',
    )

    if parameters['skip_apps']:
        dumpdata_apps = ()

    prefix = 'hive_twilio_support_backup_' + settings.ALLOWED_HOSTS[0]

    if 'start_date' in parameters:
        prefix += '_' + parameters['start_date'].isoformat()

    if 'end_date' in parameters:
        prefix += '_' + parameters['end_date'].isoformat()

    backup_staging = tempfile.gettempdir()

    try:
        backup_staging = settings.PDK_BACKUP_STAGING_DESTINATION
    except AttributeError:
        pass

    for app in dumpdata_apps:
        print('[hive_twilio_support] Backing up ' + app + '...')
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

        with open(path, 'wb') as fixture_file:
            fixture_file.write(compressed_str)

        to_transmit.append(path)

    return to_transmit, to_clear

def clear_points(to_clear): # pylint: disable=unused-argument
    pass # No data points to clear
