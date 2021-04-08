# pylint: disable=line-too-long, no-member
# -*- coding: utf-8 -*-

from builtins import object, str # pylint: disable=redefined-builtin

import json
import logging
import sys
import time

from enum import Enum

import requests

class HiveError(Exception):
    def __init__(self, value):
        super(HiveError, self).__init__(value) # pylint: disable=super-with-arguments

        self.value = value

    def __str__(self):
        return repr(self.value)

def post_request_with_retries(url, payload, logger, max_retry_duration=120, initial_retry_duration=3.75, server_timeout=60): # pylint: disable=too-many-arguments, unused-argument
    query = None
    last_error = None

    while initial_retry_duration <= max_retry_duration:
        try:
            query = None

            if server_timeout is not None:
                query = requests.post(url, data=payload, timeout=server_timeout)
            else:
                query = requests.post(url, data=payload)

            if query.status_code == requests.codes.ok: # pylint: disable=no-else-return
                return query
            elif query.status_code >= 400:
                last_error = HiveError(url + ' returned ' + str(query.status_code))

                logging.error(str(last_error))

                break
        except requests.exceptions.HTTPError as error:
            logging.warning(str(error))
            logging.warning('Retrying in %.2f seconds...', initial_retry_duration)

            last_error = error
        except requests.exceptions.Timeout as error:
            logging.warning(str(error))
            logging.warning('Retrying in %.2f seconds...', initial_retry_duration)

            last_error = error
        except requests.exceptions.ConnectionError as error:
            logging.warning(str(error))
            logging.warning('Retrying in %.2f seconds...', initial_retry_duration)

            last_error = error

        time.sleep(initial_retry_duration)

        initial_retry_duration *= 2

    if last_error is not None:
        raise last_error # pylint: disable=raising-bad-type

    raise Exception('Unknown error occurred.')

class VariableScope(Enum):
    game = 'game'
    player = 'player'
    session = 'session'

class HiveClient(object): # pylint: disable=useless-object-inheritance
    def __init__(self, **kwargs):
        self.api_url = kwargs['api_url']
        self.token = None
        self.timeout = None

        if self.api_url.endswith('/') is False:
            self.api_url = self.api_url + '/'

        if 'token' in kwargs:
            self.token = kwargs['token']

        if 'timeout' in kwargs:
            self.timeout = kwargs['timeout']

        if 'logger' in kwargs:
            self.logger = kwargs['logger']
        else:
            self.logger = logging.getLogger()
            self.logger.setLevel(logging.INFO)

            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('HiveMechanic Client [%(levelname)s] %(asctime)s: %(message)s')
            handler.setFormatter(formatter)

            self.logger.addHandler(handler)

    def issue_commands(self, commands, player=None, endpoint=None): # pylint: disable=unused-argument
        payload = {
            'token': self.token,
            'player': player
        }

        payload_commands = []

        for command in commands:
            payload_commands.append(command.to_dict())

        payload['commands'] = json.dumps(payload_commands, indent=2)

        response = post_request_with_retries(self.command_url(), payload, self.logger, server_timeout=self.timeout)

        return response.json()

    def issue_command(self, command, player=None):
        return self.issue_commands([command], player)

    def fetch_variable(self, variable_name, player=None, default=None, scope=VariableScope.game):
        payload = {
            'token': self.token,
            'name': variable_name,
            'scope': scope.value
        }

        if player is not None:
            payload['player'] = player

        response = post_request_with_retries(self.fetch_url(), payload, self.logger, server_timeout=self.timeout)

        logging.info('%s = %s', self.fetch_url(), response.json())

        if 'value' in response.json():
            logging.info('%s = %s', variable_name, response.json()['value'])

            return response.json()['value']

        logging.info('Unable to retrieve value for %s from %s', variable_name, self.fetch_url())

        return default

    def command_url(self, endpoint='commands.json'):
        return self.api_url + endpoint

    def fetch_url(self, endpoint='fetch.json'):
        return self.api_url + endpoint


class Command(object): # pylint: disable=useless-object-inheritance
    def __init__(self, **kwargs): # pylint: disable=super-with-arguments
        pass

    def to_dict(self):
        command = {}

        self.add_arguments(command)

        command['type'] = self.command_type()

        return command

    def add_arguments(self, command):
        pass # Add additional arguments in subclass.

    def command_type(self): # pylint: disable=no-self-use
        return 'base-command'


class GotoCommand(Command):
    def __init__(self, destination, **kwargs):
        super(GotoCommand, self).__init__(**kwargs) # pylint: disable=super-with-arguments

        self.destination = destination

    def add_arguments(self, command):
        command['destination'] = self.destination

    def command_type(self): # pylint: disable=no-self-use
        return 'go-to'

class TriggerInterruptCommand(Command):
    def __init__(self, interrupt, **kwargs):
        super(TriggerInterruptCommand, self).__init__(**kwargs) # pylint: disable=super-with-arguments

        self.interrupt = interrupt

    def add_arguments(self, command):
        command['interrupt'] = self.interrupt

    def command_type(self): # pylint: disable=no-self-use
        return 'trigger-interrupt'

class SetVariableCommand(Command):
    def __init__(self, name, value, scope, **kwargs):
        super(SetVariableCommand, self).__init__(**kwargs) # pylint: disable=super-with-arguments

        self.name = name
        self.value = value
        self.scope = scope.value

    def add_arguments(self, command):
        command['scope'] = self.scope
        command['variable'] = self.name
        command['value'] = self.value

    def command_type(self): # pylint: disable=no-self-use
        return 'set-variable'
