import json
import os

from django.contrib.auth.decorators import permission_required, login_required
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.db.models import F, Q
from xhtml2pdf import pisa

from rechum import settings
from rechum.utils import generate_pisa_report
from rechum.views import SgeListView, SgeCreateView, SgeDetailView, SgeDeleteView, SgeUpdateView
from .form import *
from .models import Plantilla, Dpto, Unidad, Registro
from ges_trab.models import Trabajador, Alta
from adm.models import Departamento, UnidadOrg, Cargo, EscalaSalarial
from prenomina15.models import PlantillaServicio, Obra


class PlantillaListView(SgeListView):
    permission_required = 'plantilla.read_plantilla'
    raise_exception = True
    model = Plantilla
    template_name = 'plantilla/list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        object_list = self.model.objects.all()
        if self.kwargs.get('departamento_id'):
            dep_id = self.kwargs.get('departamento_id')
            dep = Departamento.objects.filter(pk=dep_id).annotate(
                unidad_nombre=F('unidad__nombre')).values('nombre', 'unidad_nombre', 'unidad_id')[0]
            self.extra_context = {'departamento': dep['nombre'], 'unidad': dep['unidad_nombre'],
                                  'unidad_id': dep['unidad_id']}
            object_list = object_list.filter(departamento_id=dep_id)
        return super().get_context_data(object_list=object_list, **kwargs)


class PlantillaCreateView(SgeCreateView):
    permission_required = 'plantilla.add_plantilla'
    model = Plantilla
    form_class = PlantillaForm
    template_name = 'plantilla/create.html'
    success_url = reverse_lazy('plantilla_create')


class PlantillaUpdateView(SgeUpdateView):
    permission_required = 'plantilla.change_plantilla'
    model = Plantilla
    form_class = PlantillaForm
    template_name = 'plantilla/create.html'
    success_url = reverse_lazy('plantilla_list')


class PlantillaDetailView(SgeDetailView):
    permission_required = 'plantilla.read_plantilla'
    model = Plantilla
    template_name = 'plantilla/detail.html'


class PlantillaDeleteView(SgeDeleteView):
    permission_required = 'plantilla.delete_plantilla'
    model = Plantilla
    success_url = reverse_lazy('plantilla_list')


########################################################################
# Plantilla Servicios
#

class ServicioListView(SgeListView):
    permission_required = 'prenomina15.read_obra'
    model = Obra
    template_name = 'obra-servicio/list.html'


class PlantillaServicioListView(SgeListView):
    permission_required = 'prenomina15.read_plantillaservicio'
    model = PlantillaServicio
    template_name = 'plantilla-servicio/list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        object_list = self.model.objects.all()
        if self.kwargs.get('servicio_id'):
            srv_id = self.kwargs.get('servicio_id')
            srv = Obra.objects.filter(pk=srv_id).values('nombre')[0]
            self.extra_context = {'servicio': srv['nombre'], 'servicio_id': srv_id}
            object_list = object_list.filter(servicio_id=srv_id)
            kwargs["create_url"] = reverse_lazy(self.model._meta.model_name + '_create', kwargs={"servicio_id": srv_id})
        return super().get_context_data(object_list=object_list, **kwargs)


class PlantillaServicioCreateView(SgeCreateView):
    permission_required = 'prenomina15.add_plantillaservicio'
    model = PlantillaServicio
    form_class = PlantillaServicioForm
    template_name = 'plantilla-servicio/create.html'

    def get_success_url(self):
        success_url = reverse_lazy('plantillaservicio_list', kwargs={'servicio_id': self.kwargs.get('servicio_id')})
        return success_url.format(**self.object.__dict__)

    def get_context_data(self, **kwargs):
        update_create_kwargs(self.kwargs.get('servicio_id'))
        kwargs.update(update_create_kwargs(self.kwargs.get('servicio_id')))
        return super().get_context_data(**kwargs)


