# pylint: disable=no-member, line-too-long

import logging

from django.core.management.base import BaseCommand
from django.db.models import Q

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments

from builder.models import Session

from ...models import LogItem

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

        log_query = LogItem.objects.filter(session=None).exclude(player=None)

        logger.info('Processing %s log items missing sessions...', log_query.count())

        for log_item in log_query:
            query_params = Q(player=log_item.player) & Q(started__lte=log_item.logged) & (Q(completed=None) | Q(completed__gte=log_item.logged))
            query = Session.objects.filter(query_params)

            logger.info('Found %s / %s sessions...', (query.count(), log_item.pk))

            if query.count() == 1:
                log_item.session = query.first()
                log_item.save()
