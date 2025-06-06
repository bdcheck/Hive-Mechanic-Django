# pylint: disable=line-too-long
# -*- coding: utf-8 -*-

from django.contrib import admin

try:
    from docker_utils.admin import PortableModelAdmin as ModelAdmin
except ImportError:
    from django.contrib.admin import ModelAdmin as ModelAdmin # pylint: disable=useless-import-alias, ungrouped-imports

from .models import Integration

@admin.register(Integration)
class IntegrationAdmin(ModelAdmin):
    list_display = ('name', 'url_slug', 'type', 'game', 'enabled',)
    search_fields = ('name', 'url_slug', 'type', 'configuration',)
    list_filter = ('enabled', 'game', 'type', 'create_new_players',)

    actions = ['export_objects']

    def export_objects(self, request, queryset):
        return self.portable_model_export_items(request, queryset)

    export_objects.short_description = 'Export selected integrations'

    def get_readonly_fields(self, request, obj=None):
        fields = super(IntegrationAdmin, self).get_readonly_fields(request, obj=obj) # pylint: disable=super-with-arguments

        if request.user.has_perm('twilio_support.twilio_history_access') is False:
            return ('configuration',)

        return fields

    def get_form(self, request, obj=None, **kwargs): # pylint: disable=arguments-differ
        if request.user.has_perm('twilio_support.twilio_history_access') is False:
            if obj is not None and obj.configuration is not None and 'auth_token' in obj.configuration:
                obj.configuration['auth_token'] = '*****' # nosec
        else:
            pass

        form = super(IntegrationAdmin, self).get_form(request, obj=obj, **kwargs) # pylint: disable=super-with-arguments

        return form
