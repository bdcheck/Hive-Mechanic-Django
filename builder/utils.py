# pylint: disable=no-member
import json

from py_mini_racer import MiniRacer

from django.contrib.staticfiles import finders
from django.template.loader import render_to_string

def fetch_cytoscape(definition): # pylint: disable=too-many-locals
    from .models import InteractionCard # pylint: disable=import-outside-toplevel, cyclic-import

    env_path = finders.find('builder-js/vendor/racer_env.js')
    node_path = finders.find('builder-js/js/app/cards/node.js')
    sequence_path = finders.find('builder-js/js/app/sequence.js')

    js_context = MiniRacer()

    with open(env_path, 'r') as env_file:
        env_source = ''.join(env_file.readlines())

        js_context.eval(env_source)

    with open(node_path, 'r') as node_file:
        node_source = ''.join(node_file.readlines())

        js_context.eval(node_source)

    with open(sequence_path, 'r') as sequence_file:
        sequence_source = ''.join(sequence_file.readlines())

        js_context.eval(sequence_source)

    for card in InteractionCard.objects.filter(enabled=True):
        with open(card.client_implementation.path, 'r') as client_file:
            client_source = ''.join(client_file.readlines())

            js_context.eval(client_source)

    context = {
        'definition': json.dumps(definition)
    }

    script_source = render_to_string('utils/cytoscape_convert.js', context)

    result = js_context.eval(script_source)

    return json.loads(result)