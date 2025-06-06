# pylint: disable=line-too-long, no-member, ungrouped-imports
# -*- coding: utf-8 -*-

from __future__ import print_function

from builtins import str # pylint: disable=redefined-builtin

import datetime
import json
import re
import sys

import phonenumbers

from filer.models import filemodels
from future.utils import python_2_unicode_compatible

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from passive_data_kit.models import DataPoint

from activity_logger.models import log
from builder.models import Game, Player, Session, SiteSettings

if sys.version_info[0] > 2:
    from django.db.models import JSONField # pylint: disable=no-name-in-module
else:
    from django.contrib.postgres.fields import JSONField

INTEGRATION_TYPES = (
    ('twilio', 'Twilio'),
    ('simple_messaging', 'Simple Messaging'),
    ('http', 'HTTP'),
    ('command_line', 'Command Line'),
    ('other', 'Other'),
)

class PermissionsSupport(models.Model):
    class Meta: # pylint: disable=old-style-class, no-init, too-few-public-methods
        managed = False
        default_permissions = ()

        permissions = (
            ('integration_access_view', 'View integration information'),
            ('integration_access_edit', 'Edit integration information'),
        )

@python_2_unicode_compatible
class Integration(models.Model):
    name = models.CharField(max_length=1024, unique=True)
    url_slug = models.SlugField(max_length=1024, unique=True)
    type = models.CharField(max_length=1024, choices=INTEGRATION_TYPES, default='twilio')

    game = models.ForeignKey(Game, related_name='integrations', on_delete=models.SET_NULL, blank=True, null=True)

    create_new_players = models.BooleanField(default=True)

    configuration = JSONField(default=dict, help_text=_('configuration_help_text'), blank=True, null=True)

    editors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='integration_editables', blank=True)
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='integration_viewables', blank=True)

    enabled = models.BooleanField(default=True)

    def __str__(self):
        if self.game is not None:
            return '%s (%s)' % (self.name, self.game.slug)

        return '%s (No game configured)' % self.name

    def log_id(self):
        return 'integration:%d' % self.pk

    def is_enabled(self):
        if self.enabled is not True:
            return self.enabled

        if self.type == 'twilio': # pylint: disable=no-else-return
            site_settings = SiteSettings.objects.all().first()

            if site_settings.total_message_limit is not None:
                from twilio_support.models import IncomingMessage, OutgoingMessage, OutgoingCall # pylint: disable=import-outside-toplevel

                incoming_messages = IncomingMessage.objects.all()

                if site_settings.count_messages_since is not None:
                    incoming_messages = IncomingMessage.objects.filter(receive_date__gte=site_settings.count_messages_since)

                outgoing_messages = OutgoingMessage.objects.all()

                if site_settings.count_messages_since is not None:
                    outgoing_messages = OutgoingMessage.objects.filter(sent_date__gte=site_settings.count_messages_since)

                outgoing_calls = OutgoingCall.objects.all()

                if site_settings.count_messages_since is not None:
                    outgoing_calls = OutgoingCall.objects.filter(sent_date__gte=site_settings.count_messages_since)

                total = incoming_messages.count() + outgoing_messages.count() + outgoing_calls.count()

                if total >= site_settings.total_message_limit:
                    print('Disabling %s: Twilio traffic of %d exceeds site limit of %d.' % (self, total, site_settings.total_message_limit))

                    self.enabled = False
                    self.save()

        if self.type == 'simple_messaging': # pylint: disable=no-else-return
            site_settings = SiteSettings.objects.all().first()

            if site_settings.total_message_limit is not None:
                from simple_messaging.models import IncomingMessage, OutgoingMessage # pylint: disable=import-outside-toplevel

                incoming_messages = IncomingMessage.objects.all()

                if site_settings.count_messages_since is not None:
                    incoming_messages = IncomingMessage.objects.filter(receive_date__gte=site_settings.count_messages_since)

                outgoing_messages = OutgoingMessage.objects.all()

                if site_settings.count_messages_since is not None:
                    outgoing_messages = OutgoingMessage.objects.filter(sent_date__gte=site_settings.count_messages_since)

                total = incoming_messages.count() + outgoing_messages.count() + outgoing_calls.count()

                if total >= site_settings.total_message_limit:
                    print('Disabling %s: Messaging traffic of %d exceeds site limit of %d.' % (self, total, site_settings.total_message_limit))

                    self.enabled = False
                    self.save()

        return self.enabled

    def close_sessions(self, payload):
        if self.type == 'twilio': # pylint: disable=no-else-return
            from twilio_support.models import close_sessions as twilio_close_sessions # pylint: disable=import-outside-toplevel

            twilio_close_sessions(self, payload) # pylint: disable=no-value-for-parameter

    def process_incoming(self, payload):
        if self.type == 'twilio': # pylint: disable=no-else-return
            from twilio_support.models import process_incoming as twilio_incoming # pylint: disable=import-outside-toplevel

            return twilio_incoming(self, payload) # pylint: disable=no-value-for-parameter
        elif self.type == 'simple_messaging':
            from simple_messaging_hive.models import process_incoming as simple_messaging_incoming # pylint: disable=import-outside-toplevel

            return simple_messaging_incoming(self, payload) # pylint: disable=no-value-for-parameter
        elif self.type == 'http':
            from http_support.models import process_incoming as http_incoming # pylint: disable=import-outside-toplevel

            return http_incoming(self, payload) # pylint: disable=no-value-for-parameter
        elif self.type == 'command_line':
            from cli_support.models import process_incoming as cli_incoming # pylint: disable=import-outside-toplevel

            return cli_incoming(self, payload) # pylint: disable=no-value-for-parameter
        else:
            raise Exception('No "' + self.type + '" method implemented to process payload: ' + json.dumps(payload, indent=2))

    def is_interrupt(self, pattern, value): # pylint: disable=no-self-use
        # TODO: Implement support-specific interrupts here... # pylint: disable=fixme

        if pattern == '':
            return False

        if isinstance(pattern, str) and isinstance(value, str):
            if re.search(pattern, value, re.IGNORECASE) is not None:
                return True

        return False

    def process_player_incoming(self, player_lookup_key, player_lookup_value, payload, extras=None):
        player_match = None

        for player in Player.objects.all():
            if player_lookup_key in player.player_state:
                if player.player_state[player_lookup_key] == player_lookup_value:
                    player_match = player

        if player_match is None and self.create_new_players:
            player_match = Player(identifier=(player_lookup_key + ':' + player_lookup_value))
            player_match.player_state[player_lookup_key] = player_lookup_value # pylint: disable=unsupported-assignment-operation

            player_match.save()

            log(self.log_id(), 'Created new player.', tags=['integration', 'player'], metadata=payload, player=player_match, session=None, game_version=self.game.latest_version())

        if player_match is not None:
            session = self.game.current_active_session(player=player_match)

            if session is None:
                session = Session(game_version=self.game.versions.order_by('-created').first(), player=player_match, started=timezone.now())
                session.save()

                if extras is not None and 'last_message' in extras:
                    del extras['last_message']

                if extras is not None and ('message_type' in extras) and extras['message_type'] == 'call':
                    pass
                else:
                    pass # session.process_incoming(self, None, extras)

                log(self.log_id(), 'Created new session.', tags=['integration', 'player'], metadata=payload, player=player_match, session=session, game_version=session.game_version)

            log(self.log_id(), 'Processing incoming payload.', tags=['integration'], metadata=payload, player=player_match, session=session, game_version=session.game_version)

            # Skip terms if call...

            if extras.get('message_type', 'text') != 'call' and session.visited_terms() is False and session.accepted_terms() is False:
                session.advance_to_terms(payload=payload)

                session.process_incoming(self, None)

                return

            if isinstance(payload, list):
                actions = payload

                payload = None

                self.execute_actions(session, actions)

            session.process_incoming(self, payload, extras)

    def execute_actions(self, session, actions): # pylint: disable=no-self-use, unused-argument
        if actions is not None:
            for action in actions:
                processed = False

                if self.type == 'twilio':
                    from twilio_support.models import execute_action as twilio_execute # pylint: disable=import-outside-toplevel

                    processed = twilio_execute(self, session, action)
                if self.type == 'simple_messaging':
                    from simple_messaging_hive.models import execute_action as simple_messaging_execute # pylint: disable=import-outside-toplevel

                    processed = simple_messaging_execute(self, session, action)
                elif self.type == 'http':
                    from http_support.models import execute_action as http_execute # pylint: disable=import-outside-toplevel

                    processed = http_execute(self, session, action)
                elif self.type == 'command_line':
                    from cli_support.models import execute_action as cli_execute # pylint: disable=import-outside-toplevel

                    processed = cli_execute(self, session, action)

                if processed is False:
                    processed = execute_action(self, session, action)

                if processed is False:
                    settings.FETCH_LOGGER().warn('TODO: Process', action)

                log(self.log_id(), 'Executed action.', tags=['integration', 'action'], metadata=action, player=session.player, session=session, game_version=session.game_version)

    def translate_value(self, value, session, scope='session'): # pylint: disable=unused-argument, no-self-use, too-many-branches, too-many-statements
        translated_value = value

        try:
            while '[ME]' in translated_value:
                translated_value = translated_value.replace('[ME]', session.player.identifier)

            while '[LAST-MESSAGE]' in translated_value:
                translated_value = translated_value.replace('[LAST-MESSAGE]', session.last_message())

            while '[LAST-MESSAGE-TYPE]' in translated_value:
                translated_value = translated_value.replace('[LAST-MESSAGE-TYPE]', session.last_message_type())

            while '[LAST-MESSAGE-IMAGE-PATH]' in translated_value:
                translated_value = translated_value.replace('[LAST-MESSAGE-IMAGE-PATH]', session.last_message_image_path())

            if '[LAST-RESPONDER]' in translated_value:
                last_responder = session.last_message_responder()

                if last_responder is not None:
                    while '[LAST-RESPONDER]' in translated_value:
                        translated_value = translated_value.replace('[LAST-RESPONDER]', last_responder)

            while '[MEDIA-PATH:' in translated_value: # [MEDIA-PATH:3] -> /var/www/.../media/file.png
                start = translated_value.find('[MEDIA-PATH:')

                end = translated_value.find(']', start)

                if end != -1:
                    tag = translated_value[start:(end + 1)]

                    identifier = tag[9:-1]

                    media_file = None

                    try:
                        filemodels.File.objects.filter(pk=int(identifier))

                        translated_value = media_file.name
                    except ValueError:
                        translated_value = '(Unable to locate file with identifier "%s".)' % identifier

            while '[SESSION:' in translated_value:
                start = translated_value.find('[SESSION:')

                end = translated_value.find(']', start)

                if end != -1:
                    tag = translated_value[start:(end + 1)]

                    variable = tag[9:-1]

                    variable_value = session.fetch_variable(variable)

                    if variable_value is None:
                        variable_value = '???'

                    translated_value = translated_value.replace(tag, str(variable_value))

            while '[GAME:' in translated_value:
                start = translated_value.find('[GAME:')

                end = translated_value.find(']', start)

                if end != -1:
                    tag = translated_value[start:(end + 1)]

                    variable = tag[6:-1]

                    variable_value = session.game_version.game.fetch_variable(variable)

                    if variable_value is None:
                        variable_value = '???'

                    translated_value = translated_value.replace(tag, str(variable_value))

            while '[PLAYER:' in translated_value:
                start = translated_value.find('[PLAYER:')

                end = translated_value.find(']', start)

                if end != -1:
                    tag = translated_value[start:(end + 1)]

                    variable = tag[8:-1]

                    variable_value = session.player.fetch_variable(variable)

                    if variable_value is None:
                        variable_value = '???'

                    translated_value = translated_value.replace(tag, str(variable_value))

            if translated_value != value:
                metadata = {
                    'original_value': value,
                    'translated_value': translated_value,
                }

                log(self.log_id(), 'Translated value.', tags=['integration', 'translate'], metadata=metadata, player=session.player, session=session, game_version=session.game_version)

        except TypeError:
            pass # Attempting to translate non-string

            # traceback.print_exc()

        return translated_value

    def last_message_for_player(self, player):
        if self.type == 'twilio':
            from twilio_support.models import last_message_for_player # pylint: disable=import-outside-toplevel

            return last_message_for_player(self.game, player)

        if self.type == 'simple_messaging':
            from simple_messaging_hive.models import last_message_for_player # pylint: disable=import-outside-toplevel

            return last_message_for_player(self.game, player)

        return None

    def fetch_statistics(self):
        statistics = {
            'name': self.name,
            'type': self.type,
            'game': self.game,
            'details': []
        }

        now = timezone.now()
        day_start = now - datetime.timedelta(days=1)
        week_start = now - datetime.timedelta(days=7)

        if self.game is not None:
            statistics['details'].append(('Unique Users (All)', len(self.game.unique_users()),))
            statistics['details'].append(('Unique Users (Last 24 Hours)', len(self.game.unique_users(since=day_start)),))
            statistics['details'].append(('Unique Users (Last 7 Days)', len(self.game.unique_users(since=week_start)),))

        if self.type == 'twilio':
            from twilio_support.models import annotate_statistics # pylint: disable=import-outside-toplevel

            annotate_statistics(self, statistics)
        elif self.type == 'simple_messaging':
            from simple_messaging_hive.models import annotate_statistics # pylint: disable=import-outside-toplevel

            annotate_statistics(self, statistics)
        elif self.type == 'http':
            from http_support.models import annotate_statistics # pylint: disable=import-outside-toplevel

            annotate_statistics(self, statistics)
        elif self.type == 'command_line':
            from cli_support.models import annotate_statistics # pylint: disable=import-outside-toplevel

            annotate_statistics(self, statistics)

        return statistics

    def close_player_sessions(self, player_lookup_key, player_lookup_value): # pylint: disable=no-self-use
        player_match = None

        for player in Player.objects.all():
            if player_lookup_key in player.player_state:
                if player.player_state[player_lookup_key] == player_lookup_value:
                    player_match = player

        if player_match is not None:
            for session in player_match.sessions.filter(completed=None):
                session.complete()

