import sys

from django.contrib import admin
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

if sys.version_info[0] > 2:
    from django.urls import re_path, include

    urlpatterns = [
        re_path(r'^accounts/', include('django.contrib.auth.urls')),
        re_path(r'^admin/', admin.site.urls),
        re_path(r'^data/', include('passive_data_kit.urls')),
        re_path(r'^builder/', include('builder.urls')),
        re_path(r'^quicksilver/', include('quicksilver.urls')),
        re_path(r'^twilio/', include('twilio_support.urls')),
        re_path(r'^http/', include('http_support.urls')),
        re_path(r'^http/', include('http_support.urls')),
        re_path(r'^access/', include('user_creation.urls')),
        re_path(r'^monitor/', include('nagios_monitor.urls')),
        re_path(r'^activity/', include('activity_logger.urls')),
        re_path(r'^messages/', include('simple_messaging.urls')),
    ]

    urlpatterns += [re_path(r'^.*$', RedirectView.as_view(pattern_name='builder_home', permanent=False), name='index')]
else:
    from django.conf.urls import url, include

    urlpatterns = [
        url(r'^accounts/', include('django.contrib.auth.urls')),
        url(r'^admin/', admin.site.urls),
        url(r'^data/', include('passive_data_kit.urls')),
        url(r'^builder/', include('builder.urls')),
        url(r'^quicksilver/', include('quicksilver.urls')),
        url(r'^twilio/', include('twilio_support.urls')),
        url(r'^http/', include('http_support.urls')),
        url(r'^http/', include('http_support.urls')),
        url(r'^access/', include('user_creation.urls')),
        url(r'^monitor/', include('nagios_monitor.urls')),
        url(r'^activity/', include('activity_logger.urls')),
        url(r'^messages/', include('simple_messaging.urls')),
    ]

    urlpatterns += [url(r'^.*$', RedirectView.as_view(pattern_name='builder_home', permanent=False), name='index')]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500 = 'activity_logger.views.log_500_error'
