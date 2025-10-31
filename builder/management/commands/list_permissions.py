# pylint: disable=no-member, line-too-long

import six

from django.contrib import auth
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument, too-many-locals
        permissions = set()

        tmp_superuser = get_user_model()(is_active=True, is_superuser=True)

        for backend in auth.get_backends():
            if hasattr(backend, "get_all_permissions"):
                permissions.update(backend.get_all_permissions(tmp_superuser))

        sorted_list_of_permissions = sorted(list(permissions))

        for permission in sorted_list_of_permissions:
            six.print_(permission)
