# pylint: disable=line-too-long

import json
import os

from future.utils import raise_from

from django import template
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static

register = template.Library()

def base_static_path(original_path):
    file_path = original_path.replace('/static/builder-react/static', 'builder-react')

    return static(file_path)

@register.tag(name="react_asset")
def react_asset(parser, token): # pylint: disable=unused-argument
    try:
        tag_name, filename = token.split_contents() # pylint: disable=unused-variable
    except ValueError as value_exc:
        raise_from(template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0]), value_exc)

    return ReactAssetNode(filename)

class ReactAssetNode(template.Node):
    def __init__(self, filename):
        self.filename = template.Variable(filename)

    def render(self, context):
        filename = self.filename.resolve(context)

        manifest_path = os.path.abspath(os.path.join(settings.STATIC_ROOT, 'builder-react'))
        manifest_path = os.path.abspath(os.path.join(manifest_path, 'asset-manifest.json'))

        with open(manifest_path) as manifest_file:
            manifest = json.load(manifest_file)

            file_path = manifest[filename].replace('/static/builder/react-app', 'builder-react')

            return static(file_path)

        return None

@register.tag(name="react_header_tags")
def react_header_tags(parser, token): # pylint: disable=unused-argument
    return ReactHeaderTagsNode()

class ReactHeaderTagsNode(template.Node):
    def __init__(self):
        pass

    def render(self, context):
        manifest_path = os.path.abspath(os.path.join(settings.STATIC_ROOT, 'builder-react'))
        manifest_path = os.path.abspath(os.path.join(manifest_path, 'asset-manifest.json'))

        output = '<!-- Start Autogenerated React Tags -->\n'

        with open(manifest_path) as manifest_file:
            manifest = json.load(manifest_file)

            for key, path in list(manifest.items()):
                if key.endswith('css'):
                    output += '<link href="' + base_static_path(path) + '" rel="stylesheet">\n'

        output += '<!-- End Autogenerated React Tags -->'

        return output

@register.tag(name="react_footer_tags")
def react_footer_tags(parser, token): # pylint: disable=unused-argument
    return ReactFooterTagsNode()

class ReactFooterTagsNode(template.Node):
    def __init__(self):
        pass

    def render(self, context):
        manifest_path = os.path.abspath(os.path.join(settings.STATIC_ROOT, 'builder-react'))
        manifest_path = os.path.abspath(os.path.join(manifest_path, 'asset-manifest.json'))

        output = '<!-- Start Autogenerated React Tags -->\n'

        with open(manifest_path) as manifest_file:
            manifest = json.load(manifest_file)

            for key, path in list(manifest.items()):
                if key == 'main.js':
                    output += '<script src="' + base_static_path(path) + '"></script>\n'
                elif key.startswith('static/js/') and key.endswith('.js'):
                    output += '<script src="' + base_static_path(path) + '"></script>\n'

        output += '<!-- End Autogenerated React Tags -->'

        return output
