import json
import os
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from xhtml2pdf import pisa
from rechum import settings
from .form import *
from .models import Plantilla, Departamento, Dpto, Unidad
from ges_trab.models import Trabajador, Departamento, UnidadOrg, Cargo, EscalaSalarial


@permission_required('plantilla',login_url='home_principal')
def gestionar_plantilla(request):
    list_plantilla = Plantilla.objects.all()
    form = PlantillaForm(request.POST or None)
    context = {'list_plantilla': list_plantilla, 'form': form}
    return render(request, 'Gestionar_Plantilla.html', context)

@permission_required('plantilla',login_url='home_principal')
def adicionar_plantilla(request):
    form = PlantillaForm(request.POST or None)
    if form.is_valid():
        plantilla = Plantilla(
            unidad=form.cleaned_data['unidad'],
            departamento=form.cleaned_data['departamento'],
            cargo=form.cleaned_data['cargo'],
            cant_plazas=form.cleaned_data['cant_plazas'],
            disponibles=form.cleaned_data['cant_plazas']
        )
        if Plantilla.objects.filter(departamento=plantilla.departamento, cargo=plantilla.cargo).count():
            cal = Plantilla.objects.all()
            context = {'list_plantilla': cal, 'form': form, 'object': plantilla,
                       'error_add': 'El departamento seleccionado ya tiene asignado ese cargo.'}
            return render(request, 'Gestionar_Plantilla.html', context)
        else:
            plantilla.save()
            return redirect('/plantilla/')
    if request.method == 'POST':
        list_plantilla = Plantilla.objects.all()
        context = {'list_plantilla': list_plantilla, 'form': form}
        return render(request, 'Gestionar_Plantilla.html', context)

@permission_required('plantilla',login_url='home_principal')
def editar_plantilla(request, pk):
    plantilla = Plantilla.objects.get(id=pk)
    form = PlantillaForm(request.POST or None, instance=plantilla)
    if form.is_valid():
        plantilla.cant_plazas = form.cleaned_data['cant_plazas']
        plantilla.save()
        return redirect('/plantilla/')
    cal = Plantilla.objects.all()
    context = {'list_plantilla': cal, 'edit': pk, 'object': plantilla, 'form': form}
    return render(request, 'Gestionar_Plantilla.html', context)

@permission_required('plantilla',login_url='home_principal')
def editar_plantilla_plazas(request, pk):
    plantilla = Plantilla.objects.get(id=pk)
    plazas = request.POST['cant_plazas']

    if (int(plazas) < int(plantilla.cant_plazas)) and abs(int(plazas) - int(plantilla.cant_plazas)) > int(
            plantilla.disponibles):
        form = PlantillaForm(None)
        cal = Plantilla.objects.all()
        context = {'list_plantilla': cal, 'edit': pk, 'object': plantilla, 'form': form,
                   'error': 'Plazas disponibles para eliminar insuficientes.'}
        return render(request, 'Gestionar_Plantilla.html', context)

    cant_plazas_ant = plantilla.cant_plazas
    plantilla.cant_plazas = plazas
    plantilla.disponibles += int(plazas) - int(cant_plazas_ant)
    plantilla.save()
    return redirect('/plantilla/')


# este es el metodo que muestra el alerta de eliminacion y despues elimina
#@login_required
@permission_required('plantilla',login_url='home_principal')
def eliminar_plantilla(request, pk):
    plantilla = Plantilla.objects.get(id=pk)
    if request.method == 'GET':
        context = {'object': plantilla}
        return render(request, 'Eliminar_Plantilla.html', context)
    else:
        if int(plantilla.cant_plazas) == int(plantilla.disponibles):
            plantilla.delete()
            return redirect('/plantilla/')
        else:
            list_plantilla = Plantilla.objects.all()
            form = PlantillaForm(None)
            context = {'list_plantilla': list_plantilla, 'form': form,
                       'errores': 'Imposible eliminar plantilla con plazas ocupadas.'}
            return render(request, 'Gestionar_Plantilla.html', context)

@permission_required('plantilla',login_url='home_principal')
def dpto_por_unidad(request, pk):
    departamentos = Departamento.objects.filter(unidad=pk)
    datos = [{'nombre': departamento.nombre, 'id': departamento.id, 'codigo': departamento.codigo} for departamento in
             departamentos]
    response = [{"success": 1, "result": datos}]
    return HttpResponse(json.dumps(response), content_type='application/json')


