# pylint: disable=no-member, line-too-long

import arrow

from django.core.management.base import BaseCommand

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments


from activity_logger.models import LogTag, LogItem
from builder.models import Player

from ...models import IncomingMessage, OutgoingMessage, IncomingCallResponse

class Command(BaseCommand):
    @add_qs_arguments
    def add_arguments(self, parser):
        pass

    @handle_lock
    @handle_schedule
    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument, too-many-locals, too-many-branches, too-many-statements
        messaging_tag = LogTag.objects.filter(tag='messaging').first()

        if messaging_tag is None:
            messaging_tag = LogTag.objects.create(tag='messaging', name='All Messages')

        has_preview_tag = LogTag.objects.filter(tag='has_preview').first()

        if has_preview_tag is None:
            has_preview_tag = LogTag.objects.create(tag='has_preview', name='Has Preview')

        voice_message_tag = LogTag.objects.filter(tag='voice_message_tag').first()

        if voice_message_tag is None:
            voice_message_tag = LogTag.objects.create(tag='voice_message_tag', name='Voice Message')

        incoming_tag = LogTag.objects.filter(tag='incoming_message').first()

        if incoming_tag is None:
            incoming_tag = LogTag.objects.create(tag='incoming_message', name='Incoming Messages')

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

            print('Created incoming message log item for %s' % log_item.source)

        outgoing_tag = LogTag.objects.filter(tag='outgoing_message').first()

        if outgoing_tag is None:
            outgoing_tag = LogTag.objects.create(tag='outgoing_message', name='Outgoing Messages')

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

            print('Created outgoing message item for %s' % log_item.source)

        phone_call_tag = LogTag.objects.filter(tag='phone_call').first()

        if phone_call_tag is None:
            phone_call_tag = LogTag.objects.create(tag='phone_call', name='Phone Call')

        incoming_call_tag = LogTag.objects.filter(tag='incoming_call').first()

        if incoming_call_tag is None:
            incoming_call_tag = LogTag.objects.create(tag='incoming_call', name='Incoming Phone Call')

        last_incoming_call_log = incoming_call_tag.log_items.order_by('-logged').first()

        when = arrow.get(0).datetime

        if last_incoming_call_log is not None:
            when = last_incoming_call_log.logged

        for incoming_call in IncomingCallResponse.objects.filter(receive_date__gt=when).order_by('receive_date'):
            log_item = LogItem.objects.create(source='incoming_call:%s' % incoming_call.pk, message='(Incoming call response)', logged=incoming_call.receive_date)
            log_item.tags.add(incoming_call_tag)
            log_item.tags.add(phone_call_tag)

            if log_item.message is None or log_item.message == '':
                log_item.message = '(Blank or no message provided.)'

            metadata = log_item.fetch_metadata()
            metadata['player'] = 'twilio_player:%s' % incoming_call.source

            log_item.player = Player.objects.filter(identifier=metadata['player']).first()

            if incoming_call.integration is not None:
                metadata['game'] = '%s' % incoming_call.integration.game

                if incoming_call.integration.game is not None:
                    log_item.game_version = incoming_call.integration.game.versions.order_by('-pk').first()

            if incoming_call.media.count() > 0:
                media_files = []

                for media_item in incoming_call.media.all():
                    try:
                        if media_item.content_file is not None:
                            media_files.append(media_item.content_file.url)
                    except ValueError:
                        pass

                metadata['media_files'] = media_files

                log_item.tags.add(has_preview_tag)
                log_item.tags.add(voice_message_tag)

            log_item.update_metadata(metadata)

            print('Created incoming call log item for %s' % log_item.source)
