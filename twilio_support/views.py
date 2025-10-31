# pylint: disable=no-member, line-too-long, no-member

import datetime
import logging
import mimetypes
import time

from io import BytesIO

import requests

from django.conf import settings
from django.core import files
from django.core.mail import EmailMessage
from django.core.management import call_command
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils import timezone
from twilio.twiml.voice_response import VoiceResponse, Gather

from activity_logger.models import log
from integrations.models import Integration

from .models import IncomingMessage, IncomingMessageMedia, OutgoingCall, IncomingCallResponse, IncomingCallMedia

logger = logging.getLogger(__name__)

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

                media_response = requests.get(media.content_url, timeout=120)

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
def incoming_twilio_call(request): # pylint: disable=too-many-branches, too-many-statements, too-many-locals
    response = VoiceResponse()

    if request.method == 'POST': # pylint: disable=too-many-nested-blocks
        now = timezone.now() - datetime.timedelta(seconds=20)

        integration_match = None

        post_dict = request.POST.dict()

        logger.error('post_dict[1]: %s', post_dict)

        source = post_dict['From']
        destination = post_dict['To']

        for integration in Integration.objects.filter(type='twilio'):
            if 'phone_number' in integration.configuration and (source == integration.configuration['phone_number'] or destination == integration.configuration['phone_number']):
                integration_match = integration

                if source == integration.configuration['phone_number']:
                    destination = post_dict['From']
                    source = post_dict['To']

                    post_dict['From'] = source
                    post_dict['To'] = destination

        logger.error('post_dict[2]: %s', post_dict)

        if post_dict.get('CallStatus', None) is not None:
            incoming = IncomingCallResponse(source=source)
            incoming.receive_date = now

            incoming.message = ''

            if post_dict.get('RecordingUrl', None) is not None:
                post_dict['Digits'] = '#'

            if 'Digits' in post_dict:
                incoming.message = post_dict['Digits'].strip()

            if 'SpeechResult' in post_dict:
                if incoming.message:
                    incoming.message += ' | '

                incoming.message += post_dict['SpeechResult'].strip()

            incoming.transmission_metadata = post_dict

            if integration_match is not None:
                incoming.integration = integration_match

            if incoming.message.strip() == '':
                incoming.message = None

            incoming.save()

            if post_dict.get('RecordingUrl', None) is not None:
                media = IncomingCallMedia(call=incoming)

                media.content_url = '%s.mp3' % post_dict.get('RecordingUrl')

                media.index = 0

                media.save()

                attempts = 5

                while attempts > 0:
                    time.sleep(1)

                    attempts -= 1

                    media_response = requests.get(media.content_url, timeout=120)

                    media.content_type = media_response.headers['content-type']

                    if media_response.status_code == requests.codes.ok:
                        filename = media.content_url.split('/')[-1]

                        file_bytes = BytesIO()
                        file_bytes.write(media_response.content)

                        media.content_file.save(filename, files.File(file_bytes))
                        media.save()

                        log_metadata = {}

                        log_metadata['phone_number'] = post_dict.get('To', None)
                        log_metadata['phone_number'] = post_dict.get('To', None)
                        log_metadata['direction'] = post_dict.get('Direction', None)
                        log_metadata['call_status'] = post_dict.get('CallStatus', None)

                        call_command('nudge_active_sessions')

                        break

        if integration_match is not None:
            integration_match.process_incoming(request.POST)

            if post_dict.get('CallStatus', None) == 'completed':
                OutgoingCall.objects.filter(destination=source, sent_date=None, integration=integration_match).delete()

                integration_match.close_sessions(post_dict)
            else:
                # If response empty - clear out pending outgoing call objects
                # Reset position in dialog to Voice Start Card

                if (post_dict.get('RecordingUrl', None) is None) and (post_dict.get('Digits', None) is None):
                    OutgoingCall.objects.filter(destination=source, sent_date=None, send_date__lte=now, integration=integration_match).update(sent_date=now)

                now = timezone.now()

                # pending_calls = OutgoingCall.objects.filter(destination=source, sent_date=None, send_date__lte=now, integration=integration_match).order_by('send_date')
                pending_calls = OutgoingCall.objects.filter(destination=source, sent_date=None, integration=integration_match).order_by('send_date')

                while pending_calls.count() > 0:
                    do_nudge = True

                    for call in pending_calls:
                        if call.next_action != 'gather':
                            if call.message is not None and call.message != '':
                                if call.message.lower().startswith('http://') or call.message.lower().startswith('https://'):
                                    response.play(call.message.replace('\n', ' ').replace('\r', ' ').split(' ')[0])
                                else:
                                    response.say(call.message)
                            elif call.file is not None and call.file != '':
                                pass

                        call.sent_date = timezone.now()
                        call.save()

                        if call.next_action == 'pause':
                            response.pause(length=call.pause_length)
                        elif call.next_action == 'gather':
                            do_nudge = False

                            args = {
                                'input': call.gather_input,
                                'barge_in': True,
                                'num_digits': 1,
                                'action_on_empty_result': True
                            }

                            if call.gather_timeout is not None:
                                args['timeout'] = call.gather_timeout

                            # if call.gather_num_digits is not None:
                            #    args['num_digits'] = call.gather_num_digits

                            if call.gather_speech_timeout is not None:
                                args['speech_timeout'] = call.gather_speech_timeout

                            if call.gather_speech_model is not None:
                                args['speech_model'] = call.gather_speech_model

                            gather = Gather(**args)

                            if call.message is not None and call.message != '':
                                if call.message.lower().startswith('http://') or call.message.lower().startswith('https://'):
                                    gather.play(call.message.replace('\n', ' ').replace('\r', ' ').split(' ')[0], loop=call.gather_loop)
                                else:
                                    gather.say(call.message, loop=call.gather_loop)
                            elif call.file is not None and call.file != '':
                                pass

                            response.append(gather)

                            break
                        elif call.next_action == 'record':
                            do_nudge = False

                            args = {
                                'action': '%s%s' % (settings.SITE_URL, reverse('incoming_twilio_call')),
                                'timeout': 10,
                            }

                            response.record(**args)

                            break
                        elif call.next_action == 'hangup':
                            do_nudge = False

                            response.hangup()
                            break

                    if do_nudge:
                        pending_calls = OutgoingCall.objects.filter(destination=source, sent_date=None, integration=integration_match).order_by('send_date')

                        call_command('nudge_active_sessions')
                    else:
                        break

                if len(response.verbs) == 0: # pylint: disable=len-as-condition
                    log_metadata = {}

                    log_metadata['phone_number'] = post_dict.get('To', None)
                    log_metadata['direction'] = post_dict.get('Direction', None)
                    log_metadata['call_status'] = post_dict.get('CallStatus', None)

                    log('twilio:incoming_twilio_call', 'Sending empty voice response back to Twilio. (Tip: verify that you are not stuck on a process response or other card awaiting user input.)', tags=['twilio', 'voice', 'warning'], metadata=log_metadata)

    logger.error('response[2]: %s', response)

    return HttpResponse(str(response), content_type='text/xml')
