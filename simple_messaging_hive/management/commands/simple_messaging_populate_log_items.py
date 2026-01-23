# pylint: disable=no-member, line-too-long

import logging

import arrow

from django.core.management.base import BaseCommand

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments

from activity_logger.models import LogTag, LogItem
from builder.models import Player

from ...models import IncomingMessage, OutgoingMessage

class Command(BaseCommand):
    @add_qs_arguments
    def add_arguments(self, parser):
        pass

    @handle_lock
    @handle_schedule
    def handle(self, *args, **options): # pylint: disable=unused-argument, too-many-locals, too-many-branches, too-many-statements
        logger = logging.getLogger()

        if options['verbosity'] > 1:
            logger.setLevel(logging.INFO)

        messaging_tag = LogTag.objects.filter(tag='messaging').first()

        if messaging_tag is None:
            messaging_tag = LogTag.objects.create(tag='messaging', name='All Messages')

        has_preview_tag = LogTag.objects.filter(tag='has_preview').first()

        if has_preview_tag is None:
            has_preview_tag = LogTag.objects.create(tag='has_preview', name='Has Attachment')

        incoming_tag = LogTag.objects.filter(tag='incoming_message').first()

        if incoming_tag is None:
            incoming_tag = LogTag.objects.create(tag='incoming_message', name='Incoming Messages')

        simple_messaging_tag = LogTag.objects.filter(tag='simple_messaging').first()

        if simple_messaging_tag is None:
            simple_messaging_tag = LogTag.objects.create(tag='simple_messaging_tag', name='Simple Messaging')

        last_incoming_log = simple_messaging_tag.log_items.order_by('-logged').first()

        when = arrow.get(0).datetime

        if last_incoming_log is not None:
            when = last_incoming_log.logged

        for message in IncomingMessage.objects.filter(receive_date__gt=when).order_by('receive_date'):
            log_item = LogItem.objects.create(source='simple_messaging_incoming_message:%s' % message.pk, message=message.message, logged=message.receive_date)
            log_item.tags.add(incoming_tag)
            log_item.tags.add(messaging_tag)

            if log_item.message is None or log_item.message == '':
                log_item.message = '(Blank or no message provided.)'

            metadata = log_item.fetch_metadata()
            metadata['player'] = 'messaging_player:%s' % message.source

            log_item.player = Player.objects.filter(identifier=metadata['player']).first()

            if message.integration is not None:
                metadata['game'] = '%s' % message.integration.game

                if message.integration.game is not None:
                    log_item.game_version = message.integration.game.versions.order_by('-pk').first()

            if message.media.count() > 0:
                media_files = []

                for media_item in message.media.all():
                    if media_item.content_file is not None:
                        media_files.append(media_item.content_file.url)

                metadata['media_files'] = media_files

                log_item.tags.add(has_preview_tag)

            log_item.update_metadata(metadata)

            logger.info('Created incoming message log item for %s', log_item.source)

        outgoing_tag = LogTag.objects.filter(tag='outgoing_message').first()

        if outgoing_tag is None:
            outgoing_tag = LogTag.objects.create(tag='outgoing_message', name='Outgoing Messages')

        for message in OutgoingMessage.objects.filter(sent_date__gt=when).order_by('sent_date'):
            log_item = LogItem.objects.create(source='simple_messaging_outgoing_message:%s' % message.pk, message=message.message, logged=message.sent_date)
            log_item.tags.add(outgoing_tag)
            log_item.tags.add(messaging_tag)

            if log_item.message is None or log_item.message == '':
                log_item.message = '(Blank or no message provided.)'

            metadata = log_item.fetch_metadata()
            metadata['player'] = 'messaging_player:%s' % message.destination

            log_item.player = Player.objects.filter(identifier=metadata['player']).first()

            if message.integration is not None:
                metadata['game'] = '%s' % message.integration.game

                if message.integration.game is not None:
                    log_item.game_version = message.integration.game.versions.order_by('-pk').first()

            if log_item.message.startswith('image:'):
                media_files = []

                tokens = log_item.message.split()

                media_files.append(tokens[0].replace('image:', ''))

                metadata['media_files'] = media_files

                log_item.tags.add(has_preview_tag)

            log_item.update_metadata(metadata)

            logger.info('Created outgoing message item for %s', log_item.source)
