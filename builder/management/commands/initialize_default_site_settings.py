# pylint: disable=no-member, line-too-long

from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import SiteSettings

class Command(BaseCommand):
    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument, too-many-locals
        if SiteSettings.objects.all().count() == 0:
            SiteSettings.objects.create(name='New Hive Mechanic Site', created=timezone.now(), last_updated=timezone.now())
