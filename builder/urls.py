# pylint: disable=line-too-long

from django.conf.urls import url

from .views import builder_game, builder_game_definition_json, builder_interaction_card, \
                   builder_home, builder_activities, builder_players, builder_sessions, \
                   builder_add_game, builder_data_processor_options, builder_activity_delete, \
                   builder_update_icon, builder_media, builder_media_upload, builder_game_templates, \
                   builder_settings, builder_game_variables, builder_activity_view

urlpatterns = [
    url(r'add-game.json$', builder_add_game, name='builder_add_game'),
    url(r'activities$', builder_activities, name='builder_activities'),
    url(r'data-processor-options.json$', builder_data_processor_options, name='builder_data_processor_options'),
    url(r'sessions$', builder_sessions, name='builder_sessions'),
    url(r'players$', builder_players, name='builder_players'),
    url(r'settings$', builder_settings, name='builder_settings'),
    url(r'^card/(?P<card>.+)', builder_interaction_card, name='builder_interaction_card'),
    url(r'^activity/(?P<slug>.+)/view', builder_activity_view, name='builder_activity_view'),
    url(r'^activity-templates$', builder_game_templates, name="builder_game_templates"),
    url(r'^activity/(?P<slug>.+)/delete', builder_activity_delete, name='builder_activity_delete'),
    url(r'^activity/(?P<game>.+)/variables.json', builder_game_variables, name='builder_game_variables'),
    url(r'^activity/(?P<game>.+).json$', builder_game_definition_json, name='builder_game_definition_json'),
    url(r'^activity/(?P<game>.+)', builder_game, name='builder_game'),
    url(r'^update-icon.json', builder_update_icon, name='builder_update_icon'),
    url(r'^media$', builder_media, name='builder_media'),
    url(r'^media_upload$', builder_media_upload, name='builder_media_upload'),
    url(r'^', builder_home, name='builder_home'),
]
