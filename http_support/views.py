# pylint: disable=no-member, line-too-long

import json
import re

from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from builder.models import Game
from integrations.models import Integration

@csrf_exempt
def incoming_http(request, slug):
    issues = None

    response = {
        'success': True,
    }

    integration_match = Integration.objects.filter(type='http', url_slug=slug).first()

    if integration_match is None:
        raise Http404("Activity not found.")

    if request.method == 'GET':
        payload = {}

        updated = False

        for key in request.GET:
            integration_match.game.game_state[key] = request.GET.get(key)
        
            updated = True
        
        if updated:
            integration_match.game.save()

        payload['variables'] = integration_match.game.game_state

        payload['sessions'] = []

        for version in integration_match.game.versions.order_by('-created').all():
            for session in version.sessions.order_by('-started').all():
                session_def = {}

                session_def['game_version'] = version.created.isoformat()

                session_def['variables'] = session.session_state
                session_def['started'] = session.started.isoformat()

                session_def['completed'] = None
                session_def['active'] = True

                if session.completed is not None:
                    session_def['completed'] = session.completed.isoformat()
                    session_def['active'] = False

                session_def['player'] = {}
                session_def['player']['identifier'] = session.player.identifier
                session_def['player']['variables'] = session.player.player_state
                session_def['player']['api_url'] = settings.SITE_URL + reverse('incoming_http_player', args=[slug, session.player.identifier])

                payload['sessions'].append(session_def)
                
        response['game'] = payload

    elif request.method == 'POST':
        issues = integration_match.process_incoming(request.POST)
    else:
        issues = ['Unsupported HTTP verb: ' + request.method + '.']

    status_code = 200

    if issues:
        response['success'] = False
        response['issues'] = issues

        status_code = 500

    return HttpResponse(json.dumps(response, indent=2), content_type='application/json', status=status_code)

@csrf_exempt
def incoming_http_player(request, slug, player):
    issues = None

    response = {
        'success': True,
    }

    integration_match = Integration.objects.filter(type='http', url_slug=slug).first()

    if integration_match is None:
        raise Http404("Activity not found.")

    if request.method == 'GET':
        players = []
        seen_players = {}

        for version in integration_match.game.versions.order_by('-created').all():
            for session in version.sessions.order_by('-started').all():
                if (session.player.identifier in seen_players) is False and (player == session.player.identifier or re.search(player, session.player.identifier) is not None):
                    if (session.player.identifier in seen_players) is False:
                        updated = False

                        for key in request.GET:
                            session.player.player_state[key] = request.GET.get(key)
                            
                            updated = True
                            
                        if updated:
                            session.player.save()
                            
                        seen_players[session.player.identifier] = {}
                        seen_players[session.player.identifier]['identifier'] = session.player.identifier
                        seen_players[session.player.identifier]['variables'] = session.player.player_state
                        seen_players[session.player.identifier]['sessions'] = []
                        seen_players[session.player.identifier]['api_url'] = settings.SITE_URL + reverse('incoming_http_player', args=[slug, session.player.identifier])

                        players.append(seen_players[session.player.identifier])

                    session_def = {}

                    session_def['game_version'] = version.created.isoformat()

                    session_def['variables'] = session.session_state
                    session_def['started'] = session.started.isoformat()

                    session_def['completed'] = None
                    session_def['active'] = True

                    if session.completed is not None:
                        session_def['completed'] = session.completed.isoformat()
                        session_def['active'] = False
                        
                    seen_players[session.player.identifier]['sessions'].append(session_def)
                    
        response['players'] = players
        
        response['game'] = {}
        response['game']['variables'] = integration_match.game.game_state

    elif request.method == 'POST':
        issues = integration_match.process_incoming(request.POST)
    else:
        issues = ['Unsupported HTTP verb: ' + request.method + '.']

    status_code = 200

    if issues:
        response['success'] = False
        response['issues'] = issues

        status_code = 500

    return HttpResponse(json.dumps(response, indent=2), content_type='application/json', status=status_code)