def request_report():
    sql = 'SELECT adm_unidadorg.nombre AS "nombreUO", adm_unidadorg.id AS "idUO", ' \
          'adm_departamento.nombre AS "nombreDep", ges_trab_trabajador.primer_nombre AS nombre, ' \
          'ges_trab_trabajador.segundo_nombre AS "segundo_nombre", ges_trab_trabajador.apellidos AS apellidos, ' \
          'ges_trab_trabajador.categoria AS categoria,ges_trab_trabajador.t_plantilla, ' \
          'ges_trab_trabajador.org_plantilla, adm_cargo.nombre AS "nombreCargo", ' \
          'adm_departamento.id AS dptoid, ges_trab_trabajador.sexo, ges_trab_trabajador.ci, ' \
          'adm_escalasalarial.grupo AS "grupoEscala", ges_trab_trabajador.escolaridad, ' \
          'ges_trab_trabajador.salario_escala, ges_trab_trabajador.incre_res, ges_trab_trabajador.cies, ' \
          'ges_trab_trabajador.sal_plus, ges_trab_trabajador.antiguedad, ges_trab_trabajador.cat_cient, ' \
          'ges_trab_trabajador.fecha_contrato, ges_trab_trabajador.id AS id, adm_departamento.codigo AS dptoCod, ' \
          'ges_trab_trabajador.sal_cat_cient, ges_trab_trabajador.salario_total, ' \
          'ges_trab_trabajador.salario_jornada_laboral ' \
          'FROM public.adm_unidadorg, public.adm_departamento, public.ges_trab_trabajador, public.adm_cargo, ' \
          'public.adm_escalasalarial ' \
          'WHERE adm_unidadorg.id = adm_departamento.unidad_id ' \
          'AND adm_departamento.id = ges_trab_trabajador.departamento_id ' \
          'AND adm_cargo.id = ges_trab_trabajador.cargo_id ' \
          'AND adm_escalasalarial.id = ges_trab_trabajador.escala_salarial_id' \
          ' AND (ges_trab_trabajador.t_contrato=\'1\' OR ges_trab_trabajador.t_contrato=\'2\') ' \
          'GROUP BY adm_unidadorg.id, adm_departamento.nombre, ges_trab_trabajador.primer_nombre, ' \
          'ges_trab_trabajador.segundo_nombre, ges_trab_trabajador.apellidos, ges_trab_trabajador.categoria, ' \
          'adm_cargo.nombre, adm_departamento.id, ges_trab_trabajador.sexo, ges_trab_trabajador.ci, ' \
          'adm_escalasalarial.grupo, ges_trab_trabajador.escolaridad, adm_escalasalarial.salario_escala, ' \
          'ges_trab_trabajador.incre_res, ges_trab_trabajador.cies, ges_trab_trabajador.sal_plus, ' \
          'ges_trab_trabajador.antiguedad, ges_trab_trabajador.cat_cient, ges_trab_trabajador.fecha_alta, ' \
          'ges_trab_trabajador.id ' \
          'ORDER BY adm_unidadorg.id ASC, adm_departamento.id ASC, ges_trab_trabajador.org_plantilla ASC ;'
    result = Plantilla.objects.raw(sql)
    departamentos = []
    unidades = []
    trabajadores = []

    num = 0
    for element in result:
        flag = False
        for depa in unidades:
            if depa.codigo == element.idUO:
                flag = True
                break
        if not flag:
            num += 1
            unidades.append(
                Unidad(codigo=element.idUO, nombre=element.nombreUO, departamentos=[], cant_registros=0, numero=num))

    for element in result:
        flag = False
        for cod in departamentos:
            if cod.codigo == element.dptocod:
                flag = True
                break
        if not flag:
            departamentos.append(
                Dpto(codigo=element.dptocod, nombre=element.nombreDep, trabajadores=[], cant_registros=0))

    for element in result:
        trabajadores.append(element)

    for dep in departamentos:
        for trabajador in trabajadores:
            if trabajador.dptocod == dep.codigo:
                dep.trabajadores.append(
                    Registro(data=trabajador))
                dep.cant_registros += 1

    for unidad in unidades:
        for dep in departamentos:
            if dep.trabajadores[0].data.idUO == unidad.codigo:
                unidad.departamentos.append(dep)
                unidad.cant_registros += dep.cant_registros

    cant_registros_bd = 0
    for u in unidades:
        cant_registros_bd += u.cant_registros

    total = unidades.__len__()

    return {'unidades': unidades, 'cant_registros_bd': cant_registros_bd, 'total': total}

@permission_required('plantilla',login_url='home_principal')
def reporte(request):
    return render(request, 'Reporte_Plantilla.html', request_report())


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
    template_path = 'Reporte_Plantilla_template.html'
    context = request_report()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte_Plantilla.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisastatus = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisastatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisastatus.err,
                                                                               html))
    return response


