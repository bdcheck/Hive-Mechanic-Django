# pylint: disable=no-member, line-too-long

from django.core.management.base import BaseCommand
from django.db.models import Q

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments

from ...models import GameVersion

class Command(BaseCommand):
    @add_qs_arguments
    def add_arguments(self, parser):
        pass

    @handle_lock
    @handle_schedule
    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument
        query = Q(cached_cytoscape=None) | Q(cached_cytoscape='null')

        for version in GameVersion.objects.filter(query):
            graph = version.cytoscape_json(simplify=False, compute=True)

            # if graph is None:
            #    print('Unable to update %s' % version)
