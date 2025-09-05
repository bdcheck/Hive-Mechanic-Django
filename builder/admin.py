# pylint: disable=line-too-long, ungrouped-imports
# -*- coding: utf-8 -*-

from filer.admin.fileadmin import FileAdmin
from prettyjson import PrettyJSONWidget

from django.contrib import messages
from django.contrib.gis import admin
from django.utils import timezone
from django.utils.safestring import mark_safe

try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField

try:
    from docker_utils.admin import PortableModelAdmin as ModelAdmin
except ImportError:
    from django.contrib.admin import ModelAdmin as ModelAdmin # pylint: disable=useless-import-alias

from .models import Game, GameVersion, InteractionCard, InteractionCardCategory, Player, \
                    Session, RemoteRepository, DataProcessor, DataProcessorLog, SiteSettings, \
                    CachedFile, StateVariable


class PrettyJSONWidgetFixed(PrettyJSONWidget):
    def render(self, name, value, attrs=None, **kwargs):
        return mark_safe(super(PrettyJSONWidgetFixed, self).render(name, value, attrs=None, **kwargs)) # nosec

@admin.register(DataProcessorLog)
class DataProcessorLogAdmin(admin.GISModelAdmin):
    list_display = ('data_processor', 'url', 'requested', 'response_status')
    list_filter = ('requested', 'response_status', 'data_processor')
    search_fields = ('url', 'request_payload', 'response_payload')

class GameVersionInline(admin.TabularInline):
    model = GameVersion

    verbose_name = 'Version'
    verbose_name_plural = 'Versions'
    template = 'admin_inlines/versions_tabular.html'

    show_change_link = True

    fields = ['created', 'creator', 'size']
    readonly_fields = ['created', 'creator', 'size']
    ordering = ('-created',)

    def has_add_permission(self, request, obj=None): # pylint: disable=arguments-differ,unused-argument
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Game)
class GameAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'is_template', 'archived',)
    list_filter = ('is_template', 'archived',)

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidgetFixed(attrs={'initial': 'parsed'})}
    }

    inlines = [
        GameVersionInline,
    ]

    actions = ['export_objects', 'archive_activity', 'restore_activity']

    def export_objects(self, request, queryset):
        return self.portable_model_export_items(request, queryset)

    export_objects.short_description = 'Export selected activities'

    def archive_activity(self, request, queryset):
        updated = queryset.filter(archived=None).update(archived=timezone.now())

        if updated == 1:
            self.message_user(request, '1 activity archived.', messages.SUCCESS)
        else:
            self.message_user(request, '%s activities archived.' % updated, messages.SUCCESS)

    archive_activity.short_description = "Archive activities"

    def restore_activity(self, request, queryset):
        updated = queryset.update(archived=None)

        if updated == 1:
            self.message_user(request, '1 activity restored.', messages.SUCCESS)
        else:
            self.message_user(request, '%s activities restored.' % updated, messages.SUCCESS)

    restore_activity.short_description = "Restore activities"

@admin.register(GameVersion)
class GameVersionAdmin(admin.GISModelAdmin):
    list_display = ('game', 'created', 'creator')
    search_fields = ['definition']
    list_filter = ('created', 'creator',)

    readonly_fields = ['game']

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidgetFixed(attrs={'initial': 'parsed'})}
    }

@admin.register(InteractionCardCategory)
class InteractionCardCategoryAdmin(admin.GISModelAdmin):
    list_display = ('name', 'priority',)

    search_fields = ['name']

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidgetFixed(attrs={'initial': 'parsed'})}
    }

@admin.register(InteractionCard)
class InteractionCardAdmin(admin.GISModelAdmin):
    list_display = ('name', 'identifier', 'category', 'enabled', 'version', 'issues', 'available_update',)
    list_filter = ('enabled', 'category',)
    search_fields = ['name', 'identifier']

    fieldsets = (
        (None, {
            'fields': ('name', 'identifier', 'enabled', 'version', 'category',)
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

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidgetFixed(attrs={'initial': 'parsed'})}
    }

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
class PlayerAdmin(ModelAdmin):
    list_display = ('identifier',)

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidgetFixed(attrs={'initial': 'parsed'})}
    }

    def export_objects(self, request, queryset):
        return self.portable_model_export_items(request, queryset)

    export_objects.short_description = 'Export selected players'

    actions = ['export_objects']

@admin.register(Session)
class SessionAdmin(admin.GISModelAdmin):
    list_display = ('player', 'game_version', 'started', 'completed')

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidgetFixed(attrs={'initial': 'parsed'})}
    }

@admin.register(RemoteRepository)
class RemoteRepositoryAdmin(admin.GISModelAdmin):
    list_display = ('name', 'url', 'priority', 'last_updated', 'enabled',)
    list_filter = ('enabled', 'last_updated',)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.GISModelAdmin):
    list_display = ('name', 'created', 'last_updated', 'total_message_limit', 'count_messages_since')

@admin.register(DataProcessor)
class DataProcessorAdmin(ModelAdmin):
    list_display = ('name', 'identifier', 'enabled', 'version', 'issues', 'available_update',)

    fieldsets = (
        (None, {
            'fields': ('name', 'identifier', 'enabled', 'version',)
        }),
        ('Implementaion', {
            'fields': ('processor_function', 'log_summary_function',),
        }),
        ('Miscellaneous', {
            'fields': ('repository_definition', 'metadata',),
        }),
    )

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidgetFixed(attrs={'initial': 'parsed'})}
    }

    actions = ['export_objects', 'update_data_processor', 'enable_data_processor', 'disable_data_processor']

    def export_objects(self, request, queryset):
        return self.portable_model_export_items(request, queryset)

    export_objects.short_description = 'Export selected data processors'

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

@admin.register(CachedFile)
class CachedFileAdmin(FileAdmin):
    list_display = ('original_url',)
    search_fields = ['original_url',]

@admin.register(StateVariable)
class StateVariableAdmin(admin.GISModelAdmin):
    list_display = ('key', 'added', 'length', 'player', 'activity', 'session')
    search_fields = ['key', 'value', 'metadata']
    list_filter = ('added', 'activity',)
