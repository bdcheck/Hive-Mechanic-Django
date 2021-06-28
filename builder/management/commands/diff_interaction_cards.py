# pylint: disable=no-member, line-too-long

import hashlib
import json
import zipfile

import zipstream

from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import InteractionCard

class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument
        for card in InteractionCard.objects.all():
            card.print_repository_diffs()
