# pylint: disable=no-member, line-too-long

import json

from django.conf import settings
from django.core.mail import EmailMessage

from integrations.models import Integration

def process_incoming_message(message):
    integration_match = None

    for integration in Integration.objects.filter(type='simple_messaging'):
        if 'phone_number' in integration.configuration and message.recipient == integration.configuration['phone_number']:
            integration_match = integration

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
                    message_body = ' -- Message Content --\nTODO'

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