class PlantillaServicioUpdateView(SgeUpdateView):
    permission_required = 'prenomina15.edit_plantillaservicio'
    model = PlantillaServicio
    form_class = PlantillaServicioForm
    template_name = 'plantilla-servicio/create.html'

    def get_success_url(self):
        success_url = reverse_lazy('plantillaservicio_list', kwargs={'servicio_id': self.kwargs.get('servicio_id')})
        return success_url.format(**self.object.__dict__)

    def get_context_data(self, **kwargs):
        update_create_kwargs(self.kwargs.get('servicio_id'))
        kwargs.update(update_create_kwargs(self.kwargs.get('servicio_id')))
        return super().get_context_data(**kwargs)


class PlantillaServicioDeleteView(SgeDeleteView):
    permission_required = 'prenomina15.read_plantillaservicio'
    model = PlantillaServicio

    def get_success_url(self):
        success_url = reverse_lazy('plantillaservicio_list', kwargs={'servicio_id': self.kwargs.get('servicio_id')})
        return success_url.format(**self.object.__dict__)


def update_create_kwargs(srv_id):
    return {
        'list_url': reverse_lazy('plantillaservicio_list', kwargs={'servicio_id': srv_id}),
        'create_url': reverse_lazy('plantillaservicio_create', kwargs={'servicio_id': srv_id}),
        'servicio_id': srv_id
    }


########################################################################
# Function views
#

@permission_required('plantilla.read_plantilla', login_url='home_principal')
def gestionar_plantilla(request):
    list_plantilla = Plantilla.objects.all()
    form = PlantillaForm(request.POST or None)
    context = {'list_plantilla': list_plantilla, 'form': form}
    return render(request, 'Gestionar_Plantilla.html', context)


