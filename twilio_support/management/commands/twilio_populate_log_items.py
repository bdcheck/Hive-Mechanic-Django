# pylint: disable=no-member, line-too-long

import arrow

from django.core.management.base import BaseCommand

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments


from activity_logger.models import LogTag, LogItem

from ...models import IncomingMessage, OutgoingMessage

class Command(BaseCommand):
    @add_qs_arguments
    def add_arguments(self, parser):
        pass

    @handle_lock
    @handle_schedule
    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument, too-many-locals
        messaging_tag = LogTag.objects.get(tag='messaging')
        has_preview_tag = LogTag.objects.get(tag='has_preview')

        incoming_tag = LogTag.objects.get(tag='incoming_message')

        last_incoming_log = incoming_tag.log_items.order_by('-logged').first()

        when = arrow.get(0).datetime

        if last_incoming_log is not None:
            when = last_incoming_log.logged

        for message in IncomingMessage.objects.filter(receive_date__gt=when).order_by('receive_date'):
            log_item = LogItem.objects.create(source='incoming_message:%s' % message.pk, message=message.message, logged=message.receive_date)
            log_item.tags.add(incoming_tag)
            log_item.tags.add(messaging_tag)

            if log_item.message is None or log_item.message == '':
                log_item.message = '(Blank or no message provided.)'

            metadata = log_item.fetch_metadata()
            metadata['player'] = 'twilio_player:%s' % message.source

            if message.integration is not None:
                metadata['game'] = '%s' % message.integration.game

            if message.media.count() > 0:
                media_files = []

                for media_item in message.media.all():
                    if media_item.content_file is not None:
                        media_files.append(media_item.content_file.url)

                metadata['media_files'] = media_files

                log_item.tags.add(has_preview_tag)

            log_item.update_metadata(metadata)

            print('Created incoming message log item for %s' % log_item.source)

        outgoing_tag = LogTag.objects.get(tag='outgoing_message')

        last_outgoing_log = outgoing_tag.log_items.order_by('-logged').first()

        when = arrow.get(0).datetime

        if last_outgoing_log is not None:
            when = last_outgoing_log.logged

        for message in OutgoingMessage.objects.filter(sent_date__gt=when).order_by('sent_date'):
            log_item = LogItem.objects.create(source='outgoing_message:%s' % message.pk, message=message.message, logged=message.sent_date)
            log_item.tags.add(outgoing_tag)
            log_item.tags.add(messaging_tag)

            if log_item.message is None or log_item.message == '':
                log_item.message = '(Blank or no message provided.)'

            metadata = log_item.fetch_metadata()
            metadata['player'] = 'twilio_player:%s' % message.destination

            if message.integration is not None:
                metadata['game'] = '%s' % message.integration.game

            if log_item.message.startswith('image:'):
                media_files = []

                tokens = log_item.message.split()

                media_files.append(tokens[0].replace('image:', ''))

                metadata['media_files'] = media_files

                log_item.tags.add(has_preview_tag)

            log_item.update_metadata(metadata)

            print('Created outgoing message item for %s' % log_item.source)
