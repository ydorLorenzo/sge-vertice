from django.http import HttpResponse
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, redirect
from xhtml2pdf import pisa
from rechum import settings
from .form import SubsidioForm
from .models import Subsidio, Department, Person
from django.contrib.auth.decorators import permission_required
import os

# Create your views here.

@permission_required('subsidio',login_url='home_principal')
def gestionar_subsidio(request):
    list_subsidio = Subsidio.objects.all()
    form = SubsidioForm(request.POST or None)
    context = {'list_subsidio': list_subsidio, 'form': form}
    return render(request, 'Gestionar_Subsidio.html', context)

@permission_required('subsidio',login_url='home_principal')
def adicionar_subsidio(request):
    form = SubsidioForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/subsidios/')
    cal = Subsidio.objects.all()
    context = {'list_subsidio': cal, 'form': form}
    return render(request, 'Gestionar_Subsidio.html', context)

@permission_required('subsidio',login_url='home_principal')
def editar_subsidio(request, pk):
    subsidio = Subsidio.objects.get(id=pk)
    form = SubsidioForm(request.POST or None, instance=subsidio)
    if form.is_valid():
        form.save()
        return redirect('/subsidios/')
    cal = Subsidio.objects.all()
    context = {'list_subsidio': cal, 'form': form, 'edit': pk}
    return render(request, 'Gestionar_Subsidio.html', context)

#@permission_required('subsidio',login_url='home_principal')
class EliminarSubsidio(generic.DeleteView):
    model = Subsidio
    template_name = 'Eliminar_Subsidio.html'
    success_url = reverse_lazy('gestionarSubsidio')

#@permission_required('subsidio',login_url='home_principal')
class DetalleSubsidio(generic.DetailView):
    model = Subsidio
    template_name = 'Detalle_Subsidio.html'


def request_report(fecha_inic, fecha_fin):
    sql = "SELECT ges_trab_trabajador.primer_nombre, ges_trab_trabajador.segundo_nombre, " \
          "ges_trab_trabajador.apellidos, adm_departamento.codigo as dpt_cod, adm_unidadorg.nombre as uo, " \
          "adm_departamento.nombre as nombre_dpto, ges_trab_trabajador.codigo_interno as cod_trab, " \
          "subsidio_subsidio.desde, subsidio_subsidio.hasta, subsidio_subsidio.centro, " \
          "subsidio_subsidio.medico, subsidio_subsidio.fecha, subsidio_subsidio.diagnostico, " \
          "subsidio_subsidio.tipo, subsidio_subsidio.id " \
          "FROM public.adm_unidadorg, public.adm_departamento, public.ges_trab_trabajador, " \
          "public.subsidio_subsidio " \
          "WHERE adm_departamento.unidad_id = adm_unidadorg.id " \
          "AND ges_trab_trabajador.departamento_id = adm_departamento.id " \
          "AND subsidio_subsidio.codigo_trab_id = ges_trab_trabajador.id " \
          "AND ((subsidio_subsidio.desde BETWEEN " +"'"+ fecha_inic +"'"+ "::DATE AND " +"'"+ fecha_fin +"'"+ "::DATE " \
          "OR subsidio_subsidio.hasta BETWEEN " + "'" + fecha_inic + "'" + "::DATE AND " + "'" + fecha_fin + "'" + "::DATE)" \
          "OR (subsidio_subsidio.desde < " + "'" + fecha_inic + "'" + "::DATE " \
          "AND subsidio_subsidio.hasta > " + "'" + fecha_inic + "'" + "::DATE))" \
          "GROUP BY adm_unidadorg.nombre, ges_trab_trabajador.primer_nombre, ges_trab_trabajador.segundo_nombre, " \
          "ges_trab_trabajador.apellidos, adm_departamento.codigo, adm_departamento.nombre, " \
          "ges_trab_trabajador.codigo_interno, subsidio_subsidio.desde, subsidio_subsidio.hasta, " \
          "subsidio_subsidio.centro, subsidio_subsidio.medico, subsidio_subsidio.fecha, " \
          "subsidio_subsidio.diagnostico, subsidio_subsidio.tipo, subsidio_subsidio.id " \
          "ORDER BY adm_departamento.codigo ASC, ges_trab_trabajador.codigo_interno DESC;"
    result = Subsidio.objects.raw(sql)
    codes_personas = []
    departments = []
    subsidios = []
    for element in result:
        flag = False
        for depa in departments:
            if depa.codigo == element.dpt_cod:
                flag = True
                break
        if not flag:
            departments.append(Department(codigo=element.dpt_cod, nombre=element.nombre_dpto, personas=[], suma_area=0,
                                          cant_registros=0))

    for element in result:
        flag = False
        for cod in codes_personas:
            if cod.codigo == element.cod_trab:
                flag = True
                break
        if not flag:
            codes_personas.append(
                Person(codigo=element.cod_trab, nombre=element.primer_nombre + ' ' + element.apellidos, subsidios=[],
                       suma_cod=0, cant_registros=0))

    for element in result:
        subsidios.append(element)

    for code in codes_personas:
        for subsidio in subsidios:
            if subsidio.cod_trab == code.codigo:
                code.subsidios.append(subsidio)
                code.cant_registros += 1
                code.suma_cod += subsidio.dias

    for dep in departments:
        for code in codes_personas:
            if code.subsidios[0].dpt_cod == dep.codigo:
                dep.personas.append(code)
                dep.cant_registros += code.cant_registros
                dep.suma_area += code.suma_cod

    cant_registros_bd = 0
    total = 0
    for d in departments:
        cant_registros_bd += d.cant_registros
        total += d.suma_area

    return {'departments': departments, 'cant_registros_bd': cant_registros_bd, 'total': total,
            'fecha_inic': fecha_inic, 'fecha_fin': fecha_fin}

#@permission_required('subsidio',login_url='home_principal')
def reporte(request):
    fecha_ini = request.POST['fecha_inic']
    fecha_fin = request.POST['fecha_fin']
    if fecha_ini == '' or fecha_fin == '':
        error_subsidio = True
        context = {'error_subsidio': error_subsidio}
        return render(request, 'home.html', context)
    else:
        return render(request, 'Reporte_Subsidios.html', request_report(fecha_ini, fecha_fin))


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # use short variable names
    s_url = settings.STATIC_URL  # Typically /static/
    s_root = settings.STATIC_ROOT  # Typically /home/userX/project_static/
    m_url = settings.MEDIA_URL  # Typically /static/media/
    # Typically /home/userX/project_static/media/
    m_root = settings.MEDIA_ROOT

    # convert URIs to absolute system paths
    if uri.startswith(m_url):
        path = os.path.join(m_root, uri.replace(m_url, ""))
    elif uri.startswith(s_url):
        path = os.path.join(s_root, uri.replace(s_url, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (s_url, m_url)
        )
    return path

#@permission_required('subsidio',login_url='home_principal')
def exportar(request):
    fecha_inic = request.POST['fecha_inic']
    fecha_fin = request.POST['fecha_fin']
    template_path = 'Reporte_Subsidios_Template.html'
    context = request_report(fecha_inic, fecha_fin)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte_Subsidios.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisastatus = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisastatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisastatus.err,
                                                                               html))
    return response
