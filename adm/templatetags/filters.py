from datetime import datetime

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


@register.filter(name='days_in_month')
def days_in_month(my_date):
    current_date = datetime.strptime(my_date, '%Y-%m-%d')
    return int((datetime(current_date.year, current_date.month, 1) - datetime(
        current_date.year if current_date.month < 12 else current_date.year + 1,
        0 if current_date.month == 12 else current_date.month + 1, 1)).days)
