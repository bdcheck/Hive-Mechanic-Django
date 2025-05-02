# pylint: disable=no-member
# -*- coding: utf-8 -*-

class HiveActivityFinishedException(Exception):
    pass

def process_incoming(integration, payload):
    integration.process_player_incoming('cli_player', 'default', payload)

    return []

def execute_action(integration, session, action):
    if action['type'] == 'echo': # pylint: disable=no-else-return
        print(integration.translate_value(action['message'], session))

        return True
    elif action['type'] == 'echo-image':
        print(action['image-url'])

        return True

    elif action['type'] == 'end-activity':
        session.complete()

        return True

    return False

def annotate_statistics(integration, statistics): # pylint: disable=unused-argument
    statistics['type'] = 'Other Integration'

    # Add stats
