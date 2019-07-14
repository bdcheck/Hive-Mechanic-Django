# pylint: disable=no-member, line-too-long

import time

from django.core.management import call_command
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from django_dialog_engine.models import Dialog

from integration.models import Integration

from .models import IncomingMessage, process_response

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
            if 'twilio_phone_numbers' in integration.configuration and (destination in integration.configuration['twilio_phone_numbers']):
                integration_match = integration
                
        if integration_match is not None:
            incoming.integration = integration_match

        incoming.save()
        
        if integration_match is not None:
            integration_match.process_incoming(request.POST)

    return HttpResponse(response, content_type='text/xml')