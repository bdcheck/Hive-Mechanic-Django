from django.conf.urls import url

from .views import builder_home, builder_game, builder_game_definition_json

urlpatterns = [
    url(r'^game/(?P<game>.+).json$', builder_game_definition_json, name='builder_game_definition_json'),
    url(r'^game/(?P<game>.+)', builder_game, name='builder_game'),
    url(r'^$', builder_home, name='builder_home'),
]