def request_report_graduados():
    sql = 'SELECT adm_unidadorg.nombre AS "nombreUO", adm_unidadorg.id AS "idUO", ' \
          'adm_departamento.nombre AS "nombreDep", ges_trab_trabajador.primer_nombre AS nombre, ' \
          'ges_trab_trabajador.segundo_nombre AS "segundo_nombre", ges_trab_trabajador.apellidos AS apellidos, ' \
          'ges_trab_trabajador.categoria AS categoria, ' \
          'ges_trab_trabajador.org_plantilla, adm_cargo.nombre AS "nombreCargo", ' \
          'adm_departamento.id AS dptoid, ges_trab_trabajador.sexo, ges_trab_trabajador.ci, ' \
          'adm_escalasalarial.grupo AS "grupoEscala", ges_trab_trabajador.escolaridad, ' \
          'ges_trab_trabajador.salario_escala, ges_trab_trabajador.incre_res, ges_trab_trabajador.cies, ' \
          'ges_trab_trabajador.antiguedad, ges_trab_trabajador.fecha_contrato, ' \
          ' ges_trab_trabajador.id AS id, adm_departamento.codigo AS dptoCod, ' \
          'ges_trab_trabajador.sal_cat_cient, ges_trab_trabajador.salario_total, ' \
          'ges_trab_trabajador.salario_jornada_laboral ' \
          'FROM public.adm_unidadorg, public.adm_departamento, public.ges_trab_trabajador, public.adm_cargo, ' \
          'public.adm_escalasalarial ' \
          'WHERE adm_unidadorg.id = adm_departamento.unidad_id ' \
          'AND adm_departamento.id = ges_trab_trabajador.departamento_id ' \
          'AND adm_cargo.id = ges_trab_trabajador.cargo_id ' \
          'AND adm_escalasalarial.id = ges_trab_trabajador.escala_salarial_id' \
          ' AND ges_trab_trabajador.t_contrato=\'4\' ' \
          'GROUP BY adm_unidadorg.id, adm_departamento.nombre, ges_trab_trabajador.primer_nombre, ' \
          'ges_trab_trabajador.segundo_nombre, ges_trab_trabajador.apellidos, ges_trab_trabajador.categoria, ' \
          'adm_cargo.nombre, adm_departamento.id, ges_trab_trabajador.sexo, ges_trab_trabajador.ci, ' \
          'adm_escalasalarial.grupo, ges_trab_trabajador.escolaridad, adm_escalasalarial.salario_escala, ' \
          'ges_trab_trabajador.incre_res, ges_trab_trabajador.cies, ges_trab_trabajador.sal_plus, ' \
          'ges_trab_trabajador.antiguedad, ges_trab_trabajador.cat_cient, ges_trab_trabajador.fecha_alta, ' \
          'ges_trab_trabajador.id ' \
          'ORDER BY adm_unidadorg.id ASC, adm_departamento.id ASC, ges_trab_trabajador.org_plantilla ASC ;'
    result = Plantilla.objects.raw(sql)
    departamentos = []
    unidades = []
    trabajadores = []

    num = 0
    for element in result:
        flag = False
        for depa in unidades:
            if depa.codigo == element.idUO:
                flag = True
                break
        if not flag:
            num += 1
            unidades.append(
                Unidad(codigo=element.idUO, nombre=element.nombreUO, departamentos=[], cant_registros=0, numero=num))

    for element in result:
        flag = False
        for cod in departamentos:
            if cod.codigo == element.dptocod:
                flag = True
                break
        if not flag:
            departamentos.append(
                Dpto(codigo=element.dptocod, nombre=element.nombreDep, trabajadores=[], cant_registros=0))

    for element in result:
        trabajadores.append(element)

    for dep in departamentos:
        for trabajador in trabajadores:
            if trabajador.dptocod == dep.codigo:
                dep.trabajadores.append(
                    Registro(data=trabajador))
                dep.cant_registros += 1

    for unidad in unidades:
        for dep in departamentos:
            if dep.trabajadores[0].data.idUO == unidad.codigo:
                unidad.departamentos.append(dep)
                unidad.cant_registros += dep.cant_registros

    cant_registros_bd = 0
    for u in unidades:
        cant_registros_bd += u.cant_registros

    total = unidades.__len__()

    return {'unidades': unidades, 'cant_registros_bd': cant_registros_bd, 'total': total}

@permission_required('plantilla',login_url='home_principal')
def reporte_graduados(request):
    return render(request, 'Reporte_Plantilla_Graduados.html', request_report_graduados())

@permission_required('plantilla',login_url='home_principal')
def exportar_graduados(request):
    template_path = 'Reporte_Plantilla_Graduados_template.html'
    context = request_report_graduados()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte_Plantilla_Recien_Graduados.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisastatus = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisastatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisastatus.err,
                                                                               html))
    return response


