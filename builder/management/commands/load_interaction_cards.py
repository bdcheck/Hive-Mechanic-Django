# pylint: disable=no-member, line-too-long

import json
import zipfile

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from ...models import InteractionCard

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('cards_file', nargs=1, type=str)

        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing cards with identical identifiers',
        )

    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument
        for cards_file in cmd_options['cards_file']:
            with zipfile.ZipFile(cards_file, 'r') as import_files:
                manifest_json = import_files.read('manifest.json')

                manifest = json.loads(manifest_json)

                for key, value in manifest.iteritems():
                    identifier = key

                    card = InteractionCard.objects.filter(identifier=identifier).first()

                    if (card is None) or ('update_existing' in cmd_options and cmd_options['update_existing']):
                        if card is None:
                            print 'Creating card for "' + identifier + '"...'

                            card = InteractionCard(identifier)
                        else:
                            print 'Updating card for "' + identifier + '"...'

                        card.name = value['name']

                        card.entry_actions = import_files.read(identifier + '_entry_actions.py')
                        card.evaluate_function = import_files.read(identifier + '_evaluate_function.py')

                        card.save()

                        card.client_implementation.save(identifier + '.js', ContentFile(import_files.read(identifier + '.js')))
                        card.save()
                    else:
                        print 'Skipping update for "' + identifier + '"...'
