# pylint: disable=line-too-long, no-member, wrong-import-order, wrong-import-position
# -*- coding: utf-8 -*-

from builtins import str # pylint: disable=redefined-builtin

import datetime
import time
import traceback

import six
import sys

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import smart_str

if sys.version_info[0] > 2:
    from django.db.models import JSONField # pylint: disable=no-name-in-module
else:
    from django.contrib.postgres.fields import JSONField

from activity_logger.models import log
from builder.models import Player
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

def last_message_for_player(game, player):
    integration = Integration.objects.filter(game=game).first()

    phone = player.player_state.get('twilio_player', None)

    incoming_message = IncomingMessage.objects.filter(source=phone, integration=integration).order_by('-receive_date').first()

    last_incoming = None

    if incoming_message is not None:
        last_incoming = {
            'message': incoming_message.message,
            'received': incoming_message.receive_date,
            'type': 'sms-text-message',
            'metadata': incoming_message.transmission_metadata,
        }

        for media_item in incoming_message.media.all():
            if media_item.content_type.lower().startswith('image/'):
                last_incoming['image_path'] = media_item.content_file.path

    incoming_call_response = IncomingCallResponse.objects.filter(source=phone, integration=integration).order_by('-receive_date').first()

    if incoming_call_response is None:
        incoming_call_response = IncomingCallResponse.objects.filter(transmission_metadata__To=phone, integration=integration).order_by('-receive_date').first()

    if incoming_call_response is not None:
        if last_incoming is None or incoming_call_response.receive_date > last_incoming['received']:
            last_incoming = {
                'message': incoming_call_response.message,
                'received': incoming_call_response.receive_date,
                'type': 'phone-call',
                'metadata': incoming_call_response.transmission_metadata,
            }

    return last_incoming

def annotate_statistics(integration, statistics):
    statistics['type'] = 'Twilio Phone Number'

    if 'phone_number' in integration.configuration:
        phone_number = integration.configuration['phone_number']

        statistics['details'].append(['Phone Number', phone_number])

    today = timezone.now() - datetime.timedelta(days=1)
    week = timezone.now() - datetime.timedelta(days=7)

    all_count = OutgoingMessage.objects.filter(integration=integration, errored=False).count() + IncomingMessage.objects.filter(integration=integration).count()

    statistics['details'].append(['Message Count (All)', all_count])

    week_count = OutgoingMessage.objects.filter(integration=integration, sent_date__gte=week, errored=False).count() + IncomingMessage.objects.filter(integration=integration, receive_date__gte=week).count()

    statistics['details'].append(['Message Count (Last 7 Days)', week_count])

    today_count = OutgoingMessage.objects.filter(integration=integration, sent_date__gte=today, errored=False).count() + IncomingMessage.objects.filter(integration=integration, receive_date__gte=today).count()

    statistics['details'].append(['Message Count (Last 24 Hours)', today_count])

    recent_out = OutgoingMessage.objects.filter(integration=integration, errored=False).order_by('-sent_date').first()

    if recent_out is not None:
        statistics['details'].append(['Most Recent Sent', recent_out.sent_date])
    else:
        statistics['details'].append(['Most Recent Sent', 'No messages sent yet'])

    recent_in = IncomingMessage.objects.filter(integration=integration).order_by('-receive_date').first()

    if recent_in is not None:
        statistics['details'].append(['Most Recent Received', recent_in.receive_date])
    else:
        statistics['details'].append(['Most Recent Received', 'No messages received yet'])


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

        except TwilioRestException as twilio_exc:
            if 'unsubscribed' in twilio_exc.msg:
                OutgoingMessage.objects.filter(sent_date=None, destination=self.destination).delete()

                player_id = 'twilio_player:%s' % self.destination

                player = Player.objects.filter(identifier=player_id).first()

                if player is not None:
                    tags = ['twilio', 'warning', 'messaging']

                    log('integration:%s' % self.integration.pk, 'Attempted to send to player who sent STOP to a phone number.', tags=tags, player=player)

                    for session in player.sessions.filter(completed=None):
                        session.complete()

            self.errored = True

            self.transmission_metadata['error'] = traceback.format_exc().splitlines()

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

