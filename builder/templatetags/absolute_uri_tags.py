from django.template import Library

register = Library()

@register.simple_tag
def absolute_uri(url, request):
    return request.build_absolute_uri(url)
