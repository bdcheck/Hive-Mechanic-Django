# pylint: disable=line-too-long, no-member
# -*- coding: utf-8 -*-

from __future__ import print_function

from builtins import str # pylint: disable=redefined-builtin

import sys
import time
import traceback

from twilio.rest import Client

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import smart_text

from integrations.models import Integration

OUTGOING_CALL_NEXT_ACTIONS = (
    ('continue', 'Continue',),
    ('pause', 'Pause',),
    ('gather', 'Gather Response',),
    ('hangup', 'Hang Up',),
)

GATHER_INPUT_OPTIONS = (
    ('dtmf speech', 'Speech and Key Presses'),
    ('dtmf', 'Key Presses'),
    ('speech', 'Speech'),
)

GATHER_SPEECH_MODELS = (
    ('default', 'Default'),
    ('numbers_and_commands', 'Numbers and Commands'),
    ('phone_call', 'Phone Call'),
)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def last_message_for_player(game, player):
    integration = Integration.objects.filter(game=game).first()

    phone = player.player_state.get('twilio_player', None)

    incoming = IncomingMessage.objects.filter(source=phone, integration=integration).order_by('-receive_date').first()

    if incoming is not None:
        return {
            'message': incoming.message,
            'received': incoming.receive_date
        }

    return None

class PermissionsSupport(models.Model):
    class Meta: # pylint: disable=old-style-class, no-init, too-few-public-methods
        managed = False
        default_permissions = ()

        permissions = (
            ('twilio_history_access', 'Access Twilio message history'),
        )

class OutgoingMessage(models.Model):
    destination = models.CharField(max_length=256)

    send_date = models.DateTimeField()
    sent_date = models.DateTimeField(null=True, blank=True)

    message = models.TextField(max_length=1024)

    errored = models.BooleanField(default=False)
    transmission_metadata = JSONField(default=dict, blank=True, null=True)

    integration = models.ForeignKey(Integration, related_name='twilio_outgoing', null=True, blank=True, on_delete=models.SET_NULL)

    def transmit(self):
        if self.transmission_metadata is None:
            self.transmission_metadata = {}

        if self.sent_date is not None:
            raise Exception('Message (pk=' + str(self.pk) + ') already transmitted on ' + self.sent_date.isoformat() + '.')

        try:
            client = Client(self.integration.configuration['client_id'], self.integration.configuration['auth_token'])

            if self.message.startswith('image:'):
                message = client.messages.create(to=self.destination, from_=self.integration.configuration['phone_number'], media_url=[self.message[6:]])

                time.sleep(10)
            else:
                message = client.messages.create(to=self.destination, from_=self.integration.configuration['phone_number'], body=self.message)

            self.sent_date = timezone.now()
            self.transmission_metadata['twilio_sid'] = message.sid
            self.errored = False
            self.save()

        except: # pylint: disable=bare-except
            traceback.print_exc()
            self.errored = True

            self.transmission_metadata['error'] = traceback.format_exc().splitlines()

            self.save()

class IncomingMessage(models.Model):
    source = models.CharField(max_length=256)

    receive_date = models.DateTimeField()

    message = models.TextField(max_length=1024)

    transmission_metadata = JSONField(default=dict, blank=True, null=True)

    integration = models.ForeignKey(Integration, related_name='twilio_incoming', null=True, blank=True, on_delete=models.SET_NULL)

class IncomingMessageMedia(models.Model):
    message = models.ForeignKey(IncomingMessage, related_name='media', on_delete=models.CASCADE)

    index = models.IntegerField(default=0)

    content_file = models.FileField(upload_to='incoming_message_media', null=True, blank=True)
    content_url = models.CharField(max_length=1024, null=True, blank=True)
    content_type = models.CharField(max_length=128, default='application/octet-stream')

