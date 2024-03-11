# pylint: disable=wrong-import-position

import sys

if sys.version_info[0] > 2:
    from django.urls import re_path as url
else:
    from django.conf.urls import url

from .views import intentional_error

urlpatterns = [
    url(r'^error$', intentional_error, name='intentional_error'),
]
