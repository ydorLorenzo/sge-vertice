import os
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .form import *
from decimal import Decimal
from entrada_datos.models import Actividad, OT
import json
from .models import OrdenTrabajo, Area, Actividades, Trabajador
from rechum import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
import calendar
import datetime


# Create your views here.


def home_pr3(request):
    coeficiente = CoeficientePromedioSalario.objects.get(id=1)
    formcoe = CoeficientePromedioSalarioForm(request.POST or None, instance=coeficiente)
    form = DatosForm(None)
    context = {'request': request, 'formcoe': formcoe, 'form': form}
    return render(request, 'home_pr3.html', context)


def registrar_datos(request):
    coeficiente = CoeficientePromedioSalario.objects.get(id=1).coeficiente
    formcoe = CoeficientePromedioSalarioForm(None)
    form = DatosForm(request.POST or None)
    if form.is_valid():
        trab = form.cleaned_data['trabajador']
        horas = form.cleaned_data['cant_horas']
        tarifa = Decimal(trab.salario_escala / Decimal(190.6))
        act = form.cleaned_data['actividad']
        prod = horas * coeficiente
        datos = Datos(
            orden_trab=form.cleaned_data['orden_trab'],
            actividad=act,
            trabajador=trab,
            cant_horas=horas,
            horas_ext=form.cleaned_data['horas_ext'],
            tarifa_hor=tarifa,
            prod_reportada=prod
        )
        datos.save()
        act.valor_prod_act += prod
        act.save()
        return redirect('/home_pr3/')
    context = {'form': form, 'formcoe': formcoe}
    return render(request, 'home_pr3.html', context)


def editar_coeficiente(request):
    coeficiente = CoeficientePromedioSalario.objects.get(id=1)
    formcoe = CoeficientePromedioSalarioForm(request.POST or None, instance=coeficiente)
    if formcoe.is_valid():
        formcoe.save()
        return redirect('/home_pr3/')
    form = DatosForm(None)
    context = {'formcoe': formcoe, 'form': form}
    return render(request, 'home_pr3.html', context)


def listar_valor_prod(request):
    list_act = Actividad.objects.all()
    coeficiente = CoeficientePromedioSalario.objects.get(id=1)
    formcoe = CoeficientePromedioSalarioForm(request.POST or None, instance=coeficiente)
    form = DatosForm(None)
    formajuste = AjusteForm(request.POST or None)
    context = {'list_act': list_act, 'formajuste': formajuste, 'formcoe': formcoe, 'form': form}
    return render(request, 'Listar_Valor_Produccion.html', context)


def ajustar_valor_prod(request):
    coeficiente = CoeficientePromedioSalario.objects.get(id=1)
    formcoe = CoeficientePromedioSalarioForm(request.POST or None, instance=coeficiente)
    form = DatosForm(None)
    act = Actividad.objects.get(id=request.POST['codigo_act'])
    formajuste = AjusteForm(request.POST or None, instance=act)
    if formajuste.is_valid():
        formajuste.save()
        return redirect('/listar_valor_prod/')
    cal = Actividad.objects.all()
    context = {'list_act': cal, 'form': form, 'formcoe': formcoe, 'formajuste': formajuste}
    return render(request, 'Listar_Valor_Produccion.html', context)


def act_por_ot(request, pk):
    actividades = Actividad.objects.filter(orden_trab=pk)
    datos = [{'nombre': actividad.descripcion_act, 'id': actividad.id, 'codigo_act': actividad.codigo_act} for actividad
             in actividades]
    response = [{"success": 1, "result": datos}]
    return HttpResponse(json.dumps(response), content_type='application/json')


def listado_datos(request):
    coeficiente = CoeficientePromedioSalario.objects.get(id=1)
    formcoe = CoeficientePromedioSalarioForm(request.POST or None, instance=coeficiente)
    form = DatosForm(None)
    list_datos = Datos.objects.all()
    context = {'list_datos': list_datos, 'formcoe': formcoe, 'form': form}
    return render(request, 'Listado_Datos.html', context)


