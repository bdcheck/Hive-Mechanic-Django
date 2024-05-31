# pylint: disable=line-too-long, no-member, len-as-condition

import datetime

import humanize
import numpy

from django.utils import timezone

from simple_dashboard.models import DashboardSignal

from integrations.models import Integration
from twilio_support.models import IncomingMessage, OutgoingMessage, OutgoingCall, IncomingCallResponse

from .models import SiteSettings, Session

def dashboard_signals():
    signals = [{
        'name': 'Message of the Day',
        'refresh_interval': 300,
        'configuration': {
            'widget_columns': 12
        },
        'hide_title': True,
    }, {
        'name': 'Activity Sessions',
        'refresh_interval': 300,
        'configuration': {
            'widget_columns': 4
        }
    }, {
        'name': 'Message Traffic',
        'refresh_interval': 300,
        'configuration': {
            'widget_columns': 4
        }
    }]

    for integration in Integration.objects.all():
        signals.append({
            'name': 'Integration: %s' % integration.name,
            'refresh_interval': 300,
            'configuration': {
                'widget_columns': 4,
                'integration_id': integration.pk,
            }
        })

    if OutgoingCall.objects.all().count() > 0:
        signals.append({
            'name': 'Voice Calls',
            'refresh_interval': 300,
            'configuration': {
                'widget_columns': 4
            }
        })

    return signals


def dashboard_template(signal_name):
    if signal_name == 'Message of the Day':
        return 'dashboard/simple_dashboard_widget_motd.html'

    if signal_name == 'Activity Sessions':
        return 'dashboard/simple_dashboard_widget_activity_sessions.html'

    if signal_name == 'Message Traffic':
        return 'dashboard/simple_dashboard_widget_message_traffic.html'

    if signal_name == 'Voice Calls':
        return 'dashboard/simple_dashboard_widget_voice_calls.html'

    if signal_name.startswith('Integration: '):
        signal = DashboardSignal.objects.filter(name=signal_name).first()

        if signal is not None and signal.active is True:
            integration = Integration.objects.filter(pk=signal.configuration.get('integration_id', -1)).first()

            if integration is not None:
                return 'dashboard/simple_dashboard_widget_integration.html'

    return None

def update_dashboard_signal_value(signal_name): # pylint: disable=too-many-locals, too-many-branches, too-many-statements, too-many-return-statements
    now = timezone.now()

    if signal_name == 'Message of the Day':
        site_settings = SiteSettings.objects.all().order_by('-last_updated').first()

        if site_settings is not None:
            motd = site_settings.message_of_the_day

            motd_signal = DashboardSignal.objects.filter(package='builder', name='Message of the Day').first()

            if motd_signal is not None and motd_signal.latest_value() is not None:
                if motd == motd_signal.latest_value().fetch_value():
                    return None

            return motd

    if signal_name == 'Activity Sessions':
        value = {
            'active_count': Session.objects.filter(completed=None).count(),
            'completed_count': Session.objects.exclude(completed=None).count(),
        }

        oldest_active = Session.objects.filter(completed=None).order_by('started').first()

        if oldest_active is not None:
            value['oldest_active_session'] = '%s (started %s)' % (oldest_active.game_version.game, oldest_active.started)

        most_recent = Session.objects.all().order_by('-started').first()

        if most_recent is not None:
            value['most_recent'] = '%s (started %s)' % (most_recent.game_version.game, most_recent.started)

        durations = []

        for session in Session.objects.exclude(completed=None):
            durations.append((session.completed - session.started).total_seconds())

        if len(durations) > 0:
            mean_duration = numpy.mean(durations)

            delta = datetime.timedelta(seconds=mean_duration)

            value['average_session_duration_humanized'] = humanize.naturaldelta(delta)
            value['average_session_duration_seconds'] = mean_duration
        else:
            value['average_session_duration_humanized'] = 'Unknown, no sessions completed  yet.'

        return value

    if signal_name == 'Message Traffic':
        value = {
            'incoming_count': IncomingMessage.objects.all().count(),
            'outgoing_count': OutgoingMessage.objects.exclude(sent_date=None).filter(errored=False).count(),
            'pending_count': OutgoingMessage.objects.filter(sent_date=None, send_date__gte=now, errored=False).count(),
            'error_count': OutgoingMessage.objects.filter(errored=True).count(),
        }

        site_settings = SiteSettings.objects.all().order_by('-last_updated').first()

        if site_settings is not None:
            if site_settings.total_message_limit is not None:
                value['message_limit'] = site_settings.total_message_limit

                incoming_messages = IncomingMessage.objects.all()
                outgoing_messages = OutgoingMessage.objects.all()
                outgoing_calls = OutgoingCall.objects.all()

                if site_settings.count_messages_since is not None:
                    incoming_messages = IncomingMessage.objects.filter(receive_date__gte=site_settings.count_messages_since)
                    outgoing_messages = OutgoingMessage.objects.filter(sent_date__gte=site_settings.count_messages_since)
                    outgoing_calls = OutgoingCall.objects.filter(sent_date__gte=site_settings.count_messages_since)

                    value['message_limit_reset'] = '%s' % site_settings.count_messages_since.date()

                messages_sent = incoming_messages.count() + outgoing_messages.count() + outgoing_calls.count()
                messages_remaining = site_settings.total_message_limit - messages_sent

                if messages_remaining < site_settings.total_message_limit / 4:
                    value['messages_remaining_warning'] = True

                value['messages_remaining'] = messages_remaining

        return value

    if signal_name == 'Hive Mechanic API Calls':
        pass


    if signal_name.startswith('Integration: '):
        signal = DashboardSignal.objects.filter(name=signal_name).first()

        if signal is not None and signal.active is True:
            integration = Integration.objects.filter(pk=signal.configuration.get('integration_id', -1)).first()

            if integration is not None:
                statistics = integration.fetch_statistics()

                value = {
                    'type': statistics.get('type', 'Unknown integration type'),
                    'details': statistics.get('details', []),
                    'activity': '%s' % statistics.get('game', 'Unknown Activity')
                }

                return value

    if signal_name == 'Voice Calls':
        value = {
            'outgoing_turns': OutgoingCall.objects.all().count(),
            'incoming_turns': IncomingCallResponse.objects.all().count(),
        }

        return value

    return None
