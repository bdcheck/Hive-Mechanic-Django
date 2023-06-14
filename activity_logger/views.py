# pylint: disable=no-member

import json
import sys
import traceback

from django.views.defaults import server_error
from django.utils import timezone

from .models import LogItem, LogTag

def log_500_error(request, template_name='500.html'): # pylint: disable=too-many-locals
    tag = LogTag.objects.filter(tag='server-error').first()

    if tag is None:
        tag = LogTag.objects.create(tag='server-error', name='Server Error')

    source = 'path:%s' % request.path

    exception_type, exception, exception_traceback = sys.exc_info()
    message = str(exception)

    get_dict = {}
    get_dict.update(request.GET)

    post_dict = {}
    post_dict.update(request.POST)

    meta_dict = {}

    for key in request.META:
        meta_dict[key] = str(request.META[key])

    headers_dict = {}

    for header in request.headers:
        headers_dict[header] = str(request.headers[header])

    metadata = {
        'traceback': traceback.format_exception(exception_type, exception, exception_traceback),
        'path': request.path,
        'method': request.method,
        'GET': get_dict,
        'POST': post_dict,
        'META': meta_dict,
        'HEADERS': headers_dict,
    }

    log_item = LogItem(source=source, message=message, logged=timezone.now())
    log_item.metadata = json.dumps(metadata, indent=2)

    log_item.save()

    log_item.tags.add(tag)

    return server_error(request, template_name)

def intentional_error(request):
    raise Exception('This is an intentional exception!')