def request_report_ot_act():
    sql = 'SELECT entrada_datos_ot.codigo_ot, entrada_datos_ot.descripcion_ot, entrada_datos_actividad.codigo_act, ' \
          'entrada_datos_actividad.descripcion_act, entrada_datos_actividad.orden_trab_id,' \
          'entrada_datos_ot.id ' \
          'FROM public.entrada_datos_ot, public.entrada_datos_actividad ' \
          'WHERE entrada_datos_ot.id = entrada_datos_actividad.orden_trab_id ' \
          'GROUP BY codigo_ot, codigo_act, descripcion_ot, descripcion_act, entrada_datos_ot.id, ' \
          'entrada_datos_actividad.id;'

    result = Actividad.objects.raw(sql)
    actividades = []
    ordenes = []

    for element in result:
        flag = False
        for orden in ordenes:
            if orden.codigo == element.codigo_ot:
                flag = True
                break
        if not flag:
            ordenes.append(
                OrdenTrabajo(codigo=element.codigo_ot, nombre=element.descripcion_ot, actividades=[], total=0, area=0))

    for element in result:
        actividades.append(element)

    for orden in ordenes:
        for act in actividades:
            if act.codigo_ot == orden.codigo:
                orden.actividades.append(act)
    return ordenes


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


def reporte_ot_actividades(request):
    coeficiente = CoeficientePromedioSalario.objects.get(id=1)
    formcoe = CoeficientePromedioSalarioForm(request.POST or None, instance=coeficiente)
    form = DatosForm(None)
    context = {'list_ot': request_report_ot_act(), 'formcoe': formcoe, 'form': form}
    return render(request, 'Reporte_OT_Actividades.html', context)


def exportar_ot_actividades(request):
    template_path = 'Reporte_OT_Actividades_template.html'
    context = {'list_ot': request_report_ot_act()}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte_OT_Actividades.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisastatus = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisastatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisastatus.err,
                                                                               html))
    return response


def request_report_area_ot():
    sql = 'SELECT entrada_datos_ot.area_id, entrada_datos_ot.descripcion_ot, entrada_datos_ot.codigo_ot, ' \
          'entrada_datos_area.id, entrada_datos_area.nombre, entrada_datos_area.codigo ' \
          'FROM public.entrada_datos_ot, public.entrada_datos_area  ' \
          'WHERE entrada_datos_area.id = entrada_datos_ot.area_id ' \
          'GROUP BY codigo, nombre, codigo_ot, descripcion_ot, entrada_datos_area.id, area_id; '

    result = OT.objects.raw(sql)
    ordenes = []
    areas = []

    for element in result:
        flag = False
        for are in areas:
            if are.id == element.area_id:
                flag = True
                break
        if not flag:
            areas.append(
                Area(id_a=element.id, nombre=element.nombre, ot=[], total=0))

    for element in result:
        ordenes.append(element)

    for are in areas:
        for ot in ordenes:
            if ot.area_id == are.id:
                are.ot.append(ot)
    return areas


def reporte_area_ot(request):
    coeficiente = CoeficientePromedioSalario.objects.get(id=1)
    formcoe = CoeficientePromedioSalarioForm(request.POST or None, instance=coeficiente)
    form = DatosForm(None)
    context = {'list_area': request_report_area_ot(), 'formcoe': formcoe, 'form': form}
    return render(request, 'Reporte_Area_OT.html', context)


def exportar_area_ot(request):
    template_path = 'Reporte_Area_OT_template.html'
    context = {'list_area': request_report_area_ot()}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte_Area_OT.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisastatus = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisastatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisastatus.err,
                                                                               html))
    return response


