# pylint: disable=line-too-long, no-member

import re

from future.utils import raise_from, raise_with_traceback

import humanize

from django import template
from django.utils import dateparse
from django.utils.safestring import mark_safe

from ..models import SiteSettings
from ..utils import obfuscate_player_id

register = template.Library()

class SetVarNode(template.Node):
    def __init__(self, new_val, var_name):
        self.new_val = new_val
        self.var_name = var_name

    def render(self, context):
        context[self.var_name] = self.new_val
        return ''

@register.tag
def setvar(parser, token): # pylint: disable=unused-argument
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError as exc:
        raise_from(template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0]), exc)

    matched = re.search(r'(.*?) as (\w+)', arg)

    if not matched:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)

    new_val, var_name = matched.groups()

    if not (new_val[0] == new_val[-1] and new_val[0] in ('"', "'")):
        raise_with_traceback(template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name))

    return SetVarNode(new_val[1:-1], var_name)

@register.simple_tag
def builder_site_login_banner():
    settings = SiteSettings.objects.all().order_by('-last_updated').first()

    if settings is None:
        return mark_safe('<h1 style="margin-top: 0px;" class="mdc-typography--headline5">Hive Mechanic</h1>') # nosec

    try:
        if settings.banner is not None:
            return mark_safe('<img src="%s" style="max-width: 100%%;" alt="%s" />' % (settings.banner.url, settings.name)) # nosec
    except ValueError:
        pass

    return mark_safe('<h1 style="margin-top: 0px;" class="mdc-typography--headline5">%s</h1>' % settings.name) # nosec

@register.filter
def obfuscate_identifier(raw_identifier):
    return obfuscate_player_id(raw_identifier)

@register.filter
def humanize_file_size(original_size):
    return humanize.naturalsize(original_size)

@register.filter
def iso_to_datetime(iso_date):
    try:
        return dateparse.parse_datetime(iso_date)
    except TypeError:
        pass

    return iso_date
