# pylint: disable=no-member, line-too-long

import hashlib

import six

import arrow
import requests

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('repository_url', type=str)

    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument, too-many-locals
        response = requests.get(cmd_options['repository_url'], timeout=120)

        repository = response.json()

        for key in repository['cards'].keys():
            card_def = repository['cards'][key]

            versions = card_def['versions']

            for version in versions:
                entry_content = requests.get(version['entry-actions'], timeout=120).content
                evaluate_content = requests.get(version['evaluate-function'], timeout=120).content
                client_content = requests.get(version['client-implementation'], timeout=120).content

                computed_hash = hashlib.sha512()

                computed_hash.update(entry_content)
                computed_hash.update(evaluate_content)
                computed_hash.update(client_content)

                local_hash = computed_hash.hexdigest()

                if local_hash != version['sha512-hash']:
                    six.print_('[Card: ' + key + ' / ' + str(version['version']) + '] Computed local hash \'' + local_hash + '\'. Found \'' + version['sha512-hash'] + '\' instead.')

                try:
                    arrow.get(version['created'])
                except: # pylint: disable=bare-except
                    six.print_('[Card: ' + key + ' / ' + str(version['version']) + '] Unable to parse created date: ' + str(version['created']))

        for key in repository['data_processors'].keys():
            processor_def = repository['data_processors'][key]

            versions = processor_def['versions']

            for version in versions:
                implemementation_content = requests.get(version['implementation'], timeout=120).content
                log_summary_content = requests.get(version['log-summary'], timeout=120).content

                computed_hash = hashlib.sha512()

                computed_hash.update(implemementation_content + log_summary_content)

                local_hash = computed_hash.hexdigest()

                if local_hash != version['sha512-hash']:
                    six.print_('[Data Processor: ' + key + ' / ' + str(version['version']) + '] Computed local hash \'' + local_hash + '\'. Found \'' + version['sha512-hash'] + '\' instead.')

                try:
                    arrow.get(version['created'])
                except: # pylint: disable=bare-except
                    six.print_('[Data Processor: ' + key + ' / ' + str(version['version']) + '] Unable to parse created date: ' + str(version['created']))
