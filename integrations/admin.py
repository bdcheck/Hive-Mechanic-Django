# -*- coding: utf-8 -*-


from django.contrib import admin

from .models import Integration

@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'url_slug', 'type', 'game')
    search_fields = ('name', 'url_slug', 'type', 'configuration',)
    list_filter = ('game', 'type', 'create_new_players',)