def execute_action(integration, session, action): # pylint: disable=unused-argument, too-many-branches, too-many-return-statements, too-many-statements, too-many-locals
    if action['type'] == 'set-variable': # pylint: disable=no-else-return
        scope = 'session'

        payload = {
            'variable': action['variable'],
            'original_value': action['value'],
            'scope': 'session',
            'session': 'session-' + str(session.pk),
            'game': str(session.game_version.game.slug),
            'player': str(session.player.identifier),
            'metadata': action.get('metadata', None),
        }

        if 'scope' in action:
            scope = action['scope']

            payload['scope'] = scope

            action['translated_value'] = integration.translate_value(action['value'], session, scope)

            if scope == 'session':
                session.set_variable(action['variable'], action['translated_value'], metadata=action.get('metadata', None))
            elif scope == 'player':
                session.player.set_variable(action['variable'], action['translated_value'], metadata=action.get('metadata', None), session=session)
            elif scope == 'game':
                session.game_version.game.set_variable(action['variable'], action['translated_value'], metadata=action.get('metadata', None), session=session)

            elif scope == 'active_sessions':
                for other_session in Session.objects.filter(completed=None):
                    other_session.set_variable(action['variable'], action['translated_value'], metadata=action.get('metadata', None))
            elif scope == 'others_active_sessions':
                for other_session in Session.objects.filter(completed=None).exclude(pk=session.pk):
                    other_session.set_variable(action['variable'], action['translated_value'], metadata=action.get('metadata', None))
            elif scope == 'all_sessions':
                for other_session in Session.objects.all():
                    other_session.set_variable(action['variable'], action['translated_value'], metadata=action.get('metadata', None))
            elif scope == 'active_players':
                for player in Player.objects.all():
                    if player.sessions.filter(complete=None).count() > 0:
                        player.set_variable(action['variable'], action['translated_value'], metadata=action.get('metadata', None), session=session)
            elif scope == 'other_active_players':
                for player in Player.objects.exclude(pk=session.player.pk):
                    if player.sessions.filter(complete=None).count() > 0:
                        player.set_variable(action['variable'], action['translated_value'], metadata=action.get('metadata', None), session=session)
            elif scope == 'all_players':
                for player in Player.objects.all():
                    player.set_variable(action['variable'], action['translated_value'], metadata=action.get('metadata', None), session=session)
            elif scope == 'all_activities':
                for activity in Game.objects.all():
                    activity.set_variable(action['variable'], action['translated_value'], metadata=action.get('metadata', None), session=session)
        else:
            action['translated_value'] = integration.translate_value(action['variable'], session)

            session.set_variable(action['value'], action['translated_value'], metadata=action.get('metadata', None))

        payload['value'] = action['translated_value']

        point = DataPoint.objects.create_data_point('hive-set-variable', session.player.identifier, payload, user_agent='Hive Mechanic')
        point.secondary_identifier = payload['variable']
        point.save()

        return True
    elif action['type'] == 'continue':
        return True
    elif action['type'] == 'go-to':
        if 'destination' in action:
            if ('#' in action['destination']) is False:
                action['destination'] = session.complete_identifier(action['destination'])

            session.advance_to(action['destination'])

            return True
    elif action['type'] == 'trigger-interrupt':
        if 'interrupt' in action:
            return session.game_version.interrupt(action['interrupt'], session)
    elif action['type'] == 'end-activity':
        session.complete()

        return True
    elif action['type'] == 'echo': # pylint: disable=no-else-return
        return True
    elif action['type'] == 'nudge': # pylint: disable=no-else-return
        session.nudge()

        return True
    elif action['type'] == 'echo-image':
        return True
    elif action['type'] == 'accept-terms':
        session.accept_terms()

        return True
    elif action['type'] == 'launch-session':
        activity_param = action.get('activity', None)
        player_param = action.get('player', None)


        activity_param = integration.translate_value(activity_param, session)
        player_param = integration.translate_value(player_param, session)

        player_id = player_param

        player = Player.objects.filter(identifier=player_id).first()

        if player is None:
            try:
                parsed = phonenumbers.parse(player_param, settings.PHONE_NUMBER_REGION)

                formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

                player_id = 'twilio_player:%s' % formatted

                player = Player.objects.filter(identifier=player_id).first()

                if player is None:
                    player = Player.objects.create(identifier=player_id)

                    player.player_state = {
                        'twilio_player': formatted
                    }

                    player.save()
            except phonenumbers.phonenumberutil.NumberParseException:
                if player_id == '[PLAYER:SELF]':
                    player = session.player

        activity = Game.objects.filter(slug=activity_param).first()

        if player is not None and activity is not None:
            existing_session = activity.current_active_session(player=player)

            if existing_session is not None:
                existing_session.complete()

            new_session = Session.objects.create(game_version=activity.versions.order_by('-created').first(), player=player, started=timezone.now())

            new_session.nudge()

        return True

    return False
