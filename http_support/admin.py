# -*- coding: utf-8 -*-


from django.contrib.gis import admin

from .models import ApiClient

@admin.register(ApiClient)
class ApiClientAdmin(admin.OSMGeoAdmin):
    list_display = ('name', 'start_date', 'end_date',)
