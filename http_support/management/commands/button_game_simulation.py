# pylint: disable=no-member

from builtins import str
import logging
import sys
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from ...client import HiveClient, VariableScope, GotoCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options): # pylint: disable=unused-argument
        logger = logging.getLogger('db')

        handler = logging.StreamHandler(sys.stdout)

        verbosity = int(options['verbosity'])
        
        if verbosity == 3:
            handler.setLevel(logging.DEBUG)
        elif verbosity == 2:
            handler.setLevel(logging.INFO)
        elif verbosity == 1:
            handler.setLevel(logging.WARN)
        else:
            handler.setLevel(logging.ERROR)
        
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s: %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)    
    
        client = HiveClient(api_url=settings.HIVE_API_URL, token=settings.HIVE_CLIENT_TOKEN, logger=logger)
        
        response = client.issue_command(GotoCommand('button-sequence#button_pressed'), player='pi:12345')
        
        logger.info('Response: ' + str(response))
        
        time.sleep(5)
        
        audio_url = client.fetch_variable('claimed_audio_file', scope=VariableScope.game)
        
        logger.info('Play audio URL: ' + str(audio_url))
