# pylint: disable=no-member, line-too-long

import six

from django.core.management.base import BaseCommand

from ...models import Game

class Command(BaseCommand):
    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument, too-many-locals, too-many-statements, too-many-branches
        for game in Game.objects.all():
            for card in game.cards.all():
                if card.enabled is False:
                    card.enabled = True
                    card.save()

                    six.print_('Enabled card "%s".' % card)
