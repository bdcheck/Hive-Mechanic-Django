# pylint: disable=line-too-long, no-member

import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core import serializers

from builder.models import Game

from .models import Integration

def import_objects(file_type, import_file):
    if file_type == 'integrations.integration':
        return import_integrations(import_file)

    return None

def import_integrations(import_file): # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    user_messages = []

    with import_file.open() as file_stream:
        integrations_json = json.load(file_stream)

        integrations_imported = 0

        for integration_json in integrations_json: # pylint: disable=too-many-nested-blocks
            if integration_json.get('model', None) == 'integrations.integration':
                url_slug = integration_json.get('fields', {}).get('url_slug', None)

                if Integration.objects.filter(url_slug=url_slug).count() > 0:
                    user_messages.append(('Integration with URL slug "%s" already exists. Skipping...' % url_slug, messages.WARNING))

                    continue

                integration_obj = Integration()

                for field_key in integration_json.get('fields', {}).keys():
                    field_value = integration_json.get('fields', {}).get(field_key, None)

                    if field_key in ('viewers', 'editors'):
                        integration_obj.save()

                        for username in field_value:
                            user = get_user_model().objects.filter(username=username).first()

                            if user is None:
                                user_messages.append(('Unable to locate user with identifier "%s".' % username, messages.WARNING))
                            else:
                                if field_key == 'viewers':
                                    integration_obj.viewers.add(user)
                                else:
                                    integration_obj.editors.add(user)
                    elif field_key == 'game':
                        game = Game.objects.filter(slug=field_value).first()

                        if field_value is not None and game is None:
                            user_messages.append(('Unable to locate activity with identifier "%s". Setting up integration without link' % field_value, messages.WARNING))
                        else:
                            integration_obj.game = game

                    if (field_key in ('viewers', 'editors', 'game')) is False:
                        setattr(integration_obj, field_key, field_value)

                integration_obj.save()

                integrations_imported += 1

        if integrations_imported > 1:
            user_messages.append(('%s integrations imported.' % integrations_imported, messages.SUCCESS))
        elif integrations_imported == 1:
            user_messages.append(('1 integration imported.', messages.SUCCESS))
        else:
            user_messages.append(('No intergations imported.', messages.INFO))

    return user_messages

def export_integrations(queryset):
    to_export = []

    for integration in queryset:
        integration_json = json.loads(serializers.serialize('json', Integration.objects.filter(pk=integration.pk)))[0]

        del integration_json['pk']

        for role in ('editors', 'viewers',):
            new_roles = []

            for user_pk in integration_json['fields'][role]:
                user = get_user_model().objects.filter(pk=user_pk).first()

                if user is not None:
                    new_roles.append(user.username)
                else:
                    new_roles.append('unknown-user')

            integration_json['fields'][role] = new_roles

        game = integration.game

        if game is not None:
            integration_json['fields']['game'] = game.slug

        to_export.append(integration_json)

    return to_export

def export_objects(queryset, queryset_name):
    to_export = []

    if queryset_name == 'Integration':
        to_export.extend(export_integrations(queryset))

    return to_export
