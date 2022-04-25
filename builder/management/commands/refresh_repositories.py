# pylint: disable=no-member, line-too-long

from __future__ import print_function

import json

import requests

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import RemoteRepository, InteractionCard, InteractionCardCategory, DataProcessor

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--silent', default=False, action='store_true')

    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument, too-many-locals, too-many-statements, too-many-branches
        for repository in RemoteRepository.objects.order_by('priority'): # pylint: disable=too-many-nested-blocks
            headers = {
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }

            response = requests.get(repository.url, headers=headers)

            repository_content = response.content

            if repository_content != repository.repository_definition:
                repository.repository_definition = repository_content

                repository.last_updated = timezone.now()
                repository.save()

                repository_def = json.loads(repository_content)

                for key in repository_def['cards'].keys():
                    card_def = repository_def['cards'][key]

                    card_json = json.dumps(card_def, indent=2)

                    versions = sorted(card_def['versions'], key=lambda version: version['version'])

                    last_version = versions[-1]

                    matched_card = InteractionCard.objects.filter(identifier=card_def['identifier']).first()

                    if matched_card is None:
                        if cmd_options['silent'] is False:
                            print('Adding new card: ' + card_def['name'] + '...')
                        matched_card = InteractionCard(identifier=card_def['identifier'], name=card_def['name'], enabled=False)

                        matched_card.entry_actions = requests.get(last_version['entry-actions']).content.decode("utf-8")
                        matched_card.evaluate_function = requests.get(last_version['evaluate-function']).content.decode("utf-8")
                        matched_card.version = last_version['version']
                        matched_card.repository_definition = card_json

                        metadata = {}

                        metadata['updated'] = timezone.now().isoformat()

                        matched_card.metadata = json.dumps(metadata, indent=2)

                        matched_card.save()

                        client_content = requests.get(last_version['client-implementation']).content

                        matched_card.client_implementation.save(card_def['identifier'] + '.js', ContentFile(client_content))

                        matched_card.save()
                    elif last_version['version'] != matched_card.version or matched_card.repository_definition != card_json:
                        if cmd_options['silent'] is False:
                            print('Update available for existing card: ' + card_def['name'] + '...')

                        matched_card.repository_definition = card_json

                        metadata = {}

                        if matched_card.metadata is not None:
                            metadata = json.loads(matched_card.metadata)

                        metadata['updated'] = timezone.now().isoformat()
                        matched_card.metadata = json.dumps(metadata, indent=2)

                        matched_card.save()

                    if matched_card.category is None:
                        category_name = card_def.get('category', None)

                        if category_name is not None:
                            category = InteractionCardCategory.objects.filter(name=category_name).first()

                            if category is None:
                                category = InteractionCardCategory.objects.create(name=category_name)

                            matched_card.category = category
                            matched_card.save()

                for key in repository_def['data_processors'].keys():
                    processor_def = repository_def['data_processors'][key]

                    processor_json = json.dumps(processor_def, indent=2)

                    versions = sorted(processor_def['versions'], key=lambda version: version['version'])

                    last_version = versions[-1]

                    matched_processor = DataProcessor.objects.filter(identifier=processor_def['identifier']).first()

                    if matched_processor is None:
                        if cmd_options['silent'] is False:
                            print('Adding new data processor: ' + processor_def['name'] + '...')
                        matched_processor = DataProcessor(identifier=processor_def['identifier'], name=processor_def['name'], enabled=False)

                        matched_processor.processor_function = requests.get(last_version['implementation']).content.decode("utf-8")
                        matched_processor.version = last_version['version']
                        matched_processor.repository_definition = processor_json

                        metadata = {}

                        metadata['updated'] = timezone.now().isoformat()

                        matched_processor.metadata = json.dumps(metadata, indent=2)

                        matched_processor.save()
                    elif last_version['version'] != matched_processor.version or matched_processor.repository_definition != processor_json:
                        if cmd_options['silent'] is False:
                            print('Update available for existing data processor: ' + processor_def['name'] + '...')

                        matched_processor.repository_definition = processor_json

                        metadata = json.loads(matched_processor.metadata)
                        metadata['updated'] = timezone.now().isoformat()
                        matched_processor.metadata = json.dumps(metadata, indent=2)


                        matched_processor.save()