@permission_required('plantilla.add_plantilla', login_url='home_principal')
def adicionar_plantilla(request):
    form = PlantillaForm(request.POST or None)
    if form.is_valid():
        plantilla = Plantilla(
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
            return redirect(reverse_lazy('gestionarPlantilla'))
    if request.method == 'POST':
        list_plantilla = Plantilla.objects.all()
        context = {'list_plantilla': list_plantilla, 'form': form}
        return render(request, 'Gestionar_Plantilla.html', context)


@permission_required('plantilla.change_plantilla', login_url='home_principal')
def editar_plantilla(request, pk):
    plantilla = Plantilla.objects.get(id=pk)
    form = PlantillaForm(request.POST or None, instance=plantilla)
    if form.is_valid():
        plantilla.cant_plazas = form.cleaned_data['cant_plazas']
        plantilla.save()
        return redirect(reverse_lazy('gestionarPlantilla'))
    cal = Plantilla.objects.all()
    context = {'list_plantilla': cal, 'edit': pk, 'object': plantilla, 'form': form}
    return render(request, 'Gestionar_Plantilla.html', context)


@permission_required('plantilla.change_plantilla', login_url='home_principal')
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
    return redirect(reverse_lazy('gestionarPlantilla'))


# este es el metodo que muestra el alerta de eliminacion y despues elimina
@permission_required('plantilla.delete_plantilla', login_url='home_principal')
def eliminar_plantilla(request, pk):
    plantilla = Plantilla.objects.get(id=pk)
    if request.method == 'GET':
        context = {'object': plantilla}
        return render(request, 'Eliminar_Plantilla.html', context)
    else:
        if int(plantilla.cant_plazas) == int(plantilla.disponibles):
            plantilla.delete()
            return redirect(reverse_lazy('gestionarPlantilla'))
        else:
            list_plantilla = Plantilla.objects.all()
            form = PlantillaForm(None)
            context = {'list_plantilla': list_plantilla, 'form': form,
                       'errores': 'Imposible eliminar plantilla con plazas ocupadas.'}
            return render(request, 'Gestionar_Plantilla.html', context)


# @permission_required('plantilla', login_url='home_principal')
def dpto_por_unidad(request, pk, area=None):
    if area:
        departamentos = Departamento.objects.filter(
            unidad=pk, dirige_id__isnull=True
        ).order_by('codigo').values('nombre', 'id', 'codigo')
    else:
        departamentos = Departamento.objects.filter(unidad=pk).annotate(dirige_nombre=F('dirige__nombre')).values(
            'nombre', 'id', 'codigo', 'dirige_nombre'
        ).order_by('codigo')
    response = [{"success": 1, "result": list(departamentos)}]
    return HttpResponse(json.dumps(response), content_type='application/json')


########################################################################
# Reports
#

def request_plantilla_all(fltr=None):
    queryset = Alta.objects.all()
    if fltr == 'rg':
        queryset = queryset.filter(t_contrato='4')
    elif fltr == 'cd':
        queryset = queryset.filter(Q(t_contrato='3') | Q(t_contrato='7') | Q(t_contrato='6'))
    elif fltr == 'ci':
        queryset = queryset.filter(Q(t_contrato='1') | Q(t_contrato='2'))
    queryset = queryset.annotate(
        unidad_nombre=F('unidad_org__nombre'),
        dpto_nombre=F('departamento__nombre'),
        dpto_codigo=F('departamento__codigo'),
        cargo_nombre=F('cargo__nombre'),
        grupo_escala=F('escala_salarial__grupo')
    ).order_by('dpto_codigo', 'org_plantilla', '-grupo_escala')
    return queryset


def request_report():
    queryset = Alta.objects.filter(Q(t_contrato='1') | Q(t_contrato='2')).values('org_plantilla').annotate(
        unidad_nombre=F('unidad_org__nombre'),
        dpto_nombre=F('departamento__nombre'),
        dpto_codigo=F('departamento__codigo'),
        cargo_nombre=F('cargo__nombre'),
        grupo_escala=F('escala_salarial__grupo')
    ).values(
        'id', 'primer_nombre', 'segundo_nombre', 'apellidos', 'ci', 'categoria', 't_plantilla', 'org_plantilla',
        'sexo', 'escolaridad', 'salario_escala', 'incre_res', 'cies', 'sal_plus', 'antiguedad', 'cat_cient',
        'fecha_contrato', 'sal_cat_cient', 'salario_total', 'salario_jornada_laboral', 'unidad_org_id',
        'departamento_id', 'unidad_nombre', 'dpto_nombre', 'cargo_nombre', 'grupo_escala', 'dpto_codigo'
    ).order_by('dpto_codigo', 'org_plantilla', '-grupo_escala')

    return {'queryset': queryset}


# def request_plantilla_all():
#    queryset = Alta.objects.annotate(
#        unidad_nombre=F('unidad_org__nombre'),
#        dpto_nombre=F('departamento__nombre'),
#        dpto_codigo=F('departamento__codigo'),
#        cargo_nombre=F('cargo__nombre'),
#        grupo_escala=F('escala_salarial__grupo')
#    ).order_by('dpto_codigo', 'org_plantilla', '-grupo_escala')
#    return {'queryset': queryset}


def request_report_otro():
    sql = """
            SELECT
                adm_unidadorg.nombre AS "nombreUO",
                adm_unidadorg.id AS "idUO",
                adm_departamento.nombre AS "nombreDep",
                ges_trab_trabajador.primer_nombre AS nombre,
                ges_trab_trabajador.segundo_nombre AS "segundo_nombre",
                ges_trab_trabajador.apellidos AS apellidos,
                ges_trab_trabajador.categoria AS categoria,
                ges_trab_trabajador.t_plantilla,
                ges_trab_trabajador.org_plantilla,
                adm_cargo.nombre AS "nombreCargo",
                adm_departamento.id AS dptoid,
                ges_trab_trabajador.sexo,
                ges_trab_trabajador.ci,
                adm_escalasalarial.grupo AS "grupoEscala",
                ges_trab_trabajador.escolaridad,
                ges_trab_trabajador.salario_escala,
                ges_trab_trabajador.incre_res,
                ges_trab_trabajador.cies,
                ges_trab_trabajador.sal_plus,
                ges_trab_trabajador.antiguedad,
                ges_trab_trabajador.cat_cient,
                ges_trab_trabajador.fecha_contrato,
                ges_trab_trabajador.id AS id,
                adm_departamento.codigo AS dptoCod,
                ges_trab_trabajador.sal_cat_cient,
                ges_trab_trabajador.salario_total,
                ges_trab_trabajador.salario_jornada_laboral,
                ges_trab_trabajador.j_laboral
            FROM
                public.adm_unidadorg,
                public.adm_departamento,
                public.ges_trab_trabajador,
                public.adm_cargo,
                public.adm_escalasalarial
            WHERE
                adm_unidadorg.id = adm_departamento.unidad_id AND
                adm_departamento.id = ges_trab_trabajador.departamento_id AND
                ges_trab_trabajador.fecha_baja is Null AND
                adm_cargo.id = ges_trab_trabajador.cargo_id AND
                adm_escalasalarial.id = ges_trab_trabajador.escala_salarial_id AND
                (ges_trab_trabajador.t_contrato='1' OR ges_trab_trabajador.t_contrato='2')
            GROUP BY
                adm_unidadorg.id,
                adm_departamento.nombre,
                ges_trab_trabajador.primer_nombre,
                ges_trab_trabajador.segundo_nombre,
                ges_trab_trabajador.apellidos,
                ges_trab_trabajador.categoria,
                adm_cargo.nombre,
                adm_departamento.id,
                ges_trab_trabajador.sexo,
                ges_trab_trabajador.ci,
                adm_escalasalarial.grupo,
                ges_trab_trabajador.escolaridad,
                adm_escalasalarial.salario_escala,
                ges_trab_trabajador.incre_res,
                ges_trab_trabajador.cies,
                ges_trab_trabajador.sal_plus,
                ges_trab_trabajador.antiguedad,
                ges_trab_trabajador.cat_cient,
                ges_trab_trabajador.fecha_alta,
                ges_trab_trabajador.id,
                ges_trab_trabajador.org_plantilla
            ORDER BY
                adm_unidadorg.id, adm_departamento.codigo, ges_trab_trabajador.org_plantilla;
          """
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


@permission_required('plantilla.report_plantilla', login_url='home_principal')
def reporte(request):
    return render(request, 'Reporte_Plantilla.html', request_report())


# @permission_required('plantilla.report_plantilla', login_url='home_principal')
# def reporte_plantilla_general(request):
#     return render(request, 'plantilla_general.html', request_plantilla_all())


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


@permission_required('plantilla.export_plantilla', login_url='home_principal')
def exportar(request):
    template_path = 'Reporte_Plantilla_template.html'
    context = request_report_otro()
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
    sql = """
            SELECT
                adm_unidadorg.nombre AS "nombreUO",
                adm_unidadorg.id AS "idUO",
                adm_departamento.nombre AS "nombreDep",
                ges_trab_trabajador.primer_nombre AS nombre,
                ges_trab_trabajador.segundo_nombre AS "segundo_nombre",
                ges_trab_trabajador.apellidos AS apellidos,
                ges_trab_trabajador.categoria AS categoria,
                ges_trab_trabajador.org_plantilla,
                adm_cargo.nombre AS "nombreCargo",
                adm_departamento.id AS dptoid,
                ges_trab_trabajador.sexo, ges_trab_trabajador.ci,
                adm_escalasalarial.grupo AS "grupoEscala",
                ges_trab_trabajador.escolaridad,
                ges_trab_trabajador.salario_escala, ges_trab_trabajador.incre_res,
                ges_trab_trabajador.cies,
                ges_trab_trabajador.antiguedad, ges_trab_trabajador.fecha_contrato,
                ges_trab_trabajador.id AS id, adm_departamento.codigo AS dptoCod,
                ges_trab_trabajador.sal_cat_cient, ges_trab_trabajador.salario_total,
                ges_trab_trabajador.salario_jornada_laboral,
                ges_trab_trabajador.j_laboral
            FROM
                public.adm_unidadorg, public.adm_departamento,
                public.ges_trab_trabajador, public.adm_cargo,
                public.adm_escalasalarial
            WHERE adm_unidadorg.id = adm_departamento.unidad_id
                AND adm_departamento.id = ges_trab_trabajador.departamento_id
                AND ges_trab_trabajador.fecha_baja is Null
                AND adm_cargo.id = ges_trab_trabajador.cargo_id
                AND adm_escalasalarial.id = ges_trab_trabajador.escala_salarial_id
                AND ges_trab_trabajador.t_contrato='4'
            GROUP BY adm_unidadorg.id, adm_departamento.nombre,
            ges_trab_trabajador.primer_nombre,
                ges_trab_trabajador.segundo_nombre, ges_trab_trabajador.apellidos,
                ges_trab_trabajador.categoria,
                adm_cargo.nombre, adm_departamento.id, ges_trab_trabajador.sexo,
                ges_trab_trabajador.ci,
                adm_escalasalarial.grupo, ges_trab_trabajador.escolaridad,
                adm_escalasalarial.salario_escala,
                ges_trab_trabajador.incre_res, ges_trab_trabajador.cies,
                ges_trab_trabajador.sal_plus,
                ges_trab_trabajador.antiguedad, ges_trab_trabajador.cat_cient,
                ges_trab_trabajador.fecha_alta,
                ges_trab_trabajador.id, ges_trab_trabajador.org_plantilla
            ORDER BY adm_unidadorg.id, adm_departamento.codigo, ges_trab_trabajador.org_plantilla;
          """
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


@permission_required('plantilla.report_plantilla', login_url='home_principal')
def reporte_graduados(request):
    return render(request, 'Reporte_Plantilla_Graduados.html', request_report_graduados())


@permission_required('plantilla.export_plantilla', login_url='home_principal')
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
    sql = """
            SELECT
                adm_unidadorg.nombre AS "nombreUO",
                adm_unidadorg.id AS "idUO",
                adm_departamento.nombre AS "nombreDep",
                ges_trab_trabajador.primer_nombre AS nombre,
                ges_trab_trabajador.segundo_nombre AS "segundo_nombre",
                ges_trab_trabajador.apellidos AS apellidos,
                ges_trab_trabajador.categoria AS categoria,
                ges_trab_trabajador.org_plantilla,
                adm_cargo.nombre AS "nombreCargo",
                adm_departamento.id AS dptoid, ges_trab_trabajador.sexo,
                ges_trab_trabajador.ci,
                adm_escalasalarial.grupo AS "grupoEscala", ges_trab_trabajador.escolaridad,
                ges_trab_trabajador.salario_escala, ges_trab_trabajador.incre_res,
                ges_trab_trabajador.cies,
                ges_trab_trabajador.sal_plus, ges_trab_trabajador.antiguedad,
                ges_trab_trabajador.cat_cient,
                ges_trab_trabajador.fecha_contrato, ges_trab_trabajador.id AS id,
                adm_departamento.codigo AS dptoCod,
                ges_trab_trabajador.sal_cat_cient, ges_trab_trabajador.salario_total,
                ges_trab_trabajador.salario_jornada_laboral,
                ges_trab_trabajador.j_laboral
            FROM
                adm_unidadorg, adm_departamento, ges_trab_trabajador,
                adm_cargo, adm_escalasalarial
            WHERE adm_unidadorg.id = adm_departamento.unidad_id
                AND adm_departamento.id = ges_trab_trabajador.departamento_id
                AND ges_trab_trabajador.fecha_baja is Null
                AND adm_cargo.id = ges_trab_trabajador.cargo_id
                AND adm_escalasalarial.id = ges_trab_trabajador.escala_salarial_id
                AND (ges_trab_trabajador.t_contrato='3' OR ges_trab_trabajador.t_contrato='6')
            GROUP BY
                adm_unidadorg.id, adm_departamento.nombre,
                ges_trab_trabajador.primer_nombre,
                ges_trab_trabajador.segundo_nombre, ges_trab_trabajador.apellidos,
                ges_trab_trabajador.categoria,
                adm_cargo.nombre, adm_departamento.id, ges_trab_trabajador.sexo,
                ges_trab_trabajador.ci,
                adm_escalasalarial.grupo, ges_trab_trabajador.escolaridad,
                adm_escalasalarial.salario_escala,
                ges_trab_trabajador.incre_res, ges_trab_trabajador.cies,
                ges_trab_trabajador.sal_plus,
                ges_trab_trabajador.antiguedad, ges_trab_trabajador.cat_cient,
                ges_trab_trabajador.fecha_alta,
                ges_trab_trabajador.id, ges_trab_trabajador.org_plantilla
            ORDER BY
                adm_unidadorg.id, adm_departamento.codigo, ges_trab_trabajador.org_plantilla;
          """
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


@permission_required('plantilla.report_plantilla',  login_url='home_principal')
def reporte_contratos(request):
    return render(request, 'Reporte_Plantilla_Contratos.html', request_report_contratos())


@permission_required('plantilla.export_plantilla', login_url='home_principal')
def exportar_contratos(request):
    template_path = 'Reporte_Plantilla_Contratos_template.html'
    context = request_report_contratos()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte_Plantilla_Contratos.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisastatus = pisa.CreatePDF(html, dest=response, link_callback=link_callback, encoding='utf8')
    if pisastatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisastatus.err,
                                                                               html))
    return response


