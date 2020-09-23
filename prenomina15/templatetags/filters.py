from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='replace')
@stringfilter
def replace(value):
    return value.replace(",", ".")


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='convert2char')
def convert2char(number):
    return chr(65+number)
