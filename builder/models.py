# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse


class Game(models.Model):
    name = models.CharField(max_length=1024, db_index=True)
    slug = models.SlugField(max_length=1024, db_index=True, unique=True)

    def __unicode__(self):
        return self.name
        
    def definition_json(self, timestamp=None):
        return reverse('builder_game_definition_json', args=[self.slug])
    
class GameVersion(models.Model):
    game = models.ForeignKey(Game, related_name='versions')
    created = models.DateTimeField()

    definition = models.TextField(max_length=(8 * 1024 * 1024), db_index=True)

    def __unicode__(self):
        return self.game.name + ' (' + str(self.created) + ')'
        
    def process_incoming(self, session, payload):
        pass

class InteractionCard(models.Model):
    name = models.CharField(max_length=4096, unique=True)
    identifier = models.SlugField(max_length=4096, unique=True)

    description = models.TextField(max_length=16384, null=True, blank=True)

    enabled = models.BooleanField(default=True)
    
    evaluate_function = models.TextField(max_length=1048576, default='return None, [], None')
    entry_actions = models.TextField(max_length=1048576, default='return []')

class Player(models.Model):
    identifier = models.CharField(max_length=4096, unique=True)

    player_state = JSONField(default=dict)
        
class Session(models.Model):
    player = models.ForeignKey(Player, related_name='sessions')
    game_version = models.ForeignKey(GameVersion, related_name='sessions')
    
    started = models.DateTimeField()
    completed = models.DateTimeField(null=True, blank=True)
    
    session_state = JSONField(default=dict)

    def process_incoming(self, integation, payload):
        current_node = None
        
        if 'session_current_node' in self.session_state:
            current_node = self.session_state['session_current_node']
        
        actions = self.game_version.process_incoming(self, payload)
        
        if integration is not None:
            integration.execute_actions(self, actions)
        else:
            for integration in self.game_version.game.integrations.all():
                integration.execute_actions(self, actions)
        
    def tick(self):
        self.process_incoming(None, None)