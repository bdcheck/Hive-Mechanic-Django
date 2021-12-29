# pylint: disable=line-too-long, no-member

from __future__ import division

from builtins import str # pylint: disable=redefined-builtin

import calendar
import csv
import io
import os
import tempfile

from past.utils import old_div

import arrow
import pytz

from django.conf import settings

from passive_data_kit.models import DataPoint, DataSourceReference, DataGeneratorDefinition

def generator_name(identifier): # pylint: disable=unused-argument
    return 'Hive Mechanic: Set Variable'

def compile_report(generator, sources, data_start=None, data_end=None, date_type='created'): # pylint: disable=too-many-locals
    now = arrow.get()

    filename = tempfile.gettempdir() + os.path.sep + 'hive_set_variable_' + str(now.timestamp()) + str(old_div(now.microsecond, 1e6)) + '.txt'

    with io.open(filename, 'w', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter='\t')

        columns = [
            'Player',
            'Created Timestamp',
            'Created Date',
            'Game',
            'Session',
            'Variable Name',
            'Value',
        ]

        writer.writerow(columns)

        for source in sources:
            source_reference = DataSourceReference.reference_for_source(source)
            generator_definition = DataGeneratorDefinition.definition_for_identifier(generator)

            points = DataPoint.objects.filter(source_reference=source_reference, generator_definition=generator_definition)

            if data_start is not None:
                if date_type == 'recorded':
                    points = points.filter(recorded__gte=data_start)
                else:
                    points = points.filter(created__gte=data_start)

            if data_end is not None:
                if date_type == 'recorded':
                    points = points.filter(recorded__lte=data_end)
                else:
                    points = points.filter(created__lte=data_end)

            points = points.order_by('source', 'created')

            for point in points:
                properties = point.fetch_properties()

                row = []

                created = point.created.astimezone(pytz.timezone(settings.TIME_ZONE))

                row.append(properties['player'])
                row.append(calendar.timegm(point.created.utctimetuple()))
                row.append(created.isoformat())
                row.append(properties['game'])
                row.append(properties['session'])
                row.append(properties['variable'])
                row.append(properties['value'])

                writer.writerow(row)

    return filename

def extract_secondary_identifier(properties):
    if 'state' in properties:
        return properties['state']

    return None
