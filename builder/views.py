# pylint: disable=no-member, line-too-long
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os

from django.http import HttpResponse, Http404, FileResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from django.contrib.admin.views.decorators import staff_member_required

from .models import Game, GameVersion, InteractionCard

@staff_member_required
def builder_home(request): # pylint: disable=unused-argument
    context = {}

    return render(request, 'builder_js.html', context=context)

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