def request_report_contratos():
    sql = 'SELECT adm_unidadorg.nombre AS "nombreUO", adm_unidadorg.id AS "idUO", ' \
          'adm_departamento.nombre AS "nombreDep", ges_trab_trabajador.primer_nombre AS nombre, ' \
          'ges_trab_trabajador.segundo_nombre AS "segundo_nombre", ges_trab_trabajador.apellidos AS apellidos, ' \
          'ges_trab_trabajador.categoria AS categoria, ' \
          'ges_trab_trabajador.org_plantilla, adm_cargo.nombre AS "nombreCargo", ' \
          'adm_departamento.id AS dptoid, ges_trab_trabajador.sexo, ges_trab_trabajador.ci, ' \
          'adm_escalasalarial.grupo AS "grupoEscala", ges_trab_trabajador.escolaridad, ' \
          'ges_trab_trabajador.salario_escala, ges_trab_trabajador.incre_res, ges_trab_trabajador.cies, ' \
          'ges_trab_trabajador.sal_plus, ges_trab_trabajador.antiguedad, ges_trab_trabajador.cat_cient, ' \
          'ges_trab_trabajador.fecha_contrato, ges_trab_trabajador.id AS id, adm_departamento.codigo AS dptoCod, ' \
          'ges_trab_trabajador.sal_cat_cient, ges_trab_trabajador.salario_total, ' \
          'ges_trab_trabajador.salario_jornada_laboral ' \
          'FROM public.adm_unidadorg, public.adm_departamento, public.ges_trab_trabajador, public.adm_cargo, ' \
          'public.adm_escalasalarial ' \
          'WHERE adm_unidadorg.id = adm_departamento.unidad_id ' \
          'AND adm_departamento.id = ges_trab_trabajador.departamento_id ' \
          'AND adm_cargo.id = ges_trab_trabajador.cargo_id ' \
          'AND adm_escalasalarial.id = ges_trab_trabajador.escala_salarial_id' \
          ' AND (ges_trab_trabajador.t_contrato=\'3\' OR ges_trab_trabajador.t_contrato=\'6\') ' \
          'GROUP BY adm_unidadorg.id, adm_departamento.nombre, ges_trab_trabajador.primer_nombre, ' \
          'ges_trab_trabajador.segundo_nombre, ges_trab_trabajador.apellidos, ges_trab_trabajador.categoria, ' \
          'adm_cargo.nombre, adm_departamento.id, ges_trab_trabajador.sexo, ges_trab_trabajador.ci, ' \
          'adm_escalasalarial.grupo, ges_trab_trabajador.escolaridad, adm_escalasalarial.salario_escala, ' \
          'ges_trab_trabajador.incre_res, ges_trab_trabajador.cies, ges_trab_trabajador.sal_plus, ' \
          'ges_trab_trabajador.antiguedad, ges_trab_trabajador.cat_cient, ges_trab_trabajador.fecha_alta, ' \
          'ges_trab_trabajador.id ' \
          'ORDER BY adm_unidadorg.id ASC, adm_departamento.id ASC, ges_trab_trabajador.org_plantilla ASC ;'
    result = Plantilla.objects.raw(sql)
    departamentos = []
    unidades = []
    trabajadores = []

    num = 0
    for element in result:
        flag = False
        for depa in unidades:
            if depa.codigo == element.idUO:
                flag = True
                break
        if not flag:
            num += 1
            unidades.append(
                Unidad(codigo=element.idUO, nombre=element.nombreUO, departamentos=[], cant_registros=0, numero=num))

    for element in result:
        flag = False
        for cod in departamentos:
            if cod.codigo == element.dptocod:
                flag = True
                break
        if not flag:
            departamentos.append(
                Dpto(codigo=element.dptocod, nombre=element.nombreDep, trabajadores=[], cant_registros=0))

    for element in result:
        trabajadores.append(element)

    for dep in departamentos:
        for trabajador in trabajadores:
            if trabajador.dptocod == dep.codigo:
                dep.trabajadores.append(
                    Registro(data=trabajador))
                dep.cant_registros += 1

    for unidad in unidades:
        for dep in departamentos:
            if dep.trabajadores[0].data.idUO == unidad.codigo:
                unidad.departamentos.append(dep)
                unidad.cant_registros += dep.cant_registros

    cant_registros_bd = 0
    for u in unidades:
        cant_registros_bd += u.cant_registros

    total = unidades.__len__()

    return {'unidades': unidades, 'cant_registros_bd': cant_registros_bd, 'total': total}

@permission_required('plantilla',login_url='home_principal')
def reporte_contratos(request):
    return render(request, 'Reporte_Plantilla_Contratos.html', request_report_contratos())

@permission_required('plantilla',login_url='home_principal')
def exportar_contratos(request):
    template_path = 'Reporte_Plantilla_Contratos_template.html'
    context = request_report_contratos()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte_Plantilla_Contratos.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisastatus = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisastatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisastatus.err,
                                                                               html))
    return response
