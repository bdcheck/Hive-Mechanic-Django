# pylint: disable=no-member

from django.core.management.base import BaseCommand

from ...models import Session

class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument
        for session in Session.objects.filter(completed=None):
            session.nudge()
