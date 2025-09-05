# pylint: disable=no-member

import io
import json

import sh

# from py_mini_racer import MiniRacer

from django.contrib.staticfiles import finders
from django.template.loader import render_to_string

# def fetch_cytoscape(definition, simplify=False): # pylint: disable=too-many-locals
#     from .models import InteractionCard # pylint: disable=import-outside-toplevel, cyclic-import
#
#     env_path = finders.find('builder-js/vendor/racer_env.js')
#     slugify_path = finders.find('builder-js/vendor/slugify.js')
#     node_path = finders.find('builder-js/js/app/cards/node.js')
#     sequence_path = finders.find('builder-js/js/app/sequence.js')
#
#     js_context = MiniRacer()
#
#     with io.open(env_path, 'r', encoding='utf-8') as env_file:
#         env_source = ''.join(env_file.readlines())
#
#         js_context.eval(env_source)
#
#     with io.open(slugify_path, 'r', encoding='utf-8') as slugify_file:
#         slugify_source = ''.join(slugify_file.readlines())
#
#         js_context.eval(slugify_source)
#
#     js_context.eval('slugifyExt = slugify')
#
#     with io.open(node_path, 'r', encoding='utf-8') as node_file:
#         node_source = ''.join(node_file.readlines())
#
#         js_context.eval(node_source)
#
#     with io.open(sequence_path, 'r', encoding='utf-8') as sequence_file:
#         sequence_source = ''.join(sequence_file.readlines())
#
#         js_context.eval(sequence_source)
#
#     for card in InteractionCard.objects.filter(enabled=True):
#         with io.open(card.client_implementation.path, 'r', encoding='utf-8') as client_file:
#             client_source = ''.join(client_file.readlines())
#
#             js_context.eval(client_source)
#
#     context = {
#         'definition': json.dumps(definition),
#         'simplify': simplify
#     }
#
#     script_source = render_to_string('utils/cytoscape_convert.js', context)
#
#     result = js_context.eval(script_source)
#
#     return json.loads(result)

def fetch_cytoscape_node(definition, simplify=False): # pylint: disable=too-many-locals
    from .models import InteractionCard # pylint: disable=import-outside-toplevel, cyclic-import

    env_path = finders.find('builder-js/vendor/racer_env.js')
    slugify_path = finders.find('builder-js/vendor/slugify.js')
    node_path = finders.find('builder-js/js/app/cards/node.js')
    sequence_path = finders.find('builder-js/js/app/sequence.js')

    full_script = ''

    with io.open(env_path, 'r', encoding='utf-8') as env_file:
        full_script += ''.join(env_file.readlines())

    full_script += 'var slugifyExt = require("' + slugify_path + '")\n'
    full_script += 'require("' + node_path + '")\n'
    full_script += 'require("' + sequence_path + '")\n'

    for card in InteractionCard.objects.filter(enabled=True):
        full_script += 'require("' + card.client_implementation.path + '")\n'

    full_script += '\n'

    context = {
        'definition': json.dumps(definition),
        'simplify': simplify
    }

    full_script += render_to_string('utils/cytoscape_convert_node.js', context)

    full_script += '\n'

    result_io = io.StringIO()

    try:
        sh.nodejs(_in=full_script, _out=result_io)
    except sh.ErrorReturnCode_1:
        return None

    return json.loads(result_io.getvalue())

def obfuscate_player_id(raw_identifier):
    obfuscated = ''

    number_count = 0

    for character in raw_identifier[::-1]:
        if character.isdigit():
            if number_count < 4:
                obfuscated = character + obfuscated

                number_count += 1
            else:
                obfuscated = 'X' + obfuscated
        else:
            obfuscated = character + obfuscated

    return obfuscated
