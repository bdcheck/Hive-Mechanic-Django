# pylint: disable=line-too-long

from django.conf.urls import url

from .views import user_required_terms

urlpatterns = [
    url(r'required$', user_required_terms, name='user_required_terms'),
]
