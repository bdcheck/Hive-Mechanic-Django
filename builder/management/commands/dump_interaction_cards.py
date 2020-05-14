# pylint: disable=no-member, line-too-long

import json
import zipfile

import zipstream

from django.core.management.base import BaseCommand

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
                        card_entry['prefix'] = card.identifier + '_'

                        manifest[card.identifier] = card_entry

                        export_stream.writestr(card.identifier + '_entry_actions.py', card.entry_actions)
                        export_stream.writestr(card.identifier + '_evaluate_function.py', card.evaluate_function)

                        if card.client_implementation is not None:
                            export_stream.write(card.client_implementation.path, card.identifier + '.js')

                    export_stream.writestr('manifest.json', json.dumps(manifest, indent=2))

                    for data in export_stream:
                        final_output_file.write(data)
