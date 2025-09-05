from django.contrib.gis import admin

from .models import LogTag, LogItem

@admin.register(LogTag)
class LogTagAdmin(admin.GISModelAdmin):
    list_display = ('tag', 'name',)

@admin.register(LogItem)
class LogItemAdmin(admin.GISModelAdmin):
    list_display = ('source', 'logged', 'message', 'tags_str')
    list_filter = ('tags', 'logged', 'source')