def reporte_actividades_contrato(request):
    contratos = OT.objects.all()
    coeficiente = CoeficientePromedioSalario.objects.get(id=1)
    formcoe = CoeficientePromedioSalarioForm(request.POST or None, instance=coeficiente)
    form = DatosForm(None)
    cont = contratos[0].no_contrato
    actividades = Actividad.objects.filter(orden_trab_id=contratos[0].id)
    if request.POST:
        cont = request.POST['contrato']
        if cont:
            ot = OT.objects.get(no_contrato=cont)
            actividades = Actividad.objects.filter(orden_trab_id=ot.id)
            context = {'list_act': actividades, 'formcoe': formcoe, 'form': form, 'list_cont': contratos, 'ot': ot,
                       'cont': cont}
            return render(request, 'Reporte_Actividades_Contrato.html', context)
        else:
            context = {'list_act': actividades, 'formcoe': formcoe, 'form': form, 'list_cont': contratos, 'cont': cont,
                       'ot': contratos[0]}
            return render(request, 'Reporte_Actividades_Contrato.html', context)
    else:
        context = {'list_act': actividades, 'formcoe': formcoe, 'form': form, 'list_cont': contratos, 'cont': cont,
                   'ot': contratos[0]}
        return render(request, 'Reporte_Actividades_Contrato.html', context)


def exportar_actividades_contrato(request, cont):
    ot = OT.objects.get(no_contrato=cont)
    actividades = Actividad.objects.filter(orden_trab_id=ot.id)
    context = {'list_act': actividades, 'ot': ot}
    template_path = 'Reporte_Actividades_Contrato_template.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte_Actividades_Contrato.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisastatus = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisastatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisastatus.err,
                                                                               html))
    return response


def request_report_pr3():
    sql = 'select entrada_datos_actividad.codigo_act, entrada_datos_actividad.descripcion_act, ' \
          'entrada_datos_actividad.prod_tecleada, entrada_datos_actividad.valor_prod_act,' \
          ' entrada_datos_actividad.activa, entrada_datos_ot.codigo_ot, entrada_datos_ot.descripcion_ot, ' \
          'pr3_datos.orden_trab_id as pr3_d_id, pr3_datos.actividad_id, ges_trab_trabajador.codigo_interno,' \
          ' ges_trab_trabajador.primer_nombre, ' \
          'ges_trab_trabajador.segundo_nombre, ges_trab_trabajador.apellidos, entrada_datos_area.id as ed_a_id,' \
          ' entrada_datos_area.codigo, entrada_datos_area.nombre, pr3_datos.cant_horas, pr3_datos.horas_ext,' \
          'entrada_datos_ot.id as ed_ot_id, entrada_datos_actividad.orden_trab_id, pr3_datos.id'\
          ' from entrada_datos_actividad, entrada_datos_ot, pr3_datos, ges_trab_trabajador, entrada_datos_area ' \
          'where pr3_datos.orden_trab_id = entrada_datos_ot.id and pr3_datos.actividad_id = entrada_datos_actividad.id' \
          ' and ges_trab_trabajador.id = pr3_datos.trabajador_id and entrada_datos_area.id = entrada_datos_ot.area_id' \
          ' order by entrada_datos_area.codigo, entrada_datos_ot.codigo_ot, entrada_datos_actividad.codigo_act;'

    result = Datos.objects.raw(sql)
    areas = []
    ordenes = []
    actividades = []
    trabajadores = []

    for element in result:
        flag = False
        for area in areas:
            if area.id == element.ed_a_id:
                flag = True
                break
        if not flag:
            areas.append(
                Area(id_a=element.ed_a_id, nombre=element.nombre, ot=[], total=0))

    for element in result:
        flag = False
        for orden in ordenes:
            if orden.codigo == element.codigo_ot:
                flag = True
                break
        if not flag:
            ordenes.append(
                OrdenTrabajo(codigo=element.codigo_ot, nombre=element.descripcion_ot, actividades=[], total=0,
                             area=element.ed_a_id))

    for element in result:
        flag = False
        for act in actividades:
            if act.id == element.actividad_id:
                flag = True
                break
        if not flag:
            if element.prod_tecleada > 0.00:
                val = element.prod_tecleada
            else:
                val = element.valor_prod_act
            actividades.append(Actividades(orden_trab=element.codigo_ot, codigo=element.codigo_act,
                                           nombre=element.descripcion_act, trabajadores=[], valor=val,
                                           id=element.actividad_id))

    for element in result:
        trabajadores.append(Trabajador(codigo=element.codigo_interno, nombre=element.primer_nombre + ' ' +
                                       element.segundo_nombre + ' ' + element.apellidos, real=element.cant_horas,
                                       extra=element.horas_ext, id=element.id, id_act=element.actividad_id))

    for act in actividades:
        for trab in trabajadores:
            if act.id == trab.id_act:
                act.trabajadores.append(trab)

    for orden in ordenes:
        for act in actividades:
            if act.orden_trab == orden.codigo:
                orden.actividades.append(act)
                orden.total += act.valor

    for area in areas:
        for ot in ordenes:
            if ot.area == area.id:
                area.ot.append(ot)
                area.total += ot.total

    return areas


