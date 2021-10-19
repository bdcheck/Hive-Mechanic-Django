# pylint: disable=no-member, line-too-long

from builtins import str # pylint: disable=redefined-builtin
from builtins import range # pylint: disable=redefined-builtin

import mimetypes

from io import BytesIO

import requests


from django.conf import settings
from django.core import files
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from twilio.twiml.voice_response import VoiceResponse

from integrations.models import Integration

from .models import IncomingMessage, IncomingMessageMedia, OutgoingCall, IncomingCallResponse

@csrf_exempt
def incoming_twilio(request): # pylint: disable=too-many-branches,too-many-locals,too-many-statements
    response = '<?xml version="1.0" encoding="UTF-8" ?><Response></Response>'

    if request.method == 'POST': # pylint: disable=too-many-nested-blocks
        now = timezone.now()

        destination = request.POST['To']
        source = request.POST['From']

        incoming = IncomingMessage(source=source)
        incoming.receive_date = now
        incoming.message = request.POST['Body'].strip()
        incoming.transmission_metadata = request.POST

        integration_match = None

        for integration in Integration.objects.filter(type='twilio'):
            if 'phone_number' in integration.configuration and destination == integration.configuration['phone_number']:
                integration_match = integration

        if integration_match is not None:
            incoming.integration = integration_match

        incoming.save()

        num_media = 0

        media_objects = {}

        if 'NumMedia' in request.POST:
            num_media = int(request.POST['NumMedia'])

            for i in range(0, num_media):
                media = IncomingMessageMedia(message=incoming)

                media.content_url = request.POST['MediaUrl' + str(i)]
                media.content_type = request.POST['MediaContentType' + str(i)]
                media.index = i

                media.save()

                media_response = requests.get(media.content_url)

                if media_response.status_code != requests.codes.ok:
                    continue

                filename = media.content_url.split('/')[-1]

                extension = mimetypes.guess_extension(media.content_type)

                if extension is not None:
                    if extension == '.jpe':
                        extension = '.jpg'

                    filename += extension

                file_bytes = BytesIO()
                file_bytes.write(media_response.content)

                media.content_file.save(filename, files.File(file_bytes))
                media.save()

                media_objects[filename] = {
                    'content': file_bytes.getvalue(),
                    'mime-type': media.content_type
                }

        try:
            if integration_match is not None:
                if 'mirror_emails' in integration_match.game.game_state:
                    if settings.BUILDER_MIRROR_MESSAGES:
                        if num_media > 0 or settings.BUILDER_MIRROR_MESSAGES_REQUIRE_MEDIA is False:
                            message_body = ' -- Message Content --\n'

                            for key in request.POST:
                                value = request.POST[key]
                                message_body += key + ': ' + value + '\n'

                            subject = '[' + integration_match.game.name + '] New SMS Message'

                            email = EmailMessage(
                                subject,
                                message_body,
                                settings.BUILDER_MIRROR_MESSAGES_FROM_ADDRESS,
                                integration_match.game.game_state['mirror_emails'],
                            )

                            for filename, file_content in media_objects.items():
                                email.attach(filename, file_content['content'], file_content['mime-type'])

                            email.send()


        except AttributeError:
            pass

        if integration_match is not None:
            integration_match.process_incoming(request.POST)

    return HttpResponse(response, content_type='text/xml')

@csrf_exempt
def incoming_twilio_call(request): # pylint: disable=too-many-branches
    response = VoiceResponse()

    if request.method == 'POST':
        now = timezone.now()

        integration_match = None
        
        post_dict = request.POST.dict()

        destination = post_dict['To']
        source = post_dict['From']

        for integration in Integration.objects.filter(type='twilio'):
            if 'phone_number' in integration.configuration and (source == integration.configuration['phone_number'] or destination == integration.configuration['phone_number']):
                integration_match = integration

                if destination == integration.configuration['phone_number']:
                    destination = post_dict['From']
                    source = post_dict['To']

                    post_dict['From'] = source
                    post_dict['To'] = destination

        if 'Digits' in post_dict or 'SpeechResult' in post_dict:
            incoming = IncomingCallResponse(source=source) # TODO: Swap if this is integration number
            incoming.receive_date = now

            incoming.message = ''

            if 'Digits' in post_dict:
                incoming.message = post_dict['Digits'].strip()

            if 'SpeechResult' in post_dict:
                if incoming.message:
                    incoming.message += ' | '

                incoming.message += post_dict['SpeechResult'].strip()

            incoming.transmission_metadata = post_dict

            if integration_match is not None:
                incoming.integration = integration_match

            incoming.save()

        if integration_match is not None:
            print('INT PROCESS[1]')
            integration_match.process_incoming(post_dict)
            print('INT PROCESS[2]')

            for call in OutgoingCall.objects.filter(destination=destination, sent_date=None, send_date__lte=timezone.now(), integration=integration_match).order_by('send_date'):
                if call.message is not None and call.message != '':
                    response.say(call.message)
                elif call.file is not None and call.file != '':
                    pass

                call.sent_date = timezone.now()
                call.save()

                if call.next_action == 'pause':
                    response.pause(length=call.pause_length)
                elif call.next_action == 'gather':
                    response.gather(input=call.gather_input, speech_timeout=call.gather_speech_timeout, finish_on_key=call.gather_finish_on_key) # + more
                    break
                elif call.next_action == 'hangup':
                    response.hangup()
                    break

    return HttpResponse(str(response), content_type='text/xml')
