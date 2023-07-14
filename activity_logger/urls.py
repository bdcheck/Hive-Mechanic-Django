from django.conf.urls import url

from .views import intentional_error

urlpatterns = [
    url(r'^error$', intentional_error, name='intentional_error'),
]
