# pylint: disable=no-member, line-too-long
# -*- coding: utf-8 -*-


import json
import re

from django.core.management import call_command
from django.db import models

from builder.models import Player, Session
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


def execute_action(integration, session, action):
    player = session.player

    '''
    if action['type'] == 'echo':
        outgoing = OutgoingMessage(destination=player.player_state['twilio_player'])
        outgoing.send_date = timezone.now()
        outgoing.message = action['message']
        outgoing.integration = integration

        outgoing.save()

        outgoing.transmit()

        return True
    elif action['type'] == 'echo-image':
        outgoing = OutgoingMessage(destination=player.player_state['twilio_player'])
        outgoing.send_date = timezone.now()
        outgoing.message = 'image:' + action['image-url']
        outgoing.integration = integration

        outgoing.save()

        outgoing.transmit()

        return True
    elif action['type'] == 'echo-voice':
        unsent = OutgoingCall.objects.filter(destination=player.player_state['twilio_player'], sent_date=None)

        outgoing = OutgoingCall(destination=player.player_state['twilio_player'])
        outgoing.start_call = unsent.count() == 0
        outgoing.send_date = timezone.now()
        outgoing.message = action['message']
        outgoing.next_action = action['next_action']

        outgoing.integration = integration

        outgoing.save()

        if outgoing.next_action != 'hangup' and outgoing.start_call is True:
            outgoing.transmit()

        return True
    '''

    return False
