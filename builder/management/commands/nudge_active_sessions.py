# pylint: disable=no-member

from django.core.management.base import BaseCommand

from quicksilver.decorators import handle_lock, handle_schedule

from ...models import Session

class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    @handle_lock
    @handle_schedule
    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument
        for session in Session.objects.filter(completed=None):
            session.nudge()
