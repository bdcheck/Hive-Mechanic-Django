# pylint: disable=line-too-long, no-member
# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from ..models import InteractionCard

# Verifies that client implementation files are deleted
class InteractionCardsMediaFilesDeletedTestCase(TestCase):
    def setUp(self):
        call_command('install_default_repository', silent=True)

        InteractionCard.objects.all().update(enabled=True)

        for card in InteractionCard.objects.all():
            card.update_card()

    def test_client_js_deleted(self):
        first_card = InteractionCard.objects.all().first()

        js_file_path = first_card.client_implementation.path

        self.assertIsNotNone(js_file_path)
        self.assertTrue(os.path.exists(js_file_path))

        first_card.delete()

        self.assertFalse(os.path.exists(js_file_path))

        settings.HIVE_DELETE_CLIENT_IMPLEMENTATION_JS = False

        second_card = InteractionCard.objects.all().first()

        second_file_path = second_card.client_implementation.path

        self.assertIsNotNone(second_file_path)
        self.assertTrue(os.path.exists(second_file_path))

        second_card.delete()

        self.assertTrue(os.path.exists(second_file_path))

    def tearDown(self):
        pass
