import os
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.template.loader import get_template
from xhtml2pdf import pisa
from ausentismo.form import AusenciaForm, TarjetaCNCForm
from ausentismo.models import Ausencia, TarjetaCNC
from ges_trab.models import Trabajador
from rechum import settings
from subsidio.models import Department, Person


def gestionar_ausentismo(request):
    list_trab = Trabajador.objects.all()
    form = AusenciaForm(request.POST or None)
    context = {'list_trab': list_trab, 'form': form}
    return render(request, 'Gestionar_Ausentismo.html', context)


def listar_ausentismo(request, pk):
    trabajador = Trabajador.objects.get(id=pk)
    list_ausencias = Ausencia.objects.filter(codigo_trab=pk)
    form = AusenciaForm(request.POST or None)
    context = {'list_ausencias': list_ausencias, 'form': form, 'trab': trabajador}
    return render(request, 'Listar_Ausentismo.html', context)


def adicionar_ausentismo(request):
    form = AusenciaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/listar_ausentismo/' + form.cleaned_data['codigo_trab'].pk.__str__() + '/')
    if request.environ['HTTP_REFERER'] == 'http://' + request.environ['HTTP_HOST'] + '/ausentismo/' or request.environ[
        'HTTP_REFERER'] == 'http://' + request.environ['HTTP_HOST'] + '/adicionar_ausentismo/':
        cal = Trabajador.objects.all()
        context = {'list_trab': cal, 'form': form}
        return render(request, 'Gestionar_Ausentismo.html', context)
    else:
        return listar_ausentismo(request, form.cleaned_data['codigo_trab'].pk)


def editar_ausentismo(request, idtrab, pk):
    ausencia = Ausencia.objects.get(id=pk)
    form = AusenciaForm(request.POST or None, instance=ausencia)
    if form.is_valid():
        form.save()
        return redirect('/listar_ausentismo/' + idtrab.__str__() + '/')
    trab = Trabajador.objects.get(id=int(idtrab))
    cal = Ausencia.objects.filter(codigo_trab=int(idtrab))
    context = {'list_ausencias': cal, 'form': form, 'edit': pk, 'trab': trab}
    return render(request, 'Listar_Ausentismo.html', context)


def eliminar_ausentismo(request, idtrab, pk):
    if request.method == 'POST':
        try:
            ausencia = Ausencia.objects.get(id=pk)
        except ObjectDoesNotExist:
            return redirect('/listar_ausentismo/' + idtrab.__str__() + '/')
        if ausencia:
            ausencia.delete()
            return redirect('/listar_ausentismo/' + idtrab.__str__() + '/')
    else:
        try:
            ausencia = Ausencia.objects.get(id=pk)
            context = {'object': ausencia, 'idtrab': idtrab}
        except ObjectDoesNotExist:
            context = {'error': 'El objeto que intenta eliminar no existe.', 'idtrab': idtrab}
            return render(request, 'Eliminar_Ausentismo.html', context)

        return render(request, 'Eliminar_Ausentismo.html', context)

        # Este metodo devuelve más datos de los necesarios
        # pero se dejo asi por si hay que agregarle datos al reporte despues.


def request_report(fecha_inic, fecha_fin):
    sql = "SELECT adm_unidadorg.nombre as uo, adm_departamento.codigo as dpt_cod, " \
          "adm_departamento.nombre as nombre_dpto, " \
          "ges_trab_trabajador.primer_nombre, ges_trab_trabajador.segundo_nombre, " \
          "ges_trab_trabajador.apellidos, ges_trab_trabajador.codigo_interno as cod_trab, " \
          "ausentismo_ausencia.fecha, ausentismo_ausencia.horas, ausentismo_ausencia.causal, ausentismo_ausencia.id " \
          "FROM " \
          "public.adm_unidadorg, public.adm_departamento, public.ges_trab_trabajador, public.ausentismo_ausencia " \
          "WHERE " \
          "adm_unidadorg.id = adm_departamento.unidad_id " \
          "AND adm_departamento.id = ges_trab_trabajador.departamento_id " \
          "AND ges_trab_trabajador.id = ausentismo_ausencia.codigo_trab_id " \
          "AND ausentismo_ausencia.fecha " \
          "BETWEEN " + "'" + fecha_inic + "'" + "::DATE AND " + "'" + fecha_fin + "'" + "::DATE " \
                                                                                        "GROUP BY adm_unidadorg.nombre, " \
                                                                                        "ges_trab_trabajador.primer_nombre, " \
                                                                                        "ges_trab_trabajador.segundo_nombre," \
                                                                                        "ges_trab_trabajador.apellidos, " \
                                                                                        "adm_departamento.codigo, " \
                                                                                        "adm_departamento.nombre," \
                                                                                        "ges_trab_trabajador.codigo_interno, " \
                                                                                        "ausentismo_ausencia.fecha, ausentismo_ausencia.horas, " \
                                                                                        "ausentismo_ausencia.causal, ausentismo_ausencia.id " \
                                                                                        "ORDER BY adm_departamento.codigo ASC, ges_trab_trabajador.codigo_interno ASC;"
    result = Ausencia.objects.raw(sql)
    codes_personas = []
    departments = []
    ausencias = []
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
        ausencias.append(element)

    for code in codes_personas:
        for ausencia in ausencias:
            if ausencia.cod_trab == code.codigo:
                code.subsidios.append(ausencia)
                code.cant_registros += 1
                code.suma_cod += ausencia.horas

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


