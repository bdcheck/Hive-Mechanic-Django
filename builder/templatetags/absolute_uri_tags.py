from django.conf import settings
from django.template import Library

register = Library()

@register.simple_tag
def absolute_uri(url, request): # pylint: disable=unused-argument
    return '%s%s' % (settings.SITE_URL, url)
