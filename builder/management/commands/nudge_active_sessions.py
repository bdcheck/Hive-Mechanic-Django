# pylint: disable=no-member, line-too-long

from django.core.management.base import BaseCommand
from django.utils import timezone

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments

from cli_support.models import HiveActivityFinishedException

from ...models import Session

class Command(BaseCommand):
    @add_qs_arguments
    def add_arguments(self, parser):
        pass

    @handle_lock
    @handle_schedule
    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument
        for session in Session.objects.filter(completed=None):
            if 'is_testing' in session.session_state and session.session_state['is_testing'] is True:
                pass # Skip - this is a test session
            else:
                try:
                    session.nudge()
                except HiveActivityFinishedException:
                    pass
