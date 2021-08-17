# pylint: disable=no-member, line-too-long

from __future__ import print_function

from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument, too-many-locals
        for permission in Permission.objects.all():
            print(permission.name + ' -- ' + permission.codename)
