from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='replace')
@stringfilter
def replace(value):
    return value.replace(",", ".")
