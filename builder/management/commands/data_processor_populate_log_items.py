# pylint: disable=no-member, line-too-long

import arrow

from django.core.management.base import BaseCommand

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments


from activity_logger.models import LogTag, LogItem
from builder.models import Player

from ...models import DataProcessorLog

class Command(BaseCommand):
    @add_qs_arguments
    def add_arguments(self, parser):
        pass

    @handle_schedule
    @handle_lock
    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument, too-many-locals, too-many-branches, too-many-statements
        api_calls_tag = LogTag.objects.filter(tag='api-calls').first()

        if api_calls_tag is None:
            api_calls_tag = LogTag.objects.create(tag='api-calls', name='API Calls')

        has_preview_tag = LogTag.objects.filter(tag='has_preview').first()

        if has_preview_tag is None:
            has_preview_tag = LogTag.objects.create(tag='has_preview', name='Has Attachment')

        last_api_log = api_calls_tag.log_items.order_by('-logged').first()

        when = arrow.get(0).datetime

        if last_api_log is not None:
            when = last_api_log.logged

        for processor_log_item in DataProcessorLog.objects.filter(requested__gt=when).order_by('requested'):
            summary, preview_url = processor_log_item.fetch_summary()

            log_item = LogItem.objects.create(source='api_call:%s' % processor_log_item.pk, message=summary, logged=processor_log_item.requested)
            log_item.tags.add(api_calls_tag)

            metadata = log_item.fetch_metadata()
            metadata['player'] = 'twilio_player:%s' % processor_log_item.player
            metadata['game'] = '%s' % processor_log_item.game

            if processor_log_item.session is not None:
                log_item.game_version = processor_log_item.session.game_version

            log_item.player = Player.objects.filter(identifier=metadata['player']).first()

            if preview_url is not None:
                media_files = []

                media_files.append(preview_url)

                metadata['media_files'] = media_files

                log_item.tags.add(has_preview_tag)

            log_item.update_metadata(metadata)

            print('Created data processor log item for %s' % log_item.player)
