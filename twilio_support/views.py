# pylint: disable=no-member, line-too-long

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from twilio.twiml.voice_response import VoiceResponse

from integrations.models import Integration

from .models import IncomingMessage, OutgoingCall, IncomingCallResponse

@csrf_exempt
def incoming_twilio(request):
    response = '<?xml version="1.0" encoding="UTF-8" ?><Response></Response>'

    if request.method == 'POST':
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

        if integration_match is not None:
            integration_match.process_incoming(request.POST)

    return HttpResponse(response, content_type='text/xml')

@csrf_exempt
def incoming_twilio_call(request): # pylint: disable=too-many-branches
    response = VoiceResponse()

    if request.method == 'POST':
        now = timezone.now()

        integration_match = None

        destination = request.POST['To']
        source = request.POST['From']

        for integration in Integration.objects.filter(type='twilio'):
            if 'phone_number' in integration.configuration and source == integration.configuration['phone_number']:
                integration_match = integration

        if 'Digits' in request.POST or 'SpeechResult' in request.POST:
            incoming = IncomingCallResponse(source=source)
            incoming.receive_date = now

            incoming.message = ''

            if 'Digits' in request.POST:
                incoming.message = request.POST['Digits'].strip()

            if 'SpeechResult' in request.POST:
                if incoming.message:
                    incoming.message += ' | '

                incoming.message += request.POST['SpeechResult'].strip()

            incoming.transmission_metadata = request.POST

            if integration_match is not None:
                incoming.integration = integration_match

            incoming.save()

        if integration_match is not None:
            integration_match.process_incoming(request.POST.dict())

        for call in OutgoingCall.objects.filter(destination=destination, sent_date=None, send_date__lte=timezone.now()).order_by('send_date'):
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
