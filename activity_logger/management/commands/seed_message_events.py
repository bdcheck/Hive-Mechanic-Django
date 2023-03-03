# pylint: disable=no-member, line-too-long
# -*- coding: utf-8 -*-

from __future__ import print_function

import json

from django.core.management.base import BaseCommand

from activity_logger.models import LogItem, LogTag
from builder.models import Player
from twilio_support.models import IncomingMessage, OutgoingMessage


class Command(BaseCommand):
    help = 'Seeds activity log with message events.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        source_dict = {}

        messaging_tag = LogTag.objects.filter(tag='messaging').first()

        if messaging_tag is None:
            messaging_tag = LogTag.objects.create(tag='messaging', name='messaging')

        incoming_tag = LogTag.objects.filter(tag='incoming_message').first()

        if incoming_tag is None:
            incoming_tag = LogTag.objects.create(tag='incoming_message', name='incoming message')

        for message in IncomingMessage.objects.all():
            existing_player = source_dict.get(message.source, None)

            if existing_player is None:
                identifier = ('twilio_player:%s' % message.source)

                existing_player = Player.objects.filter(identifier=identifier).first()

            event_source = 'incoming_msg:%d' % message.pk

            if existing_player is not None:
                event_source = 'player:%d' % existing_player.pk

            existing_item = LogItem.objects.filter(source=event_source, logged=message.receive_date, player=existing_player, tags=incoming_tag).first()

            if existing_item is None:
                existing_item = LogItem.objects.create(source=event_source, logged=message.receive_date, player=existing_player)

                existing_item.message = message.message

                metadata = {
                    'media_files': [],
                    'identifier': 'incoming_msg:%d' % message.pk,
                }

                for media_file in message.media.all():
                    metadata['media_files'].append(media_file.content_url)

                existing_item.metadata = json.dumps(metadata, indent=2)

                existing_item.save()

                existing_item.tags.add(incoming_tag)
                existing_item.tags.add(messaging_tag)

                existing_item.save()

        outgoing_tag = LogTag.objects.filter(tag='outgoing_message').first()

        if outgoing_tag is None:
            outgoing_tag = LogTag.objects.create(tag='outgoing_message', name='outgoing message')

        for message in OutgoingMessage.objects.exclude(sent_date=None):
            existing_player = source_dict.get(message.destination, None)

            if existing_player is None:
                identifier = ('twilio_player:%s' % message.destination)

                existing_player = Player.objects.filter(identifier=identifier).first()

            event_source = 'outgoing_msg:%d' % message.pk

            if existing_player is not None:
                event_source = 'player:%d' % existing_player.pk

            existing_item = LogItem.objects.filter(source=event_source, logged=message.sent_date, player=existing_player, tags=outgoing_tag).first()

            if existing_item is None:
                existing_item = LogItem.objects.create(source=event_source, logged=message.sent_date, player=existing_player)

                existing_item.message = message.message

                metadata = {
                    'media_files': [],
                    'identifier': 'outgoing_msg:%d' % message.pk,
                }

                existing_item.metadata = json.dumps(metadata, indent=2)

                existing_item.save()

                existing_item.tags.add(outgoing_tag)
                existing_item.tags.add(messaging_tag)

                existing_item.save()
