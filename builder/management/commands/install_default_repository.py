# pylint: disable=no-member, line-too-long

from __future__ import print_function

from future.moves.urllib.parse import urlparse

from django.core.management import call_command
from django.core.management.base import BaseCommand

from ...models import RemoteRepository

DEFAULT_REPOSITORY = 'https://raw.githubusercontent.com/audacious-software/Hive-Mechanic-Interaction-Cards/main/stable.json'
DEFAULT_REPOSITORY_NAME = 'Main Hive Mechanic Repository'

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--repository_url', type=str, default=DEFAULT_REPOSITORY)

    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument
        repo_url = cmd_options['repository_url']

        repo = RemoteRepository.objects.filter(url=repo_url).first()

        if repo is None:
            parsed_url = urlparse(repo_url)

            repo_name = parsed_url.netloc

            if repo_url == DEFAULT_REPOSITORY:
                repo_name = DEFAULT_REPOSITORY_NAME

            RemoteRepository.objects.create(url=repo_url, name=repo_name)

            call_command('refresh_repositories')
