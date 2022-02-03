# pylint: disable=no-member, line-too-long

from django.core.management.base import BaseCommand

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments

from ...models import Integration

class Command(BaseCommand):
    @add_qs_arguments
    def add_arguments(self, parser):
        pass

    @handle_lock
    @handle_schedule
    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument
        for integration in Integration.objects.all():
            integration.is_enabled()
