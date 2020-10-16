# pylint: disable=no-member, line-too-long
# -*- coding: utf-8 -*-

from builtins import str # pylint: disable=redefined-builtin

import json
import os

from django.http import HttpResponse, Http404, FileResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from django.contrib.admin.views.decorators import staff_member_required

from .models import Game, GameVersion, InteractionCard, Player, Session

@staff_member_required
def builder_home(request): # pylint: disable=unused-argument
    context = {}

    return render(request, 'builder_home.html', context=context)

@staff_member_required
def builder_games(request): # pylint: disable=unused-argument
    context = {}

    context['games'] = Game.objects.all()

    return render(request, 'builder_games.html', context=context)

@staff_member_required
def builder_sessions(request): # pylint: disable=unused-argument
    context = {}

    context['sessions'] = Session.objects.all()

    return render(request, 'builder_sessions.html', context=context)

@staff_member_required
def builder_players(request): # pylint: disable=unused-argument
    context = {}

    context['players'] = Player.objects.all()

    return render(request, 'builder_players.html', context=context)

@staff_member_required
def builder_game(request, game): # pylint: disable=unused-argument
    context = {}

    context['game'] = Game.objects.filter(slug=game).first()

    if request.method == 'POST':
        definition = json.loads(request.POST['definition'])

        new_version = GameVersion(game=context['game'], created=timezone.now(), definition=json.dumps(definition, indent=2))
        new_version.save()

        return HttpResponse(json.dumps({'success': True}, indent=2), content_type='application/json', status=200)

    return render(request, 'builder_js.html', context=context)

@staff_member_required
def builder_game_definition_json(request, game): # pylint: disable=unused-argument
    game = Game.objects.filter(slug=game).first()

    latest = game.versions.order_by('-created').first()

    if latest is None:
        latest = GameVersion(game=game, created=timezone.now())

        definition = [{
            'type': 'sequence',
            'id': 'new-sequence',
            'name': 'New Sequence',
            'items': [{
                "name": "Hello World",
                "context": "Start building your game here.",
                "message": "Hello World",
                "type": "send-message",
                "id": "hello-world"
            }]
        }]

        latest.definition = json.dumps(definition, indent=2)
        latest.save()

    definition = json.loads(latest.definition)

    return HttpResponse(json.dumps(definition, indent=2), content_type='application/json', status=200)

def builder_interaction_card(request, card): # pylint: disable=unused-argument
    card = get_object_or_404(InteractionCard, identifier=card)

    if card.client_implementation is not None:
        content_type = 'application/octet-stream'

        if card.client_implementation.path.endswith('.js'):
            content_type = 'application/javascript'

        response = FileResponse(open(card.client_implementation.path, 'rb'), content_type=content_type)
        response['Content-Length'] = os.path.getsize(card.client_implementation.path)

        return response

    raise Http404('Card implementation not found. Verify that a client implementation file is attached to the card definition.')

@staff_member_required
def builder_add_game(request): # pylint: disable=unused-argument
    response = {
        'message': 'Unable to add game.',
        'success': False
    }

    if request.method == 'POST' and 'name' in request.POST:
        name = request.POST['name'].strip()

        if name:
            slug = slugify(name)

            index = 1

            while Game.objects.filter(slug=slug).count() > 0:
                slug = slugify(name) + '-' + str(index)

                index += 1

            new_game = Game(name=name, slug=slug)

            new_game.save()

            for card in InteractionCard.objects.filter(enabled=True):
                new_game.cards.add(card)

            new_game.save()

            response['success'] = True
            response['message'] = 'Game added.'
            response['redirect'] = reverse('builder_game', args=[new_game.slug])

    return HttpResponse(json.dumps(response, indent=2), content_type='application/json', status=200)
