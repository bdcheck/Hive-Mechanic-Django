# pylint: disable=no-member, line-too-long
# -*- coding: utf-8 -*-

from builtins import str # pylint: disable=redefined-builtin

import json
import os

import django.views.defaults
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from filer.admin.clipboardadmin import ajax_upload
from filer.models import filemodels

from integrations.models import Integration

from .models import Game, GameVersion, InteractionCard, Player, Session, DataProcessor, SiteSettings


@login_required
def builder_home(request): # pylint: disable=unused-argument
    if request.user.has_perm('builder.builder_login') is False:
        raise PermissionDenied('View permission required.')

    context = {}

    integration_types = {}

    for integration in Integration.objects.all():
        if (integration.type in integration_types) is False:
            integration_types[integration.type] = []

        integration_types[integration.type].append(integration.fetch_statistics())

    context['integrations'] = integration_types

    return render(request, 'builder_home.html', context=context)

@login_required
def builder_activities(request): # pylint: disable=unused-argument
    if request.user.has_perm('builder.builder_login') is False:
        raise PermissionDenied('View permission required.')

    context = {}

    context['activities'] = []

    for game in Game.objects.all():
        if game.can_edit(request.user):
            context['activities'].append(game)

    return render(request, 'builder_activities.html', context=context)


@login_required
def builder_sessions(request): # pylint: disable=unused-argument
    if request.user.has_perm('builder.builder_login') is False:
        raise PermissionDenied('View permission required.')

    context = {}

    context['sessions'] = Session.objects.all()

    return render(request, 'builder_sessions.html', context=context)


@login_required
def builder_players(request): # pylint: disable=unused-argument
    if request.user.has_perm('builder.builder_login') is False:
        raise PermissionDenied('View permission required.')

    context = {}

    context['players'] = Player.objects.all()

    return render(request, 'builder_players.html', context=context)


@login_required
def builder_game(request, game): # pylint: disable=unused-argument
    if request.user.has_perm('builder.builder_login') is False:
        raise PermissionDenied('View permission required.')

    matched_game = Game.objects.filter(slug=game).first()

    if matched_game.can_view(request.user):
        context = {}

        context['game'] = matched_game

        if request.method == 'POST':
            if matched_game.can_edit(request.user):
                definition = json.loads(request.POST['definition'])

                new_version = GameVersion(game=context['game'], created=timezone.now(), definition=json.dumps(definition, indent=2))
                new_version.save()

                return HttpResponse(json.dumps({'success': True}, indent=2), content_type='application/json', status=200)

            raise PermissionDenied('Edit permission required.')

        return render(request, 'builder_js.html', context=context)

    raise PermissionDenied('View permission required.')


@login_required
def builder_game_definition_json(request, game): # pylint: disable=unused-argument
    if request.user.has_perm('builder.builder_login') is False:
        raise PermissionDenied('View permission required.')

    matched_game = Game.objects.filter(slug=game).first()

    if matched_game.can_view(request.user):
        latest = matched_game.versions.order_by('-created').first()

        if latest is None:
            latest = GameVersion(game=matched_game, created=timezone.now())

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

        response = HttpResponse(json.dumps(definition, indent=2), content_type='application/json', status=200)

        response['X-Hive-Mechanic-Editable'] = matched_game.can_edit(request.user)

        return response

    raise PermissionDenied('View permission required.')


@login_required
def builder_game_variables(request, game): # pylint: disable=unused-argument
    if request.user.has_perm('builder.builder_login') is False:
        raise PermissionDenied('View permission required.')

    matched_game = Game.objects.filter(slug=game).first()

    if matched_game.can_view(request.user):
        variables = []

        for variable_name in matched_game.game_state.keys():
            variables.append({
                'name': variable_name,
                'value': matched_game.game_state[variable_name]
            })

        response = HttpResponse(json.dumps(variables, indent=2), content_type='application/json', status=200)

        response['X-Hive-Mechanic-Editable'] = matched_game.can_edit(request.user)

        return response

    raise PermissionDenied('View permission required.')


@login_required
def builder_game_templates(request): # pylint: disable=unused-argument
    context = {}
    games = Game.objects.filter(is_template=True).order_by('name').values("name", 'slug', 'id')
    context['games'] = list(games)
    return HttpResponse(json.dumps(context, indent=2), content_type='application/json', status=200)


@login_required
def builder_interaction_card(request, card): # pylint: disable=unused-argument
    if request.user.has_perm('builder.builder_login') is False:
        raise PermissionDenied('View permission required.')

    card = get_object_or_404(InteractionCard, identifier=card)

    if card.client_implementation is not None:
        content_type = 'application/octet-stream'

        if card.client_implementation.path.endswith('.js'):
            content_type = 'application/javascript'

        response = FileResponse(open(card.client_implementation.path, 'rb'), content_type=content_type) # pylint: disable=consider-using-with
        response['Content-Length'] = os.path.getsize(card.client_implementation.path)

        return response

    raise Http404('Card implementation not found. Verify that a client implementation file is attached to the card definition.')


