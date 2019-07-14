from django.conf.urls import url

from .views import incoming_twilio

urlpatterns = [
    url(r'^incoming.xml$', incoming_twilio, name='incoming_twilio'),
]
