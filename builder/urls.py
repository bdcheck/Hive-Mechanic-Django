# pylint: disable=line-too-long

from django.conf.urls import url

from .views import builder_game, builder_game_definition_json, builder_interaction_card

urlpatterns = [
    url(r'^game/(?P<game>.+).json$', builder_game_definition_json, name='builder_game_definition_json'),
    url(r'^card/(?P<card>.+)', builder_interaction_card, name='builder_interaction_card'),
    url(r'^game/(?P<game>.+)', builder_game, name='builder_game'),
]
