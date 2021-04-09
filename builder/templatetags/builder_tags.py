# pylint: disable=line-too-long

import re

from future.utils import raise_from, raise_with_traceback

from django import template

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
