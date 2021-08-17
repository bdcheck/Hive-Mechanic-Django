# pylint: disable=line-too-long, no-member
# -*- coding: utf-8 -*-

import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Game

class UserPermissionsTestCase(TestCase):
    fixtures = ['fixtures/groups.json']

    def setUp(self):
        user_model = get_user_model()

        self.first_user = user_model.objects.create_user(username='first_test_user', email='first_test_user@example.com', password='foobar') # nosec
        self.second_user = user_model.objects.create_user(username='second_test_user', email='second_test_user@example.com', password='foobar') # nosec
        self.views_user = user_model.objects.create_user(username='views_user', email='views_user@example.com', password='foobar') # nosec

        self.test_game = Game.objects.create(name='Test Game', slug='unit-test-game')

        self.editor_group = Group.objects.get(name='Hive Mechanic Game Editor')
        self.reader_group = Group.objects.get(name='Hive Mechanic Reader')
        self.manager_group = Group.objects.get(name='Hive Mechanic Manager')

        call_command('initialize_permissions')


    def test_models_edit_view_permissions(self): # pylint: disable=invalid-name
        self.assertIsNotNone(self.test_game)
        self.assertIsNotNone(self.first_user)
        self.assertIsNotNone(self.second_user)

        self.assertTrue(self.test_game.can_view(self.first_user))
        self.assertTrue(self.test_game.can_view(self.second_user))

        self.assertEqual(self.test_game.viewers.count(), 0)

        self.test_game.viewers.add(self.second_user)

        self.assertEqual(self.test_game.viewers.count(), 1)

        self.assertFalse(self.test_game.can_view(self.first_user))
        self.assertTrue(self.test_game.can_view(self.second_user))

        self.assertFalse(self.test_game.can_edit(self.first_user))
        self.assertFalse(self.test_game.can_edit(self.second_user))

        self.assertEqual(self.test_game.editors.count(), 0)

        self.test_game.editors.add(self.second_user)

        self.assertEqual(self.test_game.editors.count(), 1)

        self.assertFalse(self.test_game.can_edit(self.first_user))
        self.assertTrue(self.test_game.can_edit(self.second_user))

        self.test_game.viewers.remove(self.second_user)

        self.assertEqual(self.test_game.viewers.count(), 0)

        self.assertFalse(self.test_game.can_view(self.first_user))
        self.assertTrue(self.test_game.can_view(self.second_user))


    def test_views_edit_view_permissions(self): # pylint: disable=invalid-name
        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='first_test_user', password='foobar') # nosec

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 403)

        self.reader_group.user_set.add(self.first_user)

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 200)

        self.test_game.viewers.add(self.second_user)

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 403)

        self.client.login(username='second_test_user', password='foobar') # nosec

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 403)

        self.reader_group.user_set.add(self.second_user)

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response, 'bar222')

        payload = {
            'definition': json.dumps({
                'foo': 'bar222'
            })
        }

        response = self.client.post(reverse('builder_game', args=[self.test_game.slug]), payload)
        self.assertEqual(response.status_code, 403)

        self.test_game.editors.add(self.second_user)

        response = self.client.post(reverse('builder_game', args=[self.test_game.slug]), payload)

        response_msg = json.loads(response.content)

        self.assertEqual(response.status_code, 200)

        self.assertTrue(response_msg['success'])

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'bar222')

        self.test_game.editors.remove(self.second_user)

        response = self.client.post(reverse('builder_game', args=[self.test_game.slug]), payload)
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'bar222')

        self.client.login(username='first_test_user', password='foobar') # nosec

        response = self.client.get(reverse('builder_game', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 403)

        response = self.client.post(reverse('builder_game', args=[self.test_game.slug]), payload)
        self.assertEqual(response.status_code, 403)

        self.test_game.viewers.remove(self.second_user)

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'bar222')

        response = self.client.post(reverse('builder_game', args=[self.test_game.slug]), payload)
        self.assertEqual(response.status_code, 200)


    def test_views_misc_permissions(self): # pylint: disable=invalid-name, too-many-statements
        self.client.logout()

        # self.editor_group = Group.objects.get(group='Hive Mechanic Game Editor')
        # self.reader_group = Group.objects.get(group='Hive Mechanic Reader')
        # self.manager_group = Group.objects.get(group='Hive Mechanic Manager')

        response = self.client.get(reverse('builder_home'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('builder_games'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('builder_sessions'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('builder_players'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('builder_players'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('builder_game', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('builder_interaction_card', args=['send-message']))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('builder_add_game'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='views_user', password='foobar') # nosec

        response = self.client.get(reverse('builder_home'))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('builder_games'))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('builder_sessions'))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('builder_players'))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('builder_players'))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('builder_game', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('builder_interaction_card', args=['send-message']))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('builder_add_game'))
        self.assertEqual(response.status_code, 403)

        self.reader_group.user_set.add(self.views_user)

        response = self.client.get(reverse('builder_home'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_games'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_sessions'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_players'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_players'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_game', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_interaction_card', args=['send-message']))
        self.assertEqual(response.status_code, 200)

        self.test_game.viewers.add(self.second_user)

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('builder_game', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 403)

        self.test_game.viewers.add(self.views_user)

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_game', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_add_game'))
        self.assertEqual(response.status_code, 403)

        self.reader_group.user_set.remove(self.views_user)

        self.editor_group.user_set.add(self.views_user)

        response = self.client.get(reverse('builder_home'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_games'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_sessions'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_players'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_players'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_interaction_card', args=['send-message']))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_add_game'))
        self.assertEqual(response.status_code, 200)

        self.test_game.viewers.remove(self.views_user)

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('builder_game', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 403)

        self.test_game.viewers.add(self.views_user)

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_game', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 200)

        self.test_game.viewers.remove(self.views_user)
        self.test_game.editors.add(self.views_user)

        response = self.client.get(reverse('builder_game_definition_json', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('builder_game', args=[self.test_game.slug]))
        self.assertEqual(response.status_code, 200)


    def tearDown(self):
        self.first_user.delete()
        self.second_user.delete()
        self.views_user.delete()

        self.test_game.delete()
