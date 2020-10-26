# -*- coding: utf-8 -*-


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
    list_display = ('name', 'identifier', 'enabled', 'issues',)

    fieldsets = (
        (None, {
            'fields': ('name', 'identifier', 'enabled')
        }),
        ('Server Implementaion', {
            'fields': ('entry_actions', 'evaluate_function'),
        }),
        ('Client Implementaion', {
            'fields': ('client_implementation',),
        }),
    )

@admin.register(Player)
class PlayerAdmin(admin.OSMGeoAdmin):
    list_display = ('identifier',)

@admin.register(Session)
class SessionAdmin(admin.OSMGeoAdmin):
    list_display = ('player', 'game_version', 'started', 'completed')
