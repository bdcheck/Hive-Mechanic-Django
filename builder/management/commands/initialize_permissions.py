# pylint: disable=no-member, line-too-long

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument, too-many-locals
        reader_permissions = ['builder_login']

        reader_group = Group.objects.get(name='Hive Mechanic Reader')

        for codename in reader_permissions:
            permission = Permission.objects.filter(codename=codename).first()

            if permission is not None:
                reader_group.permissions.add(permission)

        editor_permissions = [
            'add_game',
            'change_game',
            'delete_game',
            'view_game',
            'add_gameversion',
            'change_gameversion',
            'delete_gameversion',
            'view_gameversion',
        ]

        editor_permissions.extend(reader_permissions)

        editor_group = Group.objects.get(name='Hive Mechanic Game Editor')

        for codename in editor_permissions:
            permission = Permission.objects.filter(codename=codename).first()

            if permission is not None:
                editor_group.permissions.add(permission)

        manager_permissions = [
            'view_group',
            'add_user',
            'change_user',
            'delete_user',
            'view_user',
            'add_interactioncard',
            'change_interactioncard',
            'delete_interactioncard',
            'view_interactioncard',
            'view_integration',
            'add_execution',
            'change_execution',
            'delete_execution',
            'view_execution',
            'add_task',
            'change_task',
            'delete_task',
            'view_task',
            'view_incomingmessage',
            'view_incomingmessagemedia',
            'view_outgoingcall',
            'view_outgoingmessage',
        ]

        manager_group = Group.objects.get(name='Hive Mechanic Manager')

        for codename in manager_permissions:
            permission = Permission.objects.filter(codename=codename).first()

            if permission is not None:
                manager_group.permissions.add(permission)
