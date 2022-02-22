# pylint: disable=no-member, line-too-long

from django.core.management.base import BaseCommand

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments

from ...models import GameVersion

class Command(BaseCommand):
    @add_qs_arguments
    def add_arguments(self, parser):
        pass

    @handle_lock
    @handle_schedule
    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument
        for version in GameVersion.objects.filter(cached_cytoscape=None):
            version.cytoscape_json(simplify=False, compute=True)
