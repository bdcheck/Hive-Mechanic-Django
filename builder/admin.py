# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis import admin

from .models import Game, GameVersion, InteractionCard, Player, Session

@admin.register(Game)
class GameAdmin(admin.OSMGeoAdmin):
    list_display = ('name', 'slug',)

@admin.register(GameVersion)
class GameVersionAdmin(admin.OSMGeoAdmin):
    list_display = ('game', 'created',)

@admin.register(InteractionCard)
class InteractionCardAdmin(admin.OSMGeoAdmin):
    list_display = ('name', 'identifier', 'enabled',)

    fieldsets = (
        (None, {
            'fields': ('name', 'identifier', 'endabled')
        }),
        ('Server Implementaion', {
            'fields': ('entry_actions', 'evaluate_function'),
        }),
    )

@admin.register(Player)
class PlayerAdmin(admin.OSMGeoAdmin):
    list_display = ('identifier',)

@admin.register(Session)
class SessionAdmin(admin.OSMGeoAdmin):
    list_display = ('player', 'game_version', 'started', 'completed')
