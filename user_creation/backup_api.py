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

from .models import TermsVersion

def incremental_backup(parameters):
    to_transmit = []

    # Dump full content of these models. No incremental backup here.

    dumpdata_apps = (
        'user_creation.TermsAcceptance',
        'user_creation.TermsVersion',
    )

    prefix = 'user_creation_backup_' + settings.ALLOWED_HOSTS[0]

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
        print('[user_creation] Backing up ' + app + '...')
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

    for version in TermsVersion.objects.all():
        try:
            if version.terms_html is not None:
                path = os.path.join(backup_staging, 'terms_version_html_%d_%s' % (version.pk, os.path.basename(version.terms_html.name)))

                with io.open(path, 'wb') as fixture_file:
                    fixture_file.write(version.terms_html.open('rb').read())

                to_transmit.append(path)
        except ValueError:
            pass
        except TypeError:
            pass

    return to_transmit