class OutgoingCall(models.Model): # pylint: disable=too-many-instance-attributes
    destination = models.CharField(max_length=256)

    send_date = models.DateTimeField()
    sent_date = models.DateTimeField(null=True, blank=True)

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
    gather_speech_model = models.CharField(max_length=64, choices=GATHER_SPEECH_MODELS, default='default')
    gather_loop = models.IntegerField(default=1)

    def transmit(self):
        if self.transmission_metadata is None:
            self.transmission_metadata = {}

        if self.sent_date is not None:
            raise Exception('Call (pk=' + str(self.pk) + ') already transmitted on ' + self.sent_date.isoformat() + '.')

        try:
            client = Client(self.integration.configuration['client_id'], self.integration.configuration['auth_token'])

            ongoing = False

            incoming_call_records = client.calls.list(to=self.destination, limit=1)

            for call_record in incoming_call_records:
                if call_record.status in ('ringing', 'in-progress', 'queued'):
                    ongoing = True

            outgoing_call_records = client.calls.list(from_=self.destination, limit=1)

            for call_record in outgoing_call_records:
                if call_record.status in ('ringing', 'in-progress', 'queued'):
                    ongoing = True

            if ongoing is False:
                call = client.calls.create(
                    url=(settings.SITE_URL + reverse('incoming_twilio_call')),
                    to=self.destination,
                    from_=self.integration.configuration['phone_number']
                )

                time.sleep(3)

                self.transmission_metadata['twilio_sid'] = call.sid

                # self.sent_date = timezone.now()

                self.errored = False
                self.save()

        except: # pylint: disable=bare-except
            self.errored = True

            self.transmission_metadata['error'] = traceback.format_exc().splitlines()

            self.save()

class IncomingCallResponse(models.Model):
    source = models.CharField(max_length=256)

    receive_date = models.DateTimeField()

    message = models.TextField(max_length=1024, null=True, blank=True)

    transmission_metadata = JSONField(default=dict, blank=True, null=True)

    integration = models.ForeignKey(Integration, related_name='twilio_incoming_calls', null=True, blank=True, on_delete=models.SET_NULL)

class IncomingCallMedia(models.Model):
    call = models.ForeignKey(IncomingCallResponse, related_name='media', on_delete=models.CASCADE)

    index = models.IntegerField(default=0)

    content_file = models.FileField(upload_to='incoming_call_media', null=True, blank=True)
    content_url = models.CharField(max_length=1024, null=True, blank=True)
    content_type = models.CharField(max_length=128, default='application/octet-stream')

def process_incoming(integration, immutable_payload): # pylint: disable=too-many-branches
    payload = {}

    for key in immutable_payload.keys():
        payload[key] = immutable_payload.get(key, None)

    message_type = 'text'

    player_identifier = None

    if ('Body' in payload) is False:
        if 'Digits' in payload:
            payload['Body'] = payload['Digits']
        elif 'SpeechResult' in payload:
            payload['Body'] = payload['SpeechResult']
        else:
            payload['Body'] = ''

    if 'CallStatus' in payload:
        if 'phone_number' in integration.configuration:
            if payload['From'] == integration.configuration['phone_number']:
                player_identifier = payload['To']
            else:
                player_identifier = payload['From']
        else:
            six.raise_from(RuntimeError('Twilio integration is missing phone number.'), None)

        message_type = 'call'
    else:
        message_type = 'text'

        player_identifier = payload['From']

    last_message = None

    incoming_message = IncomingMessage.objects.filter(source=player_identifier).order_by('-receive_date').first()

    incoming_call = IncomingCallResponse.objects.filter(source=player_identifier).order_by('-receive_date').first()

    if incoming_message is None or (incoming_call is not None and incoming_call.receive_date > incoming_message.receive_date):
        incoming_message = incoming_call

    if incoming_message is not None:
        last_message = {
            'message': incoming_message.message,
            'received': incoming_message.receive_date,
            'raw_object': incoming_message
        }

    if ('CallStatus' in payload) or payload['Body'] or incoming_message.media.count() > 0: # May require revision if voice recordings come in...
        payload_body = smart_str(payload['Body'])

        if payload_body == '':
            payload_body = None

        if payload_body is None and ('CallStatus' in payload) is False and incoming_message.media.count() > 0:
            payload_body = '^^^'

        integration.process_player_incoming('twilio_player', player_identifier, payload_body, {
            'last_message': last_message,
            'message_type': message_type,
            'payload': payload,
        })

        return []

    return ['No content provided.']