def reporte_pr3(request):
    coeficiente = CoeficientePromedioSalario.objects.get(id=1)
    formcoe = CoeficientePromedioSalarioForm(request.POST or None, instance=coeficiente)
    form = DatosForm(None)
    m = datetime.datetime.now().month
    anno = datetime.datetime.now().year
    monthrange = calendar.monthrange(anno, m)
    if m < 10:
        mes = '0' + str(m)
    else:
        mes = str(m)
    if monthrange[1] < 10:
        dia = '0' + monthrange[1]
    else:
        dia = str(monthrange[1])

    fecha_ini = '01' + '/' + mes + '/' + str(anno)
    fecha_fin = dia + '/' + mes + '/' + str(anno)
    context = {'fecha_ini': fecha_ini, 'fecha_fin': fecha_fin, 'formcoe': formcoe, 'form': form, 'list_area':
               request_report_pr3()}
    return render(request, 'Reporte_PR3.html', context)


def exportar_reporte_pr3(request):
    m = datetime.datetime.now().month
    anno = datetime.datetime.now().year
    monthrange = calendar.monthrange(anno, m)
    if m < 10:
        mes = '0' + str(m)
    else:
        mes = str(m)
    if monthrange[1] < 10:
        dia = '0' + monthrange[1]
    else:
        dia = str(monthrange[1])
    usuario = request.user
    fecha_ini = '01' + '/' + mes + '/' + str(anno)
    fecha_fin = dia + '/' + mes + '/' + str(anno)
    template_path = 'Reporte_PR3_template.html'
    context = {'list_area': request_report_pr3(), 'fecha_ini': fecha_ini, 'fecha_fin': fecha_fin, 'usuario': usuario}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte_PR3.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisastatus = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisastatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisastatus.err,
                                                                               html))
    return response


def reporte_prod_direccion(request):
    coeficiente = CoeficientePromedioSalario.objects.get(id=1)
    formcoe = CoeficientePromedioSalarioForm(request.POST or None, instance=coeficiente)
    form = DatosForm(None)
    m = datetime.datetime.now().month
    anno = datetime.datetime.now().year
    monthrange = calendar.monthrange(anno, m)
    if m < 10:
        mes = '0' + str(m)
    else:
        mes = str(m)
    if monthrange[1] < 10:
        dia = '0' + monthrange[1]
    else:
        dia = str(monthrange[1])
    areas = request_report_pr3()
    suma = 0
    for area in areas:
        suma += area.total
    fecha_ini = '01' + '/' + mes + '/' + str(anno)
    fecha_fin = dia + '/' + mes + '/' + str(anno)
    context = {'fecha_ini': fecha_ini, 'fecha_fin': fecha_fin, 'formcoe': formcoe, 'form': form, 'list_area':
               request_report_pr3(), 'suma': suma}
    return render(request, 'Reporte_Produccion_Direcciones.html', context)
