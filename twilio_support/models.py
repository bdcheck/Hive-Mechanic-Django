# pylint: disable=line-too-long, no-member
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
import traceback

from twilio.rest import Client

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

from integrations.models import Integration

class OutgoingMessage(models.Model):
    destination = models.CharField(max_length=256)

    send_date = models.DateTimeField()
    sent_date = models.DateTimeField(null=True, blank=True)

    message = models.TextField(max_length=1024)

    errored = models.BooleanField(default=False)
    transmission_metadata = JSONField(default=dict, blank=True, null=True)

    integration = models.ForeignKey(Integration, related_name='twilio_outgoing')

    def transmit(self):
        if self.transmission_metadata is None:
            self.transmission_metadata = {}

        if self.sent_date is not None:
            raise Exception('Message (pk=' + str(self.pk) + ') already transmitted on ' + self.sent_date.isoformat() + '.')

        try:
            client = Client(self.integration.configuration['client_id'], self.integration.configuration['auth_token'])
            
            if self.message.startswith('image:'):
                message = client.messages.create(to=self.destination, from_=self.integration.configuration['phone_number'], media_url=[self.message[6:]])
                
                print('GO TO BED')
                time.sleep(10)
                print('WAKE UP')
            else:
                message = client.messages.create(to=self.destination, from_=self.integration.configuration['phone_number'], body=self.message)

            self.sent_date = timezone.now()
            self.transmission_metadata['twilio_sid'] = message.sid
            self.errored = False
            self.save()
            
        except: # pylint: disable=bare-except
            self.errored = True

            self.transmission_metadata['error'] = traceback.format_exc().splitlines()

            self.save()

class IncomingMessage(models.Model):
    source = models.CharField(max_length=256)

    receive_date = models.DateTimeField()

    message = models.TextField(max_length=1024)

    transmission_metadata = JSONField(default=dict, blank=True, null=True)

    integration = models.ForeignKey(Integration, related_name='twilio_incoming', null=True, blank=True)

def process_incoming(integration, payload):
    integration.process_player_incoming('twilio_player', payload['From'], payload['Body'].strip())

def execute_action(integration, session, action):
    print('TWILIO ACTION: ' + str(action))
    
    player = session.player
    
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
    
    return False
