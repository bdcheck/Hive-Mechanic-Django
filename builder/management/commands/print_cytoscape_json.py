# pylint: disable=no-member, line-too-long

import six

from django.core.management.base import BaseCommand

from ...models import Game

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('game_slug', type=str)

    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument, too-many-locals
        game_slug = cmd_options['game_slug']

        game = Game.objects.get(slug=game_slug)

        six.print_(game_slug + ': ' + game.cytoscape_json(indent=2))
