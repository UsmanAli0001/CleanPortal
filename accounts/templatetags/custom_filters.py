from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='divide')
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
import json
from django.utils.safestring import mark_safe

@register.filter(name='to_json')
def to_json(value):
    return mark_safe(json.dumps(value))

@register.filter(name='split_comma')
def split_comma(value):
    if not value:
        return []
    return [s.strip() for s in value.split(',') if s.strip()]
