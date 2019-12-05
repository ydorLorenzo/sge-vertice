import os

from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.urls.base import reverse_lazy
from django.views import generic
from xhtml2pdf import pisa

from datos_prenom.form import TrabajoExtraordinarioForm, AlimentacionForm, VacacionesForm
from datos_prenom.models import TrabajoExtraordinario, Alimentacion, Vacaciones

# Create your views here.
from plantilla.models import Unidad, Dpto, Registro
from rechum import settings


def gestionar_trabajo_extra(request):
    list_trabajo_extra = TrabajoExtraordinario.objects.all()
    form = TrabajoExtraordinarioForm(request.POST or None)
    context = {'list_trabajo_extra': list_trabajo_extra, 'form': form}
    return render(request, 'Gestionar_TrabajoExtra.html', context)


def adicionar_trabajo_extra(request):
    form = TrabajoExtraordinarioForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/trabajo_extraordinario/')
    cal = TrabajoExtraordinario.objects.all()
    context = {'list_trabajo_extra': cal, 'form': form}
    return render(request, 'Gestionar_TrabajoExtra.html', context)


def editar_trabajo_extra(request, pk):
    trabajo_extra = TrabajoExtraordinario.objects.get(id=pk)
    form = TrabajoExtraordinarioForm(request.POST or None, instance=trabajo_extra)
    if form.is_valid():
        form.save()
        return redirect('/trabajo_extraordinario/')
    cal = TrabajoExtraordinario.objects.all()
    context = {'list_trabajo_extra': cal, 'form': form, 'edit': pk}
    return render(request, 'Gestionar_TrabajoExtra.html', context)


class EliminarTrabajoExtra(generic.DeleteView):
    model = TrabajoExtraordinario
    template_name = 'Eliminar_TrabajoExtra.html'
    success_url = reverse_lazy('gestionarTrabajoExtra')


class DetalleTrabajoExtra(generic.DetailView):
    model = TrabajoExtraordinario
    template_name = 'Detalle_TrabajoExtra.html'


##############################################################


def gestionar_alimentacion(request):
    list_alimentacion = Alimentacion.objects.all()
    form = AlimentacionForm(request.POST or None)
    context = {'list_alimentacion': list_alimentacion, 'form': form}
    return render(request, 'Gestionar_Alimentacion.html', context)


def adicionar_alimentacion(request):
    form = AlimentacionForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/alimentacion/')
    cal = Alimentacion.objects.all()
    context = {'list_alimentacion': cal, 'form': form}
    return render(request, 'Gestionar_Alimentacion.html', context)


def editar_alimentacion(request, pk):
    alimentacion = Alimentacion.objects.get(id=pk)
    form = AlimentacionForm(request.POST or None, instance=alimentacion)
    if form.is_valid():
        form.save()
        return redirect('/alimentacion/')
    cal = Alimentacion.objects.all()
    context = {'list_alimentacion': cal, 'form': form, 'edit': pk}
    return render(request, 'Gestionar_Alimentacion.html', context)


class EliminarAlimentacion(generic.DeleteView):
    model = Alimentacion
    template_name = 'Eliminar_Alimentacion.html'
    success_url = reverse_lazy('gestionarAlimentacion')


class DetalleAlimentacion(generic.DetailView):
    model = Alimentacion
    template_name = 'Detalle_Alimentacion.html'

    ##############################################################


def gestionar_vacaciones(request):
    list_vacaciones = Vacaciones.objects.all()
    form = VacacionesForm(request.POST or None)
    context = {'list_vacaciones': list_vacaciones, 'form': form}
    return render(request, 'Gestionar_Vacaciones.html', context)


def adicionar_vacaciones(request):
    form = VacacionesForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/vacaciones/')
    cal = Vacaciones.objects.all()
    context = {'list_vacaciones': cal, 'form': form}
    return render(request, 'Gestionar_Vacaciones.html', context)


def editar_vacaciones(request, pk):
    vacaciones = Vacaciones.objects.get(id=pk)
    form = VacacionesForm(request.POST or None, instance=vacaciones)
    if form.is_valid():
        form.save()
        return redirect('/vacaciones/')
    cal = Vacaciones.objects.all()
    context = {'list_vacaciones': cal, 'form': form, 'edit': pk}
    return render(request, 'Gestionar_Vacaciones.html', context)


class EliminarVacaciones(generic.DeleteView):
    model = Vacaciones
    template_name = 'Eliminar_Vacaciones.html'
    success_url = reverse_lazy('gestionarVacaciones')


class DetalleVacaciones(generic.DetailView):
    model = Vacaciones
    template_name = 'Detalle_Vacaciones.html'

    ##############################################################

    # Este metodo devuelve más datos de los necesarios
    # pero se dejo asi por si hay que agregarle datos al reporte despues.


