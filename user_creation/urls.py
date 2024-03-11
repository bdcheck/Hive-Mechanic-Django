# pylint: disable=line-too-long, wrong-import-position

import sys

if sys.version_info[0] > 2:
    from django.urls import re_path as url
else:
    from django.conf.urls import url

from .views import user_required_terms, user_request_access, user_account, user_terms_view

urlpatterns = [
    url(r'terms/view$', user_terms_view, name='user_terms_view'),
    url(r'terms$', user_required_terms, name='user_required_terms'),
    url(r'request$', user_request_access, name='user_request_access'),
    url(r'account$', user_account, name='user_account'),
]
