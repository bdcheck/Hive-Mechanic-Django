# pylint: disable=no-member, line-too-long
# -*- coding: utf-8 -*-

from future.utils import python_2_unicode_compatible

from django.conf import settings
from django.core.management import call_command
from django.db import models
from django.utils import timezone

from integrations.models import Integration

class HiveActivityFinishedException(Exception):
    pass

def process_incoming(integration, payload):
    integration.process_player_incoming('cli_player', 'default', payload)

    return []

def execute_action(integration, session, action):
    player = session.player

    if action['type'] == 'echo': # pylint: disable=no-else-return
        print(integration.translate_value(action['message'], session))

        return True
    elif action['type'] == 'echo-image':
        print(action['image-url'])

        return True

    elif action['type'] == 'echo-image':
        print(action['image-url'])

        return True

    elif action['type'] == 'end-activity':
        session.completed = timezone.now()
        session.save()
        
        raise HiveActivityFinishedException('Activity finished normally')

    return False