@permission_required('plantilla.read_plantilla', login_url='home_principal')
def preview_plantilla_general(request):
    context = {
        'queryset': request_plantilla_all(),
        'title': 'Plantilla General',
        'export_pdf': 'plantilla-general_export'
    }
    return render(request, 'preview_plantilla.html', context)


@permission_required('plantilla.read_plantilla', login_url='home_principal')
def preview_plantilla_cd(request):
    context = {
        'queryset': request_plantilla_all('cd'),
        'title': 'Plantilla Contratos',
        'export_pdf': 'plantilla-cd_export'
    }
    return render(request, 'preview_plantilla.html', context)


@permission_required('plantilla.read_plantilla', login_url='home_principal')
def preview_plantilla_ci(request):
    context = {
        'queryset': request_plantilla_all('ci'),
        'title': 'Plantilla Contratos Indeterminados',
        'export_pdf': 'plantilla-ci_export'
    }
    return render(request, 'preview_plantilla.html', context)


@permission_required('plantilla.read_plantilla', login_url='home_principal')
def preview_plantilla_rg(request):
    context = {
        'queryset': request_plantilla_all('rg'),
        'title': 'PLANTILLA RECIEN GRADUADOS',
        'export_pdf': 'plantilla-rg_export'
    }
    return render(request, 'preview_plantilla.html', context)


