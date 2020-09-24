import os
from . import settings

from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.html import escape
from django.forms.fields import DateField, DateTimeField
from xhtml2pdf import pisa


def add_required_label_tag(fn):
    """
    Adds the 'required' CSS class, and an asterisk to required field labels.
    :param fn: original function
    """
    def required_label_tag(self, contents=None, attrs=None, label_suffix=''):
        contents = contents or escape(self.label)
        attrs = {'class': 'col-form-label font-sm'}
        if self.field.required:
            if not self.label.endswith(" *"):
                self.label += " *"
                contents += " *"
            attrs['class'] += ' required'
        return fn(self, contents, attrs, label_suffix)
    return required_label_tag


def add_bootstrap_css_field_classes(fn):
    def as_widget_with_bootstrap_classes(self, widget=None, attrs=None, only_initial=False):
        if attrs is None:
            attrs = {'class': 'form-control'}
        if isinstance(self.field, DateField) or isinstance(self.field, DateTimeField):
            attrs = {'class': 'inline-date form-control', 'autocomplete': 'off'}
        if self.field.required:
            attrs.update({
                'oninvalid': "this.setCustomValidity('Este campo es requerido.')",
                'oninput': "setCustomValidity('')"
            })
        return fn(self, widget, attrs, only_initial)
    return as_widget_with_bootstrap_classes


def decorate_bound_field():
    from django.forms.forms import BoundField
    BoundField.label_tag = add_required_label_tag(BoundField.label_tag)
    BoundField.as_widget = add_bootstrap_css_field_classes(BoundField.as_widget)


def link_callback(uri, rel):
    """
    Convierte las URIs del HTML en rutas absolutas del sistema para que
    xhtml2pdf pueda acceder a esos recursos.
    :author Yanet
    """

    # use short variable names
    s_url = settings.STATIC_URL     # Typically /static/
    s_root = settings.STATIC_ROOT   # Typically /home/userX/project_static/
    m_url = settings.MEDIA_URL      # Typically /static/media/
    m_root = settings.MEDIA_ROOT    # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(m_url):
        path = os.path.join(m_root, uri.replace(m_url, ""))
    elif uri.startswith(s_url):
        path = os.path.join(s_root, uri.replace(s_url, ""))
    else:
        return uri                  # handle absolute uri (ie: http://some.tld/foo.png)
    # make sure the file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (s_url, m_url)
        )
    return path


def generate_pisa_report(context, template_path, title):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{title}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisa_status.err:
        return HttpResponse(f'Hubo algún error de código {pisa_status.err} <pre>{html}</pre>')
    return response
