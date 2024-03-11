# pylint: disable=line-too-long, wrong-import-position

import sys

if sys.version_info[0] > 2:
    from django.urls import re_path as url # pylint: disable=no-name-in-module
else:
    from django.conf.urls import url

from .views import incoming_http, incoming_http_player, incoming_http_commands, incoming_http_fetch

urlpatterns = [
    url(r'^commands.json$', incoming_http_commands, name='incoming_http_commands'),
    url(r'^fetch.json$', incoming_http_fetch, name='incoming_http_fetch'),
    url(r'^(?P<slug>.+)/players/(?P<player>.+).json$', incoming_http_player, name='incoming_http_player'),
    url(r'^(?P<slug>.+).json$', incoming_http, name='incoming_http'),
]
