# pylint: disable=no-member, line-too-long

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from integrations.models import Integration

from .models import IncomingMessage

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
