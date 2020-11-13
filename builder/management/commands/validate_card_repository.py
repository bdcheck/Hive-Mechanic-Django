# pylint: disable=no-member, line-too-long

import hashlib
import json

import arrow
import requests

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('repository_url', type=str)

    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument
        response = requests.get(cmd_options['repository_url'])

        repository = response.json()

        for key in repository.keys():
            card_def = repository[key]

            versions = card_def['versions']

            for version in versions:
                entry_content = requests.get(version['entry-actions']).content
                evaluate_content = requests.get(version['evaluate-function']).content
                client_content = requests.get(version['client-implementation']).content

                computed_hash = hashlib.sha512()

                computed_hash.update(entry_content)
                computed_hash.update(evaluate_content)
                computed_hash.update(client_content)

                local_hash = computed_hash.hexdigest()

                if local_hash != version['sha512-hash']:
                    print('[' + key + ' / ' + str(version['version']) + '] Computed local hash \'' + local_hash + '\'. Found \'' + version['sha512-hash'] + '\' instead.')

                try:
                    arrow.get(version['created'])
                except:
                    print('[' + key + ' / ' + str(version['version']) + '] Unable to parse created date: ' + str(version['created']))
