# pylint: disable=no-member,line-too-long,fixme

import json

import requests

from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.encoding import smart_str

from simple_messaging.models import OutgoingMessage, OutgoingMessageMedia, IncomingMessage

from integrations.models import Integration

class SimpleMessagingHiveException(Exception):
    pass

def process_incoming(integration, immutable_payload): # pylint: disable=too-many-branches
    payload = {}

    for key in immutable_payload.keys():
        payload[key] = immutable_payload.get(key, None)

    if ('Body' in payload) is False:
        raise SimpleMessagingHiveException('Phone call payloads not supported in Simple Messaging.')

    if 'CallStatus' in payload:
        raise SimpleMessagingHiveException('Phone call payloads not supported in Simple Messaging.')

    phone_number = payload['From']

    last_message = None

    existing_pk = payload.get('simple_messagging_incoming_pk', None)

    incoming_message = None

    if existing_pk is not None:
        incoming_message = IncomingMessage.objects.filter(pk=existing_pk).first()

    if incoming_message is None:
        # TODO encrypted lookups
        incoming_message = IncomingMessage.objects.filter(sender=phone_number).order_by('-receive_date').first()

    if incoming_message is not None:
        last_message = {
            'message': incoming_message.message,
            'received': incoming_message.receive_date,
            'raw_object': incoming_message
        }

    if payload['Body'] or incoming_message.media.count() > 0: # May require revision if voice recordings come in...
        payload_body = smart_str(payload['Body'])

        if payload_body == '':
            payload_body = None

        if payload_body is None and incoming_message.media.count() > 0:
            payload_body = '^^^'

        integration.process_player_incoming('messaging_player', phone_number, payload_body, {
            'last_message': last_message,
            'message_type': 'text',
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
            destinations.append(player.player_state['messaging_player'])

        for destination in destinations:
            outgoing = OutgoingMessage(destination=destination)
            outgoing.send_date = timezone.now()
            outgoing.message = integration.translate_value(action['message'], session)

            transmission_metadata = {
                'integration': 'integration:%s' % integration.pk
            }

            if integration.enabled is False:
                outgoing.sent_date = timezone.now()
                transmission_metadata['error'] = 'Unable to send, integration is disabled.'

            outgoing.transmission_metadata = transmission_metadata

            outgoing.save()

            if integration.enabled:
                outgoing.transmit()

        return True
    elif action['type'] == 'echo-image':
        outgoing = OutgoingMessage(destination=player.player_state['simple_messaging'])
        outgoing.send_date = timezone.now()
        outgoing.save()

        media = OutgoingMessageMedia.objects.create(message=outgoing)

        response = requests.get(integration.translate_value(action['image-url'], session), timeout=60)

        media.content_type = response.headers['content-type']
        media.content_file.save('media_%s.%s' % (media.pk, media.content_type.split('/')[-1]), ContentFile(response.content))

        transmission_metadata = {
            'integration': 'integration:%s' % integration.pk
        }

        if integration.enabled is False:
            outgoing.sent_date = timezone.now()
            transmission_metadata['error'] = 'Unable to send, integration is disabled.'

        outgoing.transmission_metadata = transmission_metadata

        outgoing.save()

        if integration.enabled:
            outgoing.transmit()

        return True

    return False

def last_message_for_player(game, player):
    integration = Integration.objects.filter(game=game).first()

    phone = player.player_state.get('simple_messaging', None)

    incoming_message = IncomingMessage.objects.filter(source=phone, integration=integration).order_by('-receive_date').first()

    last_incoming = None

    transmission_metadata = {}

    try:
        transmission_metadata = json.loads(incoming_message.transmission_metadata)
    except json.JSONDecodeError:
        pass

    if incoming_message is not None:
        last_incoming = {
            'message': incoming_message.message,
            'received': incoming_message.receive_date,
            'type': 'sms-text-message',
            'metadata': transmission_metadata,
        }

    return last_incoming

def annotate_statistics(integration, statistics): # pylint: disable=unused-argument
    pass
