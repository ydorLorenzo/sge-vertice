from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def url_sge(url_name, *args):
    """
    Etiqueta que cumple la misma función que la tradicional url pero con esta no da warnings
    al usar filtros en el url_name.

    :param url_name: El nombre de la vista
    :param args: Los argumentos necesarios para la vista (pk si es vista de detalles u otros)
    :return: la url correspondiente a ese nombre de vista
    """
    return reverse(url_name, args=args)


@register.filter(name="current_url")
def current_url(my_string):
    """
    Para vistas del modelo CRUD de la forma {nombre-modelo}_{crud} separa el nombre del modelo
    del nombre del tipo de vista para ese modelo. Ej. detail, delete, create, update y también el list.

    :param my_string: Nombre de la vista
    :return: Nombre del tipo de vista para modelo CRUD
    """
    return my_string.split("_")[1]


@register.filter(name="current_model_url")
def current_model_url(my_string):
    """
    Para vistas del modelo CRUD de la forma {nombre-modelo}_{crud} separa el nombre del modelo
    del nombre del tipo de vista para ese modelo. Ej. detail, delete, create, update y también el list.

    :param my_string: Nombre de la vista
    :return: Nombre del modelo
    """
    return my_string.split("_")[0]


@register.filter(name="get_url_name")
def get_url_name(my_string, suffix):
    """
    Para generar las vistas del CRUD a partir de la vista actual.

    :param my_string: Nombre de la vista
    :param suffix: Sufijo para el tipo de vista del CRUD
    :return: Nombre de la nueva vista
    """
    url = my_string.split("_")
    url[1] = suffix
    return '_'.join(url)


@register.filter(name="is_x_menu")
def is_x_menu(my_string, menu):
    """
    Para generar las vistas del CRUD a partir de la vista actual.

    :param my_string: Nombre de la vista
    :param menu: Nombre del menu
    :return: Nombre de la nueva vista
    """
    model_url = my_string.split("_")[0]
    menu_list = []
    if menu == 'ot':
        menu_list = ['area', 'servicio', 'ot']
    elif menu == 'actividad':
        menu_list = ['tipoactividad', 'actividad']
    elif menu == 'trabajador':
        menu_list = ['trabajador']
    return model_url in menu_list


@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):
    """
    Crea una URL (conteniendo solo la cadena de queries[preguntas] [incluyendo "?"])
    derivado de la cadena de queries que contiene la URL actual, actualizando los valores
    que cambian.

    Por ejemplo (imagina que la URL es ``/abc/?page=2&q=Juan+Manuel``)::
        {% querystring "q"="Diego" "order"=id %}
        ?page=2&q=Diego&order=id
    """
    request = context['request']
    updated = request.GET.copy()
    # tiene que iterarse y no usar .update porque es un QueryDict y no un dict
    for k, v in kwargs.items():
        updated[k] = v
    return '?{}'.format(updated.urlencode()) if updated else ''
