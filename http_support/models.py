# pylint: disable=no-member, line-too-long
# -*- coding: utf-8 -*-

from six import python_2_unicode_compatible

from django.conf import settings
from django.core.management import call_command
from django.db import models

from integrations.models import Integration

@python_2_unicode_compatible
class ApiClient(models.Model):
    class Meta: # pylint: disable=old-style-class, no-init, too-few-public-methods
        verbose_name_plural = 'API clients'
        verbose_name = 'API client'

    name = models.CharField(max_length=4096, unique=True)

    editors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='http_api_client_editables')
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='http_api_client_viewables')

    shared_secret = models.CharField(max_length=4096, unique=True)

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    integration = models.ForeignKey(Integration, related_name='api_clients', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

def process_incoming(integration, payload): # pylint: disable=too-many-branches
    issues = []

    if 'commands' in payload and 'player' in payload:
        tokens = payload['player'].split(':')

        if len(tokens) < 2:
            tokens = ['http_player', tokens[0]]

        integration.process_player_incoming(tokens[0], tokens[1], payload['commands'])

        call_command('nudge_active_sessions')

    return issues

def execute_action(integration, session, action): # pylint: disable=unused-argument
    return False

def annotate_statistics(integration, statistics):
    statistics['type'] = 'Hive Mechanic HTTP API'

    statistics['details'].append(['API Client Count', ApiClient.objects.filter(integration=integration).count()])

    # HTTP integration metrics: most recent contact date, number of contacts
    # from a Raspberry pi etc:
    # (a) today, (b) past week; (c) life of site
