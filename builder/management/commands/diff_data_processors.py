# pylint: disable=no-member, line-too-long

from __future__ import print_function

from django.core.management.base import BaseCommand

from ...models import DataProcessor

class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument
        for processor in DataProcessor.objects.all():
            processor.print_repository_diffs()
