# pylint: disable=no-member, line-too-long

import json
import os

import six

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import InteractionCard

class Command(BaseCommand):
    def add_arguments(self, parser): # pylint: disable=unused-argument
        pass

    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument
        in_use = []

        for card in InteractionCard.objects.all():
            in_use.append(card.client_implementation.path)

        card_path = os.path.join(settings.MEDIA_ROOT, 'interaction_cards')

        six.print_(json.dumps(in_use, indent=2))

        six.print_(card_path)

        files = list(os.listdir(card_path))

        six.print_(json.dumps(files, indent=2))

        for js_file in files:
            js_path = os.path.join(card_path, js_file)

            if (js_path in in_use) is False:
                six.print_('Clearing %s...' % js_path)
                os.remove(js_path)
            else:
                six.print_('Retaining %s...' % js_path)