def reporte(request):
    fecha_in = request.POST['fecha_inic']
    fecha_fin = request.POST['fecha_fin']
    if fecha_in == '' or fecha_fin == '':
        error_vacaciones = True
        context = {'error_add': error_vacaciones}
        return render(request, 'home.html', context)
    else:
        return render(request, 'Reporte_Ausentismo.html', request_report(fecha_in, fecha_fin))


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
    template_path = 'Reporte_Ausentismo_Template.html'
    context = request_report(fecha_inic, fecha_fin)
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'
    ] = 'attachment; filename="Reporte_Ausentismo de ' + fecha_inic + ' a ' + fecha_fin + '".pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisastatus = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisastatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisastatus.err,
                                                                               html))
    return response

    # ************************** Tarjeta CNC ************************** #


def gestionar_tarjeta_snc(request):
    list_trab = Trabajador.objects.all()
    form = TarjetaCNCForm(request.POST or None)
    context = {'list_trab': list_trab, 'form': form}
    return render(request, 'Gestionar_TarjetaSNC.html', context)


def listar_tarjeta_snc(request, pk):
    trabajador = Trabajador.objects.get(id=pk)
    list_entradas = TarjetaCNC.objects.filter(codigo_trab=pk)
    form = TarjetaCNCForm(request.POST or None)
    context = {'list_entradas': list_entradas, 'form': form, 'trab': trabajador}
    return render(request, 'Listar_TarjetaSNC.html', context)


def adicionar_tarjeta_snc(request):
    lista_entradas = []
    form = TarjetaCNCForm(request.POST or None)
    if form.is_valid():
        tarjeta = TarjetaCNC(codigo_trab=form.cleaned_data['codigo_trab'], mes=form.cleaned_data['mes'],
                             anno=form.cleaned_data['anno'], cant_dias=form.cleaned_data['cant_dias'],
                             salario=form.cleaned_data['salario'])
        if TarjetaCNC.objects.filter(mes=form.cleaned_data['mes'], anno=form.cleaned_data['anno'],
                                     codigo_trab=form.cleaned_data['codigo_trab']).count():
            cal = TarjetaCNC.objects.filter(codigo_trab=tarjeta.codigo_trab)
            for i in cal:
                lista_entradas.append(i)
            context = {'list_entradas': cal, 'form': form, 'trab': tarjeta.codigo_trab,
                       'error_add': 'Ya existe un registro asociado al trabajador con la misma fecha.'}
            return render(request, 'Listar_TarjetaSNC.html', context)
        else:
            form.save()
            return redirect('/listar_registro_tarjetaSNC/' + tarjeta.codigo_trab.pk.__str__() + '/')
    if request.environ['HTTP_REFERER'] == 'http://' + request.environ['HTTP_HOST'] + '/registro_tarjeta_SNC/' or \
        request.environ['HTTP_REFERER'] == 'http://' + request.environ[
                'HTTP_HOST'] + '/adicionar_registro_tarjetaSNC/':
        cal = Trabajador.objects.all()
        context = {'list_trab': cal, 'form': form}
        return render(request, 'Gestionar_TarjetaSNC.html', context)
    else:
        return listar_tarjeta_snc(request, form.cleaned_data['codigo_trab'].pk)


def editar_tarjeta_snc(request, idtrab, pk):
    lista_entradas = []
    tarjeta = TarjetaCNC.objects.get(id=pk)
    form = TarjetaCNCForm(request.POST or None, instance=tarjeta)
    if form.is_valid():
        lista = TarjetaCNC.objects.filter(mes=form.cleaned_data['mes'], anno=form.cleaned_data['anno'],
                                          codigo_trab=form.cleaned_data['codigo_trab'])
        bandera = False
        for i in lista:
            if pk != i.id:
                bandera = True
                break
        if bandera:
            cal = TarjetaCNC.objects.filter(codigo_trab=tarjeta.codigo_trab)
            for i in cal:
                lista_entradas.append(i)
            context = {'list_entradas': cal, 'form': form, 'trab': tarjeta.codigo_trab,
                       'error_add': 'Ya existe un registro asociado al trabajador con la misma fecha.'}
            return render(request, 'Listar_TarjetaSNC.html', context)
        else:
            form.save()
            return redirect('/listar_registro_tarjetaSNC/' + idtrab.__str__() + '/')
    trab = Trabajador.objects.get(id=int(idtrab))
    cal = TarjetaCNC.objects.filter(codigo_trab=int(idtrab))
    context = {'list_entradas': cal, 'form': form, 'edit': pk, 'trab': trab}
    return render(request, 'Listar_TarjetaSNC.html', context)


def eliminar_tarjeta_snc(request, idtrab, pk):
    if request.method == 'POST':
        try:
            tarjeta = TarjetaCNC.objects.get(id=pk)
        except ObjectDoesNotExist:
            return redirect('/listar_registro_tarjetaSNC/' + idtrab.__str__() + '/')
        if tarjeta:
            tarjeta.delete()
            return redirect('/listar_registro_tarjetaSNC/' + idtrab.__str__() + '/')
    else:
        try:
            tarjeta = TarjetaCNC.objects.get(id=pk)
            context = {'object': tarjeta, 'idtrab': idtrab}
        except ObjectDoesNotExist:
            context = {'error': 'El objeto que intenta eliminar no existe.', 'idtrab': idtrab}
            return render(request, 'Eliminar_TarjetaSNC.html', context)

        return render(request, 'Eliminar_TarjetaSNC.html', context)
