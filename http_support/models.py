# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

# from django.db import models

def process_incoming(integration, payload):
    metadata = {'last_message': incoming_message}

    integration.process_player_incoming('twilio_player', payload['From'], payload['Body'].strip(), metadata)

'''
def process_incoming(integration, payload):
    if ('Body' in payload) is False:
        if 'Digits' in payload:
            payload['Body'] = payload['Digits']
        elif 'SpeechResult' in payload:
            payload['Body'] = payload['SpeechResult']
        else:
            payload['Body'] = ''

    if 'CallStatus' in payload:
        from_ = payload['From']

        payload['From'] = payload['To']

        payload['To'] = from_

    incoming_message = IncomingMessage.objects.filter(source=payload['From']).order_by('-receive_date').first()

    if payload['Body'] or incoming_message.media.count() > 0:
'''


def execute_action(integration, action):
    action_type = action['action']
    
    if action_type == 'check_server':
        return None 
        
    return 'No action found for "' + action_type + '".'
