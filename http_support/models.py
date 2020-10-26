# pylint: disable=no-member, line-too-long
# -*- coding: utf-8 -*-

from django.core.management import call_command
from django.db import models

from integrations.models import Integration


class ApiClient(models.Model):
    name = models.CharField(max_length=4096, unique=True)

    shared_secret = models.CharField(max_length=4096, unique=True)

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    integration = models.ForeignKey(Integration, related_name='api_clients', on_delete=models.CASCADE)

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
