from django.conf.urls import url

from .views import incoming_http, incoming_http_player

urlpatterns = [
    url(r'^(?P<slug>.+)/players/(?P<player>.+).json$', incoming_http_player, name='incoming_http_player'),
    url(r'^(?P<slug>.+).json$', incoming_http, name='incoming_http'),
]
