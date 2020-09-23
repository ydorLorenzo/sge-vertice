import unicodedata

from django import template

register = template.Library()


@register.filter("strip_accents")
def strip_accents(value):
    # if type(value) == str:
    #     return value
    return ''.join((c for c in unicodedata.normalize('NFD', value) if unicodedata.category(c) != 'Mn'))
