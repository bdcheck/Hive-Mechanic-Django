# pylint: disable=no-member, line-too-long

import json
import logging

from django.conf import settings
from django.core.mail import EmailMessage

from simple_messaging_switchboard.models import Channel

from integrations.models import Integration

def send_via(outgoing_message):
    metadata = json.loads(outgoing_message.transmission_metadata)

    logging.error('Looking for channel for %s from %s', outgoing_message, metadata)

    integration_str = metadata.get('integration', None)

    if integration_str is not None:
        integration_pk = int(integration_str.replace('integration:', ''))

        integration_match = Integration.objects.filter(pk=integration_pk).first()

        if integration_match is not None:
            channel_identifier = integration_match.configuration.get('channel_identifier', None)

            channel = Channel.objects.filter(identifier=channel_identifier).first()

            logging.error('channel: %s', channel)

            if channel is not None:
                return channel.identifier

    logging.error('no channel found')

    return None

def process_incoming_message(message):
    integration_match = None

    for integration in Integration.objects.filter(type='simple_messaging'):
        channel_identifier = integration.configuration.get('channel_identifier', None)

        channel = Channel.objects.filter(identifier=channel_identifier).first()

        if channel is not None:
            channel_config = json.loads(channel.configuration)

            if channel_config.get('phone_number', None) == message.recipient:
                integration_match = integration

                break

    if integration_match is not None:
        transmission_metadata = {}

        try:
            transmission_metadata = json.loads(message.transmission_metadata)
        except json.JSONDecodeError:
            pass

        transmission_metadata['integration'] = 'integration:%s' % integration_match.pk

        message.transmission_metadata = json.dumps(transmission_metadata, indent=3)
        message.save()

        if 'mirror_emails' in integration_match.game.game_state:
            if settings.BUILDER_MIRROR_MESSAGES:
                if message.media.all().count() > 0 or settings.BUILDER_MIRROR_MESSAGES_REQUIRE_MEDIA is False:
                    message_body = ' -- Message Content --\n'

                    subject = '[' + integration_match.game.name + '] New SMS Message'

                    email = EmailMessage(
                        subject,
                        message_body,
                        settings.BUILDER_MIRROR_MESSAGES_FROM_ADDRESS,
                        integration_match.game.game_state['mirror_emails'],
                    )

                    for media_obj in message.media.all():
                        email.attach(media_obj.content_file.filename, media_obj.content_file.read(), media_obj.content_type)

                    email.send()

        payload = {
            'Body': message.current_message(),
            'From': message.current_sender(),
            'simple_messaging_incoming_pk': message.pk
        }

        integration_match.process_incoming(payload)
