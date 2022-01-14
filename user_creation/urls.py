# pylint: disable=line-too-long

from django.conf.urls import url

from .views import user_required_terms, user_request_access

urlpatterns = [
    url(r'terms$', user_required_terms, name='user_required_terms'),
    url(r'request$', user_request_access, name='user_request_access'),
]
