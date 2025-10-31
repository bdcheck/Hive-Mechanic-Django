# pylint: disable=no-member, line-too-long

import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments

from activity_logger.models import log

from ...models import Session, SiteSettings

class Command(BaseCommand):
    @add_qs_arguments
    def add_arguments(self, parser):
        pass

    @handle_schedule
    @handle_lock
    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument
        duration = datetime.timedelta(days=14)

        settings = SiteSettings.objects.all().first()

        if settings is not None:
            duration = settings.maximum_session_duration

        threshold = timezone.now() - duration

        for session in Session.objects.filter(completed=None, started__lte=threshold):
            session.complete()

            if session.session_state is None:
                session.session_state = {}

            session.session_state['close_reason'] = 'Force-closed session, as it was older than the max. session duration: %s' % duration
            session.save()

            tags = ['session', 'warning']

            log('session:%s' % session.pk, 'Force-closed session, as it was older than the max. session duration: %s' % duration, tags=tags, player=session.player)
