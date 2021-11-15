# pylint: disable=no-member, line-too-long

from builtins import str # pylint: disable=redefined-builtin
import json
import re

from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.urls import reverse

from passive_data_kit.models import DataPoint

from builder.models import Player
from integrations.models import Integration

from .models import ApiClient

def valid_client(handle):
    def wrapper(request, *args, **options):
        token = request.GET.get('token', request.POST.get('token', None))

        if token is None:
            return HttpResponseForbidden('No API token provided.')

        client = ApiClient.objects.filter(shared_secret=token).first()

        if client is None:
            return HttpResponseForbidden('Invalid API token provided.')

        now = timezone.now()

        if client.start_date is not None and now < client.start_date:
            return HttpResponseForbidden('Inactive API token provided.')

        if client.end_date is not None and now > client.end_date:
            return HttpResponseForbidden('Expired API token provided.')

        options['integration'] = client.integration

        return handle(request, *args, **options)

    return wrapper


@csrf_exempt
@valid_client
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

                point = DataPoint.objects.create_data_point('hive-http-get', session.player.identifier, dict(request.GET), user_agent='Hive Mechanic Client Library')

        response['game'] = payload

    elif request.method == 'POST':
        player = request.POST.get('player', 'unknown-player')
        
        point = DataPoint.objects.create_data_point('hive-http-post', player, dict(request.POST), user_agent='Hive Mechanic Client Library')

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

    if request.method == 'GET': # pylint: disable=too-many-nested-blocks
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


@csrf_exempt
@valid_client
def incoming_http_commands(request, *args, **options): # pylint: disable=unused-argument
    commands_str = request.POST.get('commands', request.GET.get('commands', '[]'))

    commands = None

    try:
        commands = json.loads(commands_str)
    except ValueError:
        return HttpResponseBadRequest('Invalid JSON provided for "commands" parameter: "' + str(commands_str) + '".')

    if commands is None:
        return HttpResponseBadRequest('No JSON provided for "commands" parameter.')

    player = request.POST.get('player', request.GET.get('player', None))

    issues = options['integration'].process_incoming({
        'player': player,
        'commands': commands,
    })

    response = {
        'success': True,
    }

    status_code = 200

    if issues:
        response['success'] = False
        response['issues'] = issues

        status_code = 400

    return HttpResponse(json.dumps(response, indent=2), content_type='application/json', status=status_code)

@csrf_exempt
@valid_client
def incoming_http_fetch(request, *args, **options): # pylint: disable=unused-argument
    name = request.POST.get('name', request.GET.get('name', None))
    scope = request.POST.get('scope', request.GET.get('scope', None))
    player = request.POST.get('player', request.GET.get('player', None))

    issues = []

    response = {
        'success': True,
    }

    if scope == 'player':
        match = Player.objects.filter(identifier=player).first()

        if player is not None:
            response['value'] = match.fetch_variable(name)
        else:
            response['value'] = None
            issues.append('Player not found.')
    elif scope == 'session':
        response['value'] = 'todo: implement scope lookup'
    else:
        response['value'] = options['integration'].game.fetch_variable(name)

    status_code = 200

    if issues:
        response['success'] = False
        response['issues'] = issues

        status_code = 400

    return HttpResponse(json.dumps(response, indent=2), content_type='application/json', status=status_code)
