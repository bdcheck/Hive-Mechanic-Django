# pylint: disable=line-too-long

from django.conf.urls import url

from .views import builder_game, builder_game_definition_json, builder_interaction_card, \
                   builder_home, builder_games, builder_players, builder_sessions, \
                   builder_add_game

urlpatterns = [
    url(r'add-game.json$', builder_add_game, name='builder_add_game'),
    url(r'games$', builder_games, name='builder_games'),
    url(r'sessions$', builder_sessions, name='builder_sessions'),
    url(r'players$', builder_players, name='builder_players'),
    url(r'^activity/(?P<game>.+).json$', builder_game_definition_json, name='builder_game_definition_json'),
    url(r'^card/(?P<card>.+)', builder_interaction_card, name='builder_interaction_card'),
    url(r'^activity/(?P<game>.+)', builder_game, name='builder_game'),
    url(r'^', builder_home, name='builder_home'),
]
