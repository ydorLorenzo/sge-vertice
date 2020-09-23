from django import template
register = template.Library()


@register.simple_tag
def get_field_verbose_name(instance, field_name):
    """
    Returns the verbose name for a field
    :param instance: the object instance
    :param field_name: the name of the field
    :return: the verbose name of the field
    """
    return instance._meta.get_field(field_name).verbose_name.title()


@register.filter(name='get_model_verbose_name')
def get_model_verbose_name(instance):
    return instance._meta.verbose_name
