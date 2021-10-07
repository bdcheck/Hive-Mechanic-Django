# pylint: disable=line-too-long
# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.gis import admin

from .models import Game, GameVersion, InteractionCard, Player, Session, RemoteRepository, DataProcessor

@admin.register(Game)
class GameAdmin(admin.OSMGeoAdmin):
    list_display = ('name', 'slug',)

@admin.register(GameVersion)
class GameVersionAdmin(admin.OSMGeoAdmin):
    list_display = ('game', 'created',)

@admin.register(InteractionCard)
class InteractionCardAdmin(admin.OSMGeoAdmin):
    list_display = ('name', 'identifier', 'enabled', 'version', 'issues', 'available_update',)

    fieldsets = (
        (None, {
            'fields': ('name', 'identifier', 'enabled', 'version',)
        }),
        ('Server Implementaion', {
            'fields': ('entry_actions', 'evaluate_function'),
        }),
        ('Client Implementaion', {
            'fields': ('client_implementation',),
        }),
        ('Miscellaneous', {
            'fields': ('repository_definition',),
        }),
    )

    actions = ['update_interaction_card', 'refresh_interaction_card', 'enable_interaction_card', 'disable_interaction_card']

    def update_interaction_card(self, request, queryset):
        add_messages = []

        for card in queryset:
            add_messages.extend(card.update_card())

        for message in add_messages:
            if '[Success]' in message:
                self.message_user(request, message, messages.SUCCESS)
            else:
                self.message_user(request, message, messages.ERROR)

    update_interaction_card.short_description = "Install updated versions"

    def refresh_interaction_card(self, request, queryset):
        add_messages = []

        for card in queryset:
            add_messages.extend(card.refresh_card())

        for message in add_messages:
            if '[Success]' in message:
                self.message_user(request, message, messages.SUCCESS)
            else:
                self.message_user(request, message, messages.ERROR)

    refresh_interaction_card.short_description = "Refresh selected cards"

    def enable_interaction_card(self, request, queryset):
        queryset.update(enabled=True)

        self.message_user(request, str(queryset.count()) + ' card(s) enabled.')

    enable_interaction_card.short_description = "Enable selected cards"

    def disable_interaction_card(self, request, queryset):
        queryset.update(enabled=False)

        self.message_user(request, str(queryset.count()) + ' card(s) disabled.')

    disable_interaction_card.short_description = "Disable selected cards"

@admin.register(Player)
class PlayerAdmin(admin.OSMGeoAdmin):
    list_display = ('identifier',)

@admin.register(Session)
class SessionAdmin(admin.OSMGeoAdmin):
    list_display = ('player', 'game_version', 'started', 'completed')

@admin.register(RemoteRepository)
class RemoteRepositoryAdmin(admin.OSMGeoAdmin):
    list_display = ('name', 'url', 'priority', 'last_updated')

@admin.register(DataProcessor)
class DataProcessorAdmin(admin.OSMGeoAdmin):
    list_display = ('name', 'identifier', 'enabled', 'version', 'issues', 'available_update',)

    fieldsets = (
        (None, {
            'fields': ('name', 'identifier', 'enabled', 'version',)
        }),
        ('Implementaion', {
            'fields': ('processor_function',),
        }),
        ('Miscellaneous', {
            'fields': ('repository_definition', 'metadata',),
        }),
    )

    actions = ['update_data_processor', 'enable_data_processor', 'disable_data_processor']

    def update_data_processor(self, request, queryset): # pylint: disable=unused-argument
        add_messages = []

        for processor in queryset:
            add_messages.extend(processor.update_data_processor())

        for message in add_messages:
            if '[Success]' in message:
                self.message_user(request, message, messages.SUCCESS)
            else:
                self.message_user(request, message, messages.ERROR)

    update_data_processor.short_description = "Install updated versions"

    def enable_data_processor(self, request, queryset):
        queryset.update(enabled=True)

        self.message_user(request, str(queryset.count()) + ' data processor(s) enabled.')

    enable_data_processor.short_description = "Enable selected data processors"

    def disable_data_processor(self, request, queryset):
        queryset.update(enabled=False)

        self.message_user(request, str(queryset.count()) + ' data processor(s) disabled.')

    disable_data_processor.short_description = "Disable selected data processors"