def execute_action(integration, session, action): # pylint: disable=too-many-branches, too-many-statements
    player = session.player

    if action['type'] == 'echo': # pylint: disable=no-else-return
        destinations = []

        if action.get('destinations', '') != '':
            for destination in action.get('destinations', '').split('\n'):
                if len(destination) >= 10:
                    destinations.append(integration.translate_value(destination, session))
        else:
            destinations.append(player.player_state['twilio_player'])

        for destination in destinations:
            outgoing = OutgoingMessage(destination=destination)
            outgoing.send_date = timezone.now()
            outgoing.message = integration.translate_value(action['message'], session)
            outgoing.integration = integration

            if integration.enabled is False:
                outgoing.sent_date = timezone.now()
                outgoing.transmission_metadata = {
                    'error': 'Unable to send, integration is disabled.'
                }

            outgoing.save()

            if integration.enabled:
                outgoing.transmit()

        return True
    elif action['type'] == 'echo-image':
        outgoing = OutgoingMessage(destination=player.player_state['twilio_player'])
        outgoing.send_date = timezone.now()
        outgoing.message = 'image:' + integration.translate_value(action['image-url'], session)
        outgoing.integration = integration

        if integration.enabled is False:
            outgoing.sent_date = timezone.now()
            outgoing.transmission_metadata = {
                'error': 'Unable to send, integration is disabled.'
            }

        outgoing.save()

        if integration.enabled:
            outgoing.transmit()

        return True
    elif action['type'] == 'echo-voice':
        outgoing = OutgoingCall(destination=player.player_state['twilio_player'])

        outgoing.send_date = timezone.now()
        outgoing.message = integration.translate_value(action['message'], session)
        outgoing.next_action = action['next_action']
        outgoing.integration = integration

        if 'parameters' in action:
            if 'speech_model' in action['parameters']:
                outgoing.gather_speech_model = action['parameters']['speech_model']

            if 'speech_timeout' in action['parameters']:
                outgoing.gather_speech_timeout = action['parameters']['speech_timeout']

            if 'timeout' in action['parameters']:
                outgoing.gather_timeout = action['parameters']['timeout']

            if 'loop' in action['parameters']:
                outgoing.gather_loop = int(action['parameters']['loop'])

            if 'input_method' in action['parameters']:
                outgoing.gather_input = action['parameters']['input_method']

                if outgoing.gather_input == 'dtmf_speech':
                    outgoing.gather_input = 'dtmf speech' # For legacy cards...

            if 'pause' in action['parameters']:
                outgoing.pause_length = action['parameters']['pause']

            if outgoing.gather_timeout == '':
                outgoing.gather_timeout = 5

            if outgoing.gather_loop == '':
                outgoing.gather_loop = 1

            if outgoing.pause_length == '':
                outgoing.pause_length = 30

        if integration.enabled is False:
            outgoing.transmission_metadata = {
                'error': 'Unable to send, integration is disabled.'
            }

        outgoing.save()

        if integration.enabled:
            outgoing.transmit()

        return True

    return False

def close_sessions(integration, payload): # pylint: disable=too-many-branches
    player_identifier = None

    if 'CallStatus' in payload:
        if 'phone_number' in integration.configuration:
            if payload['From'] == integration.configuration['phone_number']:
                player_identifier = payload['To']
            else:
                player_identifier = payload['From']
        else:
            six.raise_from(RuntimeError('Twilio integration is missing phone number.'), None)

    if player_identifier is not None:
        integration.close_player_sessions('twilio_player', player_identifier)
