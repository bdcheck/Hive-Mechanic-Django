# pylint: disable=no-member, line-too-long

import hashlib
import json

import requests

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import RemoteRepository, InteractionCard

class Command(BaseCommand):
    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument
        for repository in RemoteRepository.objects.order_by('priority'):
            response = requests.get(repository.url)

            repository_content = response.content

            if repository_content != repository.repository_definition:
                repository.repository_definition = repository_content

                repository.last_updated = timezone.now()
                repository.save()

                repository_def = json.loads(repository_content)

                for key in repository_def.keys():
                    card_def = repository_def[key]
                    
                    card_json = json.dumps(card_def, indent=2)

                    versions = sorted(card_def['versions'], key=lambda version: version['version'])

                    last_version = versions[-1]

                    matched_card = InteractionCard.objects.filter(identifier=card_def['identifier']).first()

                    if matched_card is None:
                        print('Adding new card: ' + card_def['name'] + '...')
                        matched_card = InteractionCard(identifier=card_def['identifier'], name=card_def['name'], enabled=False)

                        matched_card.entry_actions = requests.get(last_version['entry-actions']).content
                        matched_card.evaluate_function = requests.get(last_version['evaluate-function']).content
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
                        print('Update available for existing card: ' + card_def['name'] + '...')

                        matched_card.repository_definition = card_json

                        matched_card.save()
