from django.conf.urls import url

from .views import incoming_http

urlpatterns = [
    url(r'^(?P<game_slug>.+)/(?P<slug>.+).json$', incoming_http, name='incoming_http'),
]
