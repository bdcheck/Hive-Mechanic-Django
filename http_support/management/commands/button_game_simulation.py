# pylint: disable=no-member, line-too-long

import logging
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from ...client import HiveClient, VariableScope, TriggerInterruptCommand, SetVariableCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options): # pylint: disable=unused-argument
        verbosity = int(options['verbosity'])

        level = logging.DEBUG

        if verbosity == 3:
            level = logging.DEBUG
        elif verbosity == 2:
            level = logging.INFO
        elif verbosity == 1:
            level = logging.WARN
        else:
            level = logging.ERROR

        logger = settings.FETCH_LOGGER(level)

        client = HiveClient(api_url=settings.HIVE_API_URL, token=settings.HIVE_CLIENT_TOKEN, logger=logger)

        commands = [
            TriggerInterruptCommand('BUTTON-PRESSED'),
            SetVariableCommand('button_press_ts', timezone.now().isoformat(), VariableScope.game)
        ]

        response = client.issue_commands(commands, player='pi:12345')

        logger.info('Response: %s', response)

        time.sleep(5)

        audio_url = client.fetch_variable('claimed_audio_file', scope=VariableScope.game)

        logger.info('Play audio URL: %s', audio_url)
