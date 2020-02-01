# pylint: disable=no-member, line-too-long

import json

from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from builder.models import Game
from integrations.models import Integration

@csrf_exempt
def incoming_http(request, game_slug, slug):
    issues = None

    game = Game.objects.filter(slug=game_slug).first()

    integration_match = Integration.objects.filter(type='http', url_slug=slug, game=game).first()

    if game is not None and integration_match is not None:
        if request.method == 'POST':
            issues = integration_match.process_incoming(request.POST)
        elif request.method == 'GET':
            issues = integration_match.process_incoming(request.GET)
        else:
            issues = ['Unsupported HTTP verb: ' + request.method + '.']
    else:
        raise Http404("Activity not found.")

    response = {
        'success': True
    }

    status_code = 200

    if issues:
        response['success'] = False
        response['issues'] = issues

        status_code = 500

    return HttpResponse(json.dumps(response, indent=2), content_type='application/json', status=status_code)