@login_required
def builder_add_game(request): # pylint: disable=unused-argument
    if request.user.has_perm('builder.builder_login') is False or request.user.has_perm('builder.add_game') is False:
        raise PermissionDenied('View permission required.')

    response = {
        'message': 'Unable to add game.',
        'success': False
    }

    if request.method == 'POST' and 'name' in request.POST:
        name = request.POST['name'].strip()
        template = request.POST['template'].strip()

        if name:
            slug = slugify(name)

            index = 1

            while Game.objects.filter(slug=slug).count() > 0:
                slug = slugify(name) + '-' + str(index)

                index += 1

            new_game = Game(name=name, slug=slug)
            new_game.save()

            if template and template != "none":
                old_game = Game.objects.filter(id=template).first()
                for card in old_game.cards.all():
                    new_game.cards.add(card)

                # latest version
                version = old_game.latest_version()
                version.pk = None
                version.game = new_game
                version.save()
                new_game.save()
            # default
            else:
                for card in InteractionCard.objects.filter(enabled=True):
                    new_game.cards.add(card)

                new_game.save()
            response['success'] = True
            response['message'] = 'Game added.'
            response['redirect'] = reverse('builder_game', args=[new_game.slug])

    return HttpResponse(json.dumps(response, indent=2), content_type='application/json', status=200)


@login_required
def builder_data_processor_options(request):  # pylint: disable=unused-argument
    options = []

    for processor in DataProcessor.objects.filter(enabled=True).order_by('name'):
        options.append({
            'value': processor.identifier,
            'label': {
                'en': processor.name
            }
        })

    return HttpResponse(json.dumps(options, indent=2), content_type='application/json', status=200)


@login_required
def builder_activity_delete(request, slug): # pylint: disable=unused-argument
    if request.user.has_perm('builder.delete_game') is False:
        raise PermissionDenied('Delete game permission required.')

    activity = get_object_or_404(Game, slug=slug)

    if activity.can_edit(request.user):
        activity.delete()

        return redirect('builder_activities')

    raise PermissionDenied('Delete game permission required.')


@login_required
def builder_update_icon(request):
    if request.user.has_perm('builder.builder_login') is False:
        raise PermissionDenied('View permission required.')

    if request.method == 'POST':
        activity = Game.objects.filter(pk=int(request.POST.get('activity_pk'))).first()

        if activity is not None: #  and activity.can_view(request.user):
            activity.icon = request.FILES["icon_file"]

            activity.save()

            icon_details = {
                'url': activity.icon.url
            }
            response = HttpResponse(json.dumps(icon_details, indent=2), content_type='application/json', status=200)

            response['X-Hive-Mechanic-Editable'] = activity.can_edit(request.user)

            return response

    raise PermissionDenied('View permission required.')


@login_required
def builder_media(request):
    context = {}
    page = request.GET.get('page', 1)
    media = filemodels.File.objects.order_by('-uploaded_at')
    paginator = Paginator(media, 30)

    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)

    context['media'] = media
    context['pages'] = pages
    return render(request, 'builder_media.html', context=context)

@login_required
def builder_media_upload(request):
    if request.method == 'POST':
        response = ajax_upload(request)
        res = json.loads(response.content)
        if 'error' in res:
            return redirect(django.views.defaults.HttpResponseServerError)
        description = request.POST.get("description")
        if description:
            file = filemodels.File.objects.filter(id=res["file_id"]).first()
            file.description = description
            file.save()
    return redirect('builder_media')


@login_required
def builder_settings(request): # pylint: disable=unused-argument
    if request.user.has_perm('builder.builder_login') is False:
        raise PermissionDenied('View permission required.')

    context = {}

    settings = SiteSettings.objects.all().order_by('-last_updated').first()

    now = timezone.now()

    if request.method == 'POST':
        if settings is None:
            settings = SiteSettings.objects.create(name=request.POST.get('site_name', 'Hive Mechanic'), created=now, last_updated=now)

        banner_file = request.FILES["site_banner"]

        if banner_file is not None:
            settings.banner = request.FILES["site_banner"]

        settings.name = request.POST.get('site_name', 'Hive Mechanic')
        settings.last_updated = now
        settings.save()

        response_payload = {
            'url': settings.banner.url
        }

        response = HttpResponse(json.dumps(response_payload, indent=2), content_type='application/json', status=200)

        return response

    if settings is not None:
        context['settings'] = settings

    return render(request, 'builder_settings.html', context=context)


@login_required
def builder_activity_view(request, slug): # pylint: disable=unused-argument
    if request.user.has_perm('builder.builder_login') is False:
        raise PermissionDenied('View permission required.')

    matched_activity = Game.objects.filter(slug=slug).first()

    if matched_activity.can_view(request.user):
        context = {}

        context['activity'] = matched_activity

        response = render(request, 'builder_view.html', context=context)
        response['X-Frame-Options'] = 'SAMEORIGIN'

        return response

    raise PermissionDenied('View permission required.')


@login_required
def builder_integrations(request):
    context = {}
    integration = Integration.objects.order_by("name")
    games = Game.objects.order_by("name")
    context["integrations"] = integration
    context["games"] = games
    return render(request, 'builder_integration.html', context=context)


@login_required
def builder_integrations_update(request):
    if request.method == 'POST':
        int_id = request.POST.get("integration_id")
        int_name = request.POST.get("integration_name")
        game_id = request.POST.get("game_id")
        integration = Integration.objects.get(pk=int_id)
        game = Game.objects.get(pk=game_id)
        integration.game = game
        if int_name:
            integration.name = int_name
        integration.save()
    return redirect('builder_integrations')
