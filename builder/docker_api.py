# pylint: disable=line-too-long, no-member

import json

import iso8601

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core import serializers

from .models import Game, GameVersion, InteractionCard

def import_objects(file_type, import_file):
    if file_type == 'builder.game':
        return import_games(import_file)

    return None

def import_games(import_file): # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    user_messages = []

    with import_file.open() as file_stream:
        games_json = json.load(file_stream)

        games_imported = 0
        versions_imported = 0

        for game_json in games_json: # pylint: disable=too-many-nested-blocks
            if game_json.get('model', None) == 'builder.game':
                game_slug = game_json.get('fields', {}).get('slug', None)

                if Game.objects.filter(slug=game_slug).count() > 0:
                    user_messages.append(('Activity with slug "%s" already exists. Skipping...' % game_slug, messages.WARNING))

                    continue

                game_obj = Game()

                for field_key in game_json.get('fields', {}).keys():
                    field_value = game_json.get('fields', {}).get(field_key, None)

                    if field_key in ('metadata_updated', 'archived'):
                        if field_value is not None:
                            field_value = iso8601.parse_date(field_value)
                    elif field_key in ('viewers', 'editors'):
                        game_obj.save()

                        for username in field_value:
                            user = get_user_model().objects.filter(username=username).first()

                            if user is None:
                                user_messages.append(('Unable to locate user with identifier "%s".' % username, messages.WARNING))
                            else:
                                if field_key == 'viewers':
                                    game_obj.viewers.add(user)
                                else:
                                    game_obj.editors.add(user)
                    elif field_key == 'cards':
                        game_obj.save()

                        for identifier in field_value:
                            card = InteractionCard.objects.filter(identifier=identifier).first()

                            if card is None:
                                user_messages.append(('Unable to locate card with identifier "%s".' % identifier, messages.WARNING))
                            else:
                                game_obj.cards.add(card)

                    if (field_key in ('viewers', 'editors', 'cards',)) is False:
                        setattr(game_obj, field_key, field_value)

                game_obj.save()

                games_imported += 1

                for version in game_json.get('version', []):
                    if version.get('model', None) == 'builder.gameversion':
                        version_obj = GameVersion(game=game_obj)

                        for field_key in version.get('fields', {}).keys():
                            field_value = version.get('fields', {}).get(field_key, None)

                            if field_key == 'created':
                                if field_value is not None:
                                    field_value = iso8601.parse_date(field_value)
                            elif field_key == 'creator__username':
                                creator = get_user_model().objects.filter(username=field_value).first()

                                if creator is None:
                                    creator = get_user_model().objects.create(username=field_value, is_active=False)

                                field_key = 'creator'
                                field_value = creator

                            setattr(version_obj, field_key, field_value)

                        version_obj.save()

                        versions_imported += 1

        if games_imported > 1:
            user_messages.append(('%s activities imported.' % games_imported, messages.SUCCESS))
        elif games_imported == 1:
            user_messages.append(('1 activity imported.', messages.SUCCESS))
        else:
            user_messages.append(('No activities imported.', messages.INFO))

        if versions_imported > 1:
            user_messages.append(('%s activity versions imported.' % versions_imported, messages.SUCCESS))
        elif versions_imported == 1:
            user_messages.append(('1 activity version imported.', messages.SUCCESS))
        else:
            user_messages.append(('No activity versions imported.', messages.INFO))

    return user_messages

def export_games(queryset):
    to_export = []

    for game in queryset:
        game_json = json.loads(serializers.serialize('json', Game.objects.filter(pk=game.pk)))[0]

        del game_json['pk']

        game_json['versions'] = []

        for role in ('editors', 'viewers',):
            new_roles = []

            for user_pk in game_json['fields'][role]:
                user = get_user_model().objects.filter(pk=user_pk).first()

                if user is not None:
                    new_roles.append(user.username)
                else:
                    new_roles.append('unknown-user')

            game_json['fields'][role] = new_roles

        new_cards = []

        for card_pk in game_json['fields']['cards']:
            card = InteractionCard.objects.get(pk=card_pk)

            new_cards.append(card.identifier)

        game_json['fields']['cards'] = new_cards

        for version in game.versions.all().order_by('created'):
            version_json = json.loads(serializers.serialize('json', GameVersion.objects.filter(pk=version.pk)))[0]

            del version_json['pk']
            del version_json['fields']['game']

            creator = get_user_model().objects.filter(pk=version_json['fields']['creator']).first()

            if creator is None:
                version_json['fields']['creator__username'] = 'unknown-dialog-script-creator'
            else:
                version_json['fields']['creator__username'] = creator.username

            del version_json['fields']['creator']

            game_json['versions'].append(version_json)

        to_export.append(game_json)

    return to_export

def export_objects(queryset, queryset_name):
    to_export = []

    if queryset_name == 'Game':
        to_export.extend(export_games(queryset))

    return to_export