@permission_required('plantilla.export_plantilla', login_url='home_principal')
def export_plantilla_general(request):
    context = {
        'queryset': request_plantilla_all(),
        'title': 'Plantilla General'
    }
    return export_factory(context)


@permission_required('plantilla.export_plantilla', login_url='home_principal')
def export_plantilla_rg(request):
    context = {
        'queryset': request_plantilla_all('rg'),
        'title': 'PLANTILLA RECIEN GRADUADOS'
    }
    return export_factory(context)


@permission_required('plantilla.export_plantilla', login_url='home_principal')
def export_plantilla_cd(request):
    context = {
        'queryset': request_plantilla_all('cd'),
        'title': 'Plantilla Contratos'
    }
    return export_factory(context)


@permission_required('plantilla.export_plantilla', login_url='home_principal')
def export_plantilla_ci(request):
    context = {
        'queryset': request_plantilla_all('ci'),
        'title': 'Plantilla Contratos Indeterminados'
    }
    return export_factory(context)


def export_factory(context):
    template_path = 'export_plantilla.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{context["title"]}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisastatus = pisa.CreatePDF(html, dest=response, link_callback=link_callback, encoding='utf8')
    if pisastatus.err:
        return HttpResponse(
            'We had some errors with code %s <pre>%s</pre>' % (pisastatus.err, html)
        )
    return response


def calzado_medios_de_proteccion(request):
    context = _request_listado_calzado()
    context['title'] = 'Calzado Medios de Protecci&oacute;n'
    template_name = 'reports/plantilla/calzado.html'
    return generate_pisa_report(context, template_name, context['title'])


def _request_listado_calzado():
    queryset = Alta.objects.annotate(
        uni_nombre=F('unidad_org__nombre'),
        dep_nombre=F('departamento__nombre'),
        cargo_nombre=F('cargo__nombre')
    ).order_by('departamento__codigo', 'org_plantilla')
    return {'object_list': queryset}
