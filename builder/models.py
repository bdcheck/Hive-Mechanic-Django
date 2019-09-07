# pylint: disable=no-member, line-too-long
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from django_dialog_engine.models import Dialog

class InteractionCard(models.Model):
    name = models.CharField(max_length=4096, unique=True)
    identifier = models.SlugField(max_length=4096, unique=True)

    description = models.TextField(max_length=16384, null=True, blank=True)

    enabled = models.BooleanField(default=True)

    evaluate_function = models.TextField(max_length=1048576, default='return None, [], None')
    entry_actions = models.TextField(max_length=1048576, default='return []')

    client_implementation = models.FileField(upload_to='interaction_cards/', null=True, blank=True)

    def __unicode__(self):
        return self.name + ' (' + self.identifier + ')'

class Game(models.Model):
    name = models.CharField(max_length=1024, db_index=True)
    slug = models.SlugField(max_length=1024, db_index=True, unique=True)

    cards = models.ManyToManyField(InteractionCard, related_name='games')

    game_state = JSONField(default=dict)

    def __unicode__(self):
        return self.name

    def definition_json(self):
        return reverse('builder_game_definition_json', args=[self.slug])

    def interaction_card_modules_json(self):
        modules = []

        for card in self.cards.all():
            modules.append(reverse('builder_interaction_card', args=[card.identifier]))

        return mark_safe(json.dumps(modules)) # nosec

    def current_active_session(self, player):
        session = None

        for version in self.versions.order_by('-created'):
            if session is None:
                session = version.sessions.filter(player=player, completed=None).order_by('-started').first()

        return session

    def set_cookie(self, cookie, value):
        self.game_state[cookie] = value # pylint: disable=unsupported-assignment-operation
        self.save()

class GameVersion(models.Model):
    game = models.ForeignKey(Game, related_name='versions')
    created = models.DateTimeField()

    definition = models.TextField(max_length=(1024 * 1024 * 1024))

    def __unicode__(self):
        return self.game.name + ' (' + str(self.created) + ')'

    def process_incoming(self, session, payload):
        actions = []

        dialog_key = 'session-' + str(session.pk)

        dialog = Dialog.objects.filter(key=dialog_key, finished=None).order_by('-started').first()

        if dialog is None:
            dialog = Dialog(key=dialog_key, started=timezone.now())
            dialog.dialog_snapshot = self.dialog_snapshot()
            dialog.save()

        new_actions = dialog.process(payload, extras={'session': session})

        while new_actions is not None and len(new_actions) > 0: # pylint: disable=len-as-condition
            actions.extend(new_actions)

            new_actions = dialog.process(None)

        dialog = Dialog.objects.filter(key=dialog_key).order_by('-started').first()

        if dialog.finished is not None:
            session.completed = dialog.finished
            session.save()

        return actions

    def dialog_snapshot(self):
        snapshot = []
        
        print('DEF: ' + str(self.pk) + ' -- ' + self.definition)

        sequences = json.loads(self.definition)

        for sequence in sequences:
            for item in sequence['items']:
                item_id = item['id']
                
                if ((sequence['id'] + '#') in item_id) is False:
                    item_id = sequence['id'] + '#' + item_id

                if len(snapshot) == 0: # pylint: disable=len-as-condition
                    snapshot.append({
                        'type': 'begin',
                        'id': 'dialog-start',
                        'next_id': item_id
                    })

                interaction_card = InteractionCard.objects.filter(identifier=item['type']).first()
                
                item['sequence_id'] = sequence['id']
                
                print(item_id + ' -> ' + json.dumps(item, indent=2))

                if interaction_card is not None:
                    snapshot.append({
                        'type': 'custom',
                        'id': item_id,
                        'definition': item,
                        'evaluate': interaction_card.evaluate_function,
                        'actions': interaction_card.entry_actions
                    })
                else:
                    snapshot.append({
                        'type': 'echo',
                        'id': item_id,
                        'next_id': 'dialog-end',
                        'message': 'Unknown interaction type "' + item['type'] + '".'
                    })

        snapshot.append({
            'type': 'end',
            'id': 'dialog-end'
        })

        return snapshot

class Player(models.Model):
    identifier = models.CharField(max_length=4096, unique=True)

    player_state = JSONField(default=dict)

    def set_cookie(self, cookie, value):
        self.player_state[cookie] = value # pylint: disable=unsupported-assignment-operation
        self.save()

class Session(models.Model):
    player = models.ForeignKey(Player, related_name='sessions')
    game_version = models.ForeignKey(GameVersion, related_name='sessions')

    started = models.DateTimeField()
    completed = models.DateTimeField(null=True, blank=True)

    session_state = JSONField(default=dict)

    def process_incoming(self, integration, payload):
        current_node = None # pylint: disable=unused-variable

        if 'session_current_node' in self.session_state: # pylint: disable=unsupported-membership-test
            current_node = self.session_state['session_current_node'] # pylint: disable=unsubscriptable-object

        actions = self.game_version.process_incoming(self, payload)

        if integration is not None:
            integration.execute_actions(self, actions)
        else:
            for game_integration in self.game_version.game.integrations.all():
                game_integration.execute_actions(self, actions)

    def nudge(self):
        self.process_incoming(None, None)

    def set_cookie(self, cookie, value):
        self.session_state[cookie] = value # pylint: disable=unsupported-assignment-operation
        self.save()

    def fetch_cookie(self, cookie):
        if cookie in self.session_state: # pylint: disable=unsupported-membership-test
            return self.session_state[cookie]  # pylint: disable=unsubscriptable-object

        if cookie in self.player.player_state:
            return self.player.player_state[cookie]

        if cookie in self.game_version.game.game_state:
            return self.game_version.game.game_state[cookie]

        return None
