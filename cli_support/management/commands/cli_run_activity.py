# pylint: disable=no-member, line-too-long

import os
import time
import threading

import psutil

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from builder.models import Game

from integrations.models import Integration

from ...models import HiveActivityFinishedException

class NudgeThread(threading.Thread):
    def __init__(self, integration):
        threading.Thread.__init__(self)
        self.integration = integration
        self.continue_running = True

    def run(self):
        try:
            while self.continue_running:
                self.integration.process_incoming(None)

                time.sleep(1)
        except HiveActivityFinishedException:
            pass

        print('Activity concluded. Exiting...')

        current_pid = os.getpid()

        this_process = psutil.Process(current_pid)
        this_process.terminate()

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('activity_slug', type=str)

    def handle(self, *args, **options):
        activity = Game.objects.filter(slug=options['activity_slug']).first()

        if activity is not None:
            integration = Integration.objects.filter(type='command_line', game=activity).first()

            if integration is None:
                slug = slugify(activity.name + ' (CLI)')

                integration = Integration.objects.create(type='command_line', url_slug=slug, game=activity, name=activity.name + ' (CLI)')

            nudge_thread = NudgeThread(integration)

            nudge_thread.start()

            try:
                while nudge_thread.is_alive():
                    input_str = input() # nosec

                    integration.process_incoming(input_str)
            except KeyboardInterrupt:
                nudge_thread.continue_running = False
        else:
            print('Unable to find activity with identifier "' + options['activity_slug'] + '".')
