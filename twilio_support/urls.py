# pylint: disable=wrong-import-position

import sys

from .views import incoming_twilio, incoming_twilio_call

if sys.version_info[0] > 2:
    from django.urls import re_path

    urlpatterns = [
        re_path(r'^incoming.xml$', incoming_twilio, name='incoming_twilio'),
        re_path(r'^call-incoming.xml$', incoming_twilio_call, name='incoming_twilio_call'),
    ]
else:
    from django.conf.urls import url

    urlpatterns = [
        url(r'^incoming.xml$', incoming_twilio, name='incoming_twilio'),
        url(r'^call-incoming.xml$', incoming_twilio_call, name='incoming_twilio_call'),
    ]
