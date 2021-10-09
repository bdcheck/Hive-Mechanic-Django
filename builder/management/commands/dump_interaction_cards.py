# pylint: disable=no-member, line-too-long

import hashlib
import io
import json
import zipfile

import zipstream

from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import InteractionCard

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('export_filename', nargs=1, type=str)

    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument
        for export_filename in cmd_options['export_filename']:
            with open(export_filename, 'wb') as final_output_file:
                with zipstream.ZipFile(mode='w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as export_stream: # pylint: disable=line-too-long
                    manifest = {}

                    for card in InteractionCard.objects.all():
                        card_entry = {}

                        card_entry['identifier'] = card.identifier
                        card_entry['name'] = card.name

                        card_entry['versions'] = []

                        version = {
                            'version': card.version,
                            'name': str(card.version),
                            'created': timezone.now().isoformat(),
                            'notes': '(Insert release notes here.)',
                            'entry-actions': 'URL',
                            'evaluate-function': 'URL',
                            'client-implementation': 'URL'
                        }

                        computed_hash = hashlib.sha512()

                        computed_hash.update(card.entry_actions.encode('utf-8'))
                        computed_hash.update(card.evaluate_function.encode('utf-8'))

                        with io.open(card.client_implementation.path, encoding='utf-8') as client_file:
                            computed_hash.update(client_file.read().encode('utf-8'))

                            version['sha512-hash'] = computed_hash.hexdigest()

                            card_entry['versions'].append(version)

                            file_identifier = card.identifier.replace('-', '_')

                            export_stream.writestr(file_identifier + '/__init__.py', bytes('', 'utf-8'))
                            export_stream.writestr(file_identifier + '/entry.py', bytes(card.entry_actions, 'utf-8'))
                            export_stream.writestr(file_identifier + '/evaluate.py', bytes(card.evaluate_function, 'utf-8'))

                            if card.client_implementation is not None:
                                export_stream.write(card.client_implementation.path, file_identifier + '/client.js')

                            manifest[card.identifier] = card_entry

                    export_stream.writestr('manifest.json', bytes(json.dumps(manifest, indent=2), 'utf-8'))

                    for data in export_stream:
                        final_output_file.write(data)
