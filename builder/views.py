# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from django.contrib.admin.views.decorators import staff_member_required

from .models import Game, GameVersion

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