class OutgoingCall(models.Model):
    destination = models.CharField(max_length=256)

    send_date = models.DateTimeField()
    sent_date = models.DateTimeField(null=True, blank=True)

    start_call = models.BooleanField(default=False)

    message = models.TextField(max_length=1024, null=True, blank=True)
    file = models.URLField(max_length=(1024 * 1024), null=True, blank=True)

    errored = models.BooleanField(default=False)
    transmission_metadata = JSONField(default=dict, blank=True, null=True)

    integration = models.ForeignKey(Integration, related_name='twilio_outgoing_calls', null=True, blank=True, on_delete=models.SET_NULL)

    next_action = models.CharField(max_length=64, choices=OUTGOING_CALL_NEXT_ACTIONS, default='continue')

    pause_length = models.IntegerField(default=5)

    gather_input = models.CharField(max_length=64, choices=GATHER_INPUT_OPTIONS, default='dtmf speech')
    gather_finish_on_key = models.CharField(max_length=64, default='#')
    gather_num_digits = models.IntegerField(default=4)
    gather_timeout = models.IntegerField(default=5)
    gather_speech_timeout = models.IntegerField(default=5)
    gather_speech_profanity_filter = models.BooleanField(default=False)
    gather_speech_model = models.CharField(max_length=64, choices=GATHER_SPEECH_MODELS, default='default')

    def transmit(self):
        if self.transmission_metadata is None:
            self.transmission_metadata = {}

        if self.sent_date is not None:
            raise Exception('Call (pk=' + str(self.pk) + ') already transmitted on ' + self.sent_date.isoformat() + '.')

        try:
            client = Client(self.integration.configuration['client_id'], self.integration.configuration['auth_token'])

            call = client.calls.create(
                url=(settings.SITE_URL + reverse('incoming_twilio_call')),
                to=self.destination,
                from_=self.integration.configuration['phone_number']
            )

            self.transmission_metadata['twilio_sid'] = call.sid
            self.errored = False
            self.save()
        except: # pylint: disable=bare-except
            self.errored = True

            self.transmission_metadata['error'] = traceback.format_exc().splitlines()

            self.save()

class IncomingCallResponse(models.Model):
    source = models.CharField(max_length=256)

    receive_date = models.DateTimeField()

    message = models.TextField(max_length=1024)

    transmission_metadata = JSONField(default=dict, blank=True, null=True)

    integration = models.ForeignKey(Integration, related_name='twilio_incoming_calls', null=True, blank=True, on_delete=models.SET_NULL)

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
        payload_body = smart_text(payload['Body']) # ['Body'].encode(encoding='UTF-8', errors='strict')

        integration.process_player_incoming('twilio_player', payload['From'], payload_body, {'last_message': incoming_message})

        return []

    return ['No content provided.']

def execute_action(integration, session, action):
    player = session.player

    if action['type'] == 'echo': # pylint: disable=no-else-return
        outgoing = OutgoingMessage(destination=player.player_state['twilio_player'])
        outgoing.send_date = timezone.now()
        outgoing.message = integration.translate_value(action['message'], session)
        outgoing.integration = integration

        outgoing.save()

        outgoing.transmit()

        return True
    elif action['type'] == 'echo-image':
        outgoing = OutgoingMessage(destination=player.player_state['twilio_player'])
        outgoing.send_date = timezone.now()
        outgoing.message = 'image:' + integration.translate_value(action['image-url'], session)
        outgoing.integration = integration

        outgoing.save()

        outgoing.transmit()

        return True
    elif action['type'] == 'echo-voice':
        unsent = OutgoingCall.objects.filter(destination=player.player_state['twilio_player'], sent_date=None)

        outgoing = OutgoingCall(destination=player.player_state['twilio_player'])
        outgoing.start_call = unsent.count() == 0
        outgoing.send_date = timezone.now()
        outgoing.message = integration.translate_value(action['message'], session)
        outgoing.next_action = action['next_action']

        outgoing.integration = integration

        outgoing.save()

        if outgoing.next_action != 'hangup' and outgoing.start_call is True:
            outgoing.transmit()

        return True

    return False
