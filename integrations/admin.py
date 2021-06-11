# pylint: disable=line-too-long
# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Integration

@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'url_slug', 'type', 'game')
    search_fields = ('name', 'url_slug', 'type', 'configuration',)
    list_filter = ('game', 'type', 'create_new_players',)

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
