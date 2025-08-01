# pylint: disable=no-member, line-too-long

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument, too-many-locals
        reader_permissions = ['builder_login']

        reader_group = Group.objects.filter(name='Hive Mechanic Reader').first()

        if reader_group is None:
            reader_group = Group.objects.create(name='Hive Mechanic Reader')

        for codename in reader_permissions:
            permission = Permission.objects.filter(codename=codename).first()

            if permission is not None and reader_group.permissions.filter(codename=codename).count() == 0:
                print('Adding permission "%s (%s)" to %s...' % (permission, permission.codename, reader_group))

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
            'builder_login',
            'add_file',
            'add_folder',
            'add_image',
            'can_use_directory_listing',
            'change_file',
            'change_folder',
            'change_image',
            'delete_file',
            'delete_folder',
            'delete_image',
            'view_file',
            'view_folder',
            'view_image',
        ]

        editor_permissions.extend(reader_permissions)

        editor_group = Group.objects.filter(name='Hive Mechanic Game Editor').first()

        if editor_group is None:
            editor_group = Group.objects.create(name='Hive Mechanic Game Editor')

        for codename in editor_permissions:
            permission = Permission.objects.filter(codename=codename).first()

            if permission is not None and editor_group.permissions.filter(codename=codename).count() == 0:
                print('Adding permission "%s (%s)" to %s...' % (permission, permission.codename, editor_group))

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
            'builder_login',
            'add_file',
            'add_folder',
            'add_image',
            'can_use_directory_listing',
            'change_file',
            'change_folder',
            'change_image',
            'delete_file',
            'delete_folder',
            'delete_image',
            'view_file',
            'view_folder',
            'view_image',
            'builder_moderate',
        ]

        manager_group = Group.objects.filter(name='Hive Mechanic Manager').first()

        if manager_group is None:
            manager_group = Group.objects.create(name='Hive Mechanic Manager')

        for codename in manager_permissions:
            permission = Permission.objects.filter(codename=codename).first()

            if permission is not None and manager_group.permissions.filter(codename=codename).count() == 0:
                print('Adding permission "%s (%s)" to %s...' % (permission, permission.codename, manager_group))

                manager_group.permissions.add(permission)