def request_report(fecha_inic, fecha_fin):
    sql = "SELECT " \
          "adm_unidadorg.id AS id_uo, adm_unidadorg.nombre AS nombre_uo, adm_departamento.id AS id_dpto, " \
          "adm_departamento.codigo, adm_departamento.nombre AS nombre_dep, adm_departamento.unidad_id, " \
          "ges_trab_trabajador.id, ges_trab_trabajador.primer_nombre AS nombre, ges_trab_trabajador.segundo_nombre, " \
          "ges_trab_trabajador.apellidos, ges_trab_trabajador.org_plantilla, ges_trab_trabajador.codigo_interno, " \
          "ges_trab_trabajador.departamento_id, datos_prenom_vacaciones.codigo_trab_id, " \
          "datos_prenom_vacaciones.cant_dias, datos_prenom_vacaciones.fecha " \
          "FROM " \
          "public.ges_trab_trabajador, public.datos_prenom_vacaciones, public.adm_departamento, public.adm_unidadorg " \
          "WHERE " \
          "ges_trab_trabajador.departamento_id = adm_departamento.id " \
          "AND ges_trab_trabajador.id = datos_prenom_vacaciones.codigo_trab_id " \
          "AND adm_unidadorg.id = adm_departamento.unidad_id " \
          "AND datos_prenom_vacaciones.fecha " \
          "BETWEEN " + "'" + fecha_inic + "'" + "::DATE AND " + "'" + fecha_fin + "'" + "::DATE " \
          "GROUP BY adm_unidadorg.id, adm_departamento.id, ges_trab_trabajador.id, " \
          "datos_prenom_vacaciones.codigo_trab_id, datos_prenom_vacaciones.cant_dias, " \
          "datos_prenom_vacaciones.fecha " \
          "ORDER BY " \
          "ges_trab_trabajador.org_plantilla ASC;"

    result = Vacaciones.objects.raw(sql)
    departamentos = []
    unidades = []
    trabajadores = []

    num = 0
    for element in result:
        flag = False
        for depa in unidades:
            if depa.codigo == element.id_uo:
                flag = True
                break
        if not flag:
            num += 1
            unidades.append(
                Unidad(codigo=element.id_uo, nombre=element.nombre_uo, departamentos=[], cant_registros=0, numero=num))

    for element in result:
        flag = False
        for cod in departamentos:
            if cod.codigo == element.codigo:
                flag = True
                break
        if not flag:
            departamentos.append(
                Dpto(codigo=element.codigo, nombre=element.nombre_dep, trabajadores=[], cant_registros=0))

    for element in result:
        trabajadores.append(element)

    for dep in departamentos:
        for trabajador in trabajadores:
            if trabajador.codigo == dep.codigo:
                dep.trabajadores.append(
                    Registro(data=trabajador, salario_total=None))
                dep.cant_registros += 1

    for unidad in unidades:
        for dep in departamentos:
            if dep.trabajadores[0].data.id_uo == unidad.codigo:
                unidad.departamentos.append(dep)
                unidad.cant_registros += dep.cant_registros

    cant_registros_bd = 0
    for u in unidades:
        cant_registros_bd += u.cant_registros

    total = unidades.__len__()

    return {'unidades': unidades, 'cant_registros_bd': cant_registros_bd, 'total': total, 'fecha_inic': fecha_inic,
            'fecha_fin': fecha_fin}


def reporte(request):
    fecha_i = request.POST['fecha_inic']
    fecha_fin = request.POST['fecha_fin']
    if fecha_i == '' or fecha_fin == '':
        error_vacaciones = True
        context = {'error_vacaciones': error_vacaciones}
        return render(request, 'home.html', context)
    else:
        return render(request, 'Reporte_Vacaciones.html', request_report(fecha_i, fecha_fin))


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


def exportar(request):
    fecha_inic = request.POST['fecha_inic']
    fecha_fin = request.POST['fecha_fin']
    template_path = 'Reporte_Vacaciones_template.html'
    context = request_report(fecha_inic, fecha_fin)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte_Vacaciones.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisastatus = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisastatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisastatus.err,
                                                                               html))
    return response


def exportar_modelo_vacaciones(request, pk):
    vacaciones = Vacaciones.objects.get(pk=pk)
    dia_s = vacaciones.fecha.__str__()[8:]
    mes_s = vacaciones.fecha.__str__()[5:7]
    anno_s = vacaciones.fecha.__str__()[0:4]
    dia_i = vacaciones.incorporacion.__str__()[8:]
    mes_i = vacaciones.incorporacion.__str__()[5:7]
    anno_i = vacaciones.incorporacion.__str__()[0:4]
    elaborado_por = request.user
    template_path = 'Modelo_Vacaciones.html'
    context = {'vacaciones': vacaciones, 'elaborado': elaborado_por, 'dia_s': dia_s, 'dia_i': dia_i, 'mes_s': mes_s,
               'mes_i': mes_i, 'anno_s': anno_s, 'anno_i': anno_i}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Modelo_Vacaciones.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisastatus = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisastatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisastatus.err, html))
    return response
