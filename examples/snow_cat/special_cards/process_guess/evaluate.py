# pylint: disable=line-too-long

import datetime
import logging
import re

from django.utils import timezone

# Incoming globals: definition, response, last_transition, previous_state

# Definition Example
#      {
#        "not_found_action": "request-consent-2",
#        "name": "Process Consent Response",
#        "patterns": [
#          {
#            "action": "continue-intro",
#            "pattern": "^[Yy]"
#          },
#          {
#            "action": "nonconsent-thanks-2",
#            "pattern": "^[Nn]"
#          }
#        ],
#        "timeout": {
#          "duration": 4,
#          "units": "hour",
#          "action": "consent-timeout"
#        },
#        "type": "process-guess",
#        "id": "process-consent"
#      },

logger = logging.getLogger('db')

result['details'] = {}

result['actions'] = []
result['next_id'] = None

logger.info('PROCESS RESP: %s -- %s', response, str(type(response)))

if response is not None:
    result['details']['response'] = response
    result['actions'] = []
    result['next_id'] = None

    for pattern_def in definition['patterns']:
        logger.info('MATCH?')
        logger.info(str(pattern_def['pattern']))
        logger.info(str(response))
        logger.info(str(re.match(pattern_def['pattern'], response)))

        pattern = re.compile(pattern_def['pattern'], re.IGNORECASE)

        if result['next_id'] is None and pattern.match(response) is not None:
            result['next_id'] = pattern_def['action']
            result['matched_pattern'] = pattern_def['pattern']

    if result['next_id'] is None and definition['not_found_action'] is not None:
        result['next_id'] = definition['not_found_action']
        result['matched_pattern'] = 'no-matches-found'
elif 'timeout' in definition:
    test = timezone.now()

    logger.info('NOW: %s', test.isoformat())

    if 'units' in definition['timeout'] and 'duration' in definition['timeout']:
        duration = int(definition['timeout']['duration'])

        if definition['timeout']['units'] == 'second':
            test = test - datetime.timedelta(seconds=duration)
        elif definition['timeout']['units'] == 'minute':
            test = test - datetime.timedelta(seconds=(duration * 60))
        elif definition['timeout']['units'] == 'hour':
            test = test - datetime.timedelta(seconds=(duration * 60 * 60))
        elif definition['timeout']['units'] == 'day':
            test = test - datetime.timedelta(days=duration)
        else:
            logger.info('CANNOT TEST WITH DURATION = %d, AND UNITS = %s', str(duration), str(definition['timeout']['units']))

    logger.info('TEST: %s >? %s', last_transition.isoformat(), test.isoformat())

    if last_transition < test:
        result['next_id'] = definition['timeout']['action']
    else:
        result['next_id'] = definition['id']

if result['next_id'] is not None and ('#' in result['next_id']) is False:
    result['next_id'] = definition['sequence_id'] + '#' + result['next_id']
