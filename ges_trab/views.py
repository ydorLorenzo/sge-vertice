import json
from datetime import datetime, date
from decimal import Decimal

from django.contrib.auth.decorators import permission_required
from django.db.models import F, Sum, Count
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import render, redirect

from plantilla.models import Cargo
from rechum.utils import generate_pisa_report
from rechum.views import SgeListView, SgeCreateView, SgeDetailView, SgeUpdateView, SgeDeleteView, TemplateView
from adm.models import EscalaSalarial, Especialidad
from .filters import TrabajadorFilter
from .forms import *
from .models import *

check = False

MOTIVOS_BAJA = [
    {"key": '01', "value": 'Rescisión del contrato a voluntad del trabajador'},
    {"key": '02', "value": 'Motivos salariales'},
    {"key": '03', "value": 'Deficiente organización del trabajo'},
    {"key": '04', "value": 'Lejanía del centro de trabajo'},
    {"key": '05', "value": 'Inconveniencia del horario de trabajo'},
    {"key": '06', "value": 'No trabajar dentro de la especialidad'},
    {"key": '07', "value": 'Condiciones anormales de trabajo'},
    {"key": '08', "value": 'Escasa posibilidad de superación'},
    {"key": '09', "value": 'Problemas de vivienda y o ausencia de servicios sociales'},
    {"key": '10', "value": 'Inconformidad con los métodos de dirección'},
    {"key": '11', "value": 'Matrimonio atención a menores y familiares'},
    {"key": '12', "value": 'Bajas de trabajadores por sanción laboral'},
    {
        "key": '13',
        "value":
            'Bajas por no reincorporarse después de cumplido el período de vacaciones o licencia no retribuida'
    },
    {"key": '14', "value": 'Bajas por salida del país'},
    {"key": '15', "value": 'Bajas por Jubilación'},
    {"key": '16', "value": 'Bajas por Fallecimiento'},
    {"key": '17', "value": 'Otras bajas por fluctuación'}
]


class TrabListView(SgeListView):
    permission_required = 'ges_trab.read_trabajador'
    model = Trabajador
    template_name = 'trabajador/list.html'
    raise_exception = True
    queryset = Trabajador.objects.filter(fecha_baja__isnull=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        object_list = queryset.annotate(
            departamento_nombre=F('departamento__nombre'),
            grupo_escala=F('escala_salarial__grupo'),
            especialidad_nombre=F('especialidad__nombre')
        )
        return super().get_context_data(object_list=object_list, **kwargs)


class TrabCreateView(SgeCreateView):
    permission_required = 'ges_trab.add_trabajador'
    model = Trabajador
    form_class = TrabajadorForm
    template_name = 'trabajador/create.html'
    success_url = reverse_lazy('trabajador_create')


class TrabDetailView(SgeDetailView):
    permission_required = 'ges_trab.read_trabajador'
    model = Trabajador
    template_name = 'trabajador/detail.html'


class TrabUpdateView(SgeUpdateView):
    permission_required = 'ges_trab.change_trabajador'
    model = Trabajador
    form_class = TrabajadorForm
    template_name = 'trabajador/create.html'
    success_url = reverse_lazy('trabajador_list')


class TrabDeleteView(SgeDeleteView):
    permission_required = 'ges_trab.delete_trabajador'
    model = Trabajador
    success_url = reverse_lazy('trabajador_list')


class ReportsView(TemplateView):
    template_name = 'reports/trabajadores.html'


class BajaListView(SgeListView):
    model = BajaOther
    template_name = 'bajas/list.html'
    permission_required = 'ges_trab.read_trabajador'

    def get_context_data(self, *, object_list=None, **kwargs):
        object_list = self.model.objects.annotate(
            especialidad_nombre=F('especialidad__nombre')
        ).order_by('fecha_baja')
        return super().get_context_data(object_list=object_list, **kwargs)


class BajaCreateView(SgeCreateView):
    model = BajaOther
    template_name = 'bajas/create.html'
    permission_required = 'ges_trab.add_trabajador'
    fields = '__all__'


class BajaDetailView(SgeDetailView):
    model = BajaOther
    template_name = 'bajas/detail.html'
    permission_required = 'ges_trab.read_trabajador'


@permission_required('ges_trab.read_movimiento', login_url='home_principal')
def listar_movimiento(request):
    list_movimiento = Movimiento.objects.all()
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    fecha_inicio_convert = ''
    fecha_fin_convert = ''
    if fecha_inicio:
        fecha_inicio_convert = datetime.strptime(fecha_inicio, '%d/%m/%Y').strftime('%Y-%m-%d')
    if fecha_fin:
        fecha_fin_convert = datetime.strptime(fecha_fin, '%d/%m/%Y').strftime('%Y-%m-%d')

    if fecha_inicio and fecha_fin:
        list_movimiento = Movimiento.objects.filter(fecha__range=[fecha_inicio_convert, fecha_fin_convert])

    elif not fecha_fin and fecha_inicio:
        list_movimiento = Movimiento.objects.filter(fecha__gte=fecha_inicio_convert)
    elif fecha_fin and not fecha_inicio:
        list_movimiento = Movimiento.objects.filter(fecha__lte=fecha_fin_convert)
    else:
        list_movimiento = Movimiento.objects.all()
    return render(request, 'Listar_Movimiento.html', {'list_movimiento': list_movimiento})


@permission_required('ges_trab', login_url='home_principal')
def listar_disponible(request):
    list_disponible = Disponible.objects.all()
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio and fecha_fin:

        fecha_inicio_convert = datetime.strptime(fecha_inicio, '%d/%m/%Y').strftime('%Y-%m-%d')
        fecha_fin_convert = datetime.strptime(fecha_fin, '%d/%m/%Y').strftime('%Y-%m-%d')
        list_disponible = Disponible.objects.filter(fecha__range=[fecha_inicio_convert, fecha_fin_convert])

    elif not fecha_fin and fecha_inicio:

        fecha_inicio_convert = datetime.strptime(fecha_inicio, '%d/%m/%Y').strftime('%Y-%m-%d')
        list_disponible = Disponible.objects.filter(fecha__range=[fecha_inicio_convert, '2200-01-01'])
    elif fecha_fin and not fecha_inicio:
        fecha_fin_convert = datetime.strptime(fecha_fin, '%d/%m/%Y').strftime('%Y-%m-%d')
        list_disponible = Disponible.objects.filter(fecha__range=['1970-01-01', fecha_fin_convert])
    else:
        list_disponible = Disponible.objects.all()

    return render(request, 'Listar_Disponibilidad.html', {'list_disponible': list_disponible})


@permission_required(('ges_trab.read_cpl', 'ges_trab.add_cpl'), login_url='home_principal')
def gestionar_cpl(request):
    list_cpl = Cpl.objects.all()
    context = {'list_cpl': list_cpl}
    return render(request, 'Gestionar_cpl.html', context)


@permission_required('ges_trab.read_nucleofamiliar', login_url='home_principal')
def gestionar_nucleo_familiar(request):
    list_nucleo_fam = NucleoFamiliar.objects.all()
    context = {'list_nucleo_fam': list_nucleo_fam}
    return render(request, 'Gestionar_Nucleo_Familiar.html', context)


@permission_required('ges_trab.read_trabajador', login_url='home_principal')
def gestionar_trabajador(request):
    list_trabajador = Trabajador.objects.filter(fecha_baja__isnull=True).select_related("unidad_org").select_related(
        "departamento").select_related("cargo").select_related("escala_salarial").select_related(
        "actividad").select_related("calificacion").select_related("especialidad").order_by("departamento__codigo", "org_plantilla")
    trabajador_filter = TrabajadorFilter(request.GET, queryset=list_trabajador)

    return render(request, 'Gestionar_Trabajador.html', {'trabajador_filter': trabajador_filter})


@permission_required('ges_trab.read_trabajador', login_url='home_principal')
def informaciones_trabajador(request):
    list_trabajador = Trabajador.objects.filter(fecha_baja__isnull=True).select_related("unidad_org").select_related(
        "departamento").select_related("cargo").select_related("escala_salarial").select_related(
        "actividad").select_related("calificacion").select_related("especialidad").order_by("departamento__codigo", "org_plantilla")
    trabajador_filter = TrabajadorFilter(request.GET, queryset=list_trabajador)

    return render(request, 'Informaciones_Trabajador.html', {'trabajador_filter': trabajador_filter})


@permission_required('ges_trab.read_trabajador', login_url='home_principal')
def gestionar_bajatrabajador(request):
    list_baja = Trabajador.objects.filter(fecha_baja__isnull=False)
    motivos_baja = {
        "01": 'Rescisión del contrato a voluntad del trabajador',
        "02": 'Motivos salariales',
        "03": 'Deficiente organización del trabajo',
        "04": 'Lejanía del centro de trabajo',
        "05": 'Inconveniencia del horario de trabajo',
        "06": 'No trabajar dentro de la especialidad',
        "07": 'Condiciones anormales de trabajo',
        "08": 'Escasa posibilidad de superación',
        "09": 'Problemas de vivienda y o ausencia de servicios sociales',
        "10": 'Inconformidad con los métodos de dirección',
        "11": 'Matrimonio atención a menores y familiares',
        "12": 'Bajas de trabajadores por sanción laboral',
        "13": 'Bajas por no reincorporarse después de cumplido el período de vacaciones o licencia no retribuida',
        "14": 'Bajas por salida del país',
        "15": 'Bajas por Jubilación',
        "16": 'Bajas por Fallecimiento',
        "17": 'Otras bajas por fluctuación'
    }
    return render(request, 'Gestionar_Baja.html', {'list_baja': list_baja, 'motivos': motivos_baja})


@permission_required('ges_trab.add_trabajador', login_url='home_principal')
def adicionar_trabajador_inline(request, trabajador_id=None):
    import datetime as dt_base
    globals()['check'] = False
    if trabajador_id:
        globals()['check'] = True
        trabajador = Trabajador.objects.get(pk=trabajador_id)
        cargo_id2 = trabajador.cargo_id
        departamento_id2 = trabajador.departamento_id
        cargo_bd = trabajador.cargo.nombre
        departamento_bd = trabajador.departamento.nombre
        cies_bd = trabajador.cies
        antiguedad_bd = trabajador.antiguedad
        salario_total_bd = trabajador.salario_total
        sal_plus_bd = trabajador.sal_plus
        incre_res_bd = trabajador.incre_res
        salario_escala_bd = trabajador.salario_escala
        sal_cat_cient_bd = trabajador.sal_cat_cient
        escala_salarial_bd = trabajador.escala_salarial
        por_anti_bd = trabajador.por_anti
        categoria_bd = trabajador.categoria

    else:
        trabajador = Trabajador()

    NucleoFamiliarFormSet = inlineformset_factory(
        Trabajador, NucleoFamiliar, fields=(
            'parentesco', 'fecha_nac', 'enfermedades', 'salario_dev', 'vinc_lab'
        ), form=NucleoFamiliarForm, extra=3, can_delete=True)
    if request.method == 'POST':
        inline = NucleoFamiliarFormSet(request.POST, instance=trabajador)  # , prefix='inline'
        form = TrabajadorForm(request.POST, request.FILES, instance=trabajador)

        if form.is_valid() and inline.is_valid():
            # Esto es para el rango de edad
            ci = form.cleaned_data['ci']
            semi_year = int(ci[0: 2])
            if 45 < semi_year < 99:
                fecha_nacimiento = '19' + ci[0: 2] + '-' + ci[2: 4] + '-' + ci[4: 6]
            else:
                fecha_nacimiento = '20' + ci[0: 2] + '-' + ci[2: 4] + '-' + ci[4: 6]
            trabajador.fecha_nac = fecha_nacimiento
            # Esto es para decrementar la disponibilidad de un cargo
            if not check:
                cargo_id = (form.cleaned_data['cargo'])
                departamento_id = (form.cleaned_data['departamento'])
                plantilla = Plantilla.objects.filter(cargo_id=cargo_id, departamento_id=departamento_id).get()
                plantilla.disponibles = plantilla.disponibles - 1
                plantilla.save()
            # Esto es para el salario por categoria cientifica
            if form.cleaned_data['cat_cient'] == '2':
                trabajador.sal_cat_cient = 80
            elif form.cleaned_data['cat_cient'] == '3':
                trabajador.sal_cat_cient = 150
            else:
                trabajador.sal_cat_cient = 0
            # Esto es para el salario total
            salario_escala = (form.cleaned_data['salario_escala'])
            incre_res = (form.cleaned_data['incre_res'])
            cies = (form.cleaned_data['cies'])
            sal_plus = (form.cleaned_data['sal_plus'])
            sal_cond_anor = (form.cleaned_data['sal_cond_anor'])
            antiguedad = (form.cleaned_data['antiguedad'])
            j_laboral = (form.cleaned_data['j_laboral'])
            escala_salarial = (form.cleaned_data['escala_salarial'])
            categoria = (form.cleaned_data['categoria'])
            if not j_laboral:
                trabajador.salario_total = salario_escala + incre_res + cies + sal_plus + sal_cond_anor + antiguedad + trabajador.sal_cat_cient
            else:
                trabajador_salario_jornada_laboral = (salario_escala / Decimal(190.60)) * 208
                trabajador.salario_jornada_laboral = round(trabajador_salario_jornada_laboral, 2)

                trabajador_salario_total = ((salario_escala / Decimal(
                    190.60)) * 208) + incre_res + cies + sal_plus + sal_cond_anor + antiguedad + trabajador.sal_cat_cient
                trabajador.salario_total = round(trabajador_salario_total, 2)
            # Esto es para registrar el movimiento
            if trabajador_id:
                departamento_form = form.cleaned_data['departamento'].nombre
                cargo_form = form.cleaned_data['cargo'].nombre
                departamento = form.cleaned_data['departamento']
                cargo = form.cleaned_data['cargo']
                antiguedad = form.cleaned_data['antiguedad']
                por_anti = form.cleaned_data['por_anti']
                if (departamento_form != departamento_bd) or (cargo_form != cargo_bd) or (por_anti != por_anti_bd):
                    # Aumentar disponibilidad
                    plantilla2 = Plantilla.objects.filter(cargo_id=cargo_id2, departamento_id=departamento_id2).get()
                    plantilla2.disponibles = plantilla2.disponibles + 1
                    plantilla2.save()
                    # Decrementar disponibilidad
                    plantilla = Plantilla.objects.filter(cargo_id=cargo, departamento_id=departamento).get()
                    plantilla.disponibles = plantilla.disponibles - 1
                    plantilla.save()
                    # Movimiento
                    movimiento = Movimiento()
                    movimiento.trabajador_id = trabajador_id
                    movimiento.area_act = departamento
                    movimiento.area_ant = departamento_bd
                    movimiento.cargo_act = cargo
                    movimiento.cargo_ant = cargo_bd
                    movimiento.cies_ant = cies_bd
                    movimiento.cies_act = cies
                    movimiento.antiguedad_ant = antiguedad_bd
                    movimiento.antiguedad_act = antiguedad
                    movimiento.categoria_ant = categoria_bd
                    movimiento.categoria_act = categoria
                    movimiento.incre_res_act = incre_res
                    movimiento.incre_res_ant = incre_res_bd
                    movimiento.salario_escala_ant = salario_escala_bd
                    movimiento.salario_escala_act = salario_escala
                    movimiento.escala_salarial_ant = escala_salarial_bd
                    movimiento.escala_salarial_act = escala_salarial
                    movimiento.salario_total_ant = salario_total_bd
                    movimiento.salario_total_act = Decimal(salario_escala) + Decimal(incre_res) + Decimal(
                        cies) + Decimal(sal_plus) + Decimal(sal_cond_anor) + Decimal(
                        antiguedad) + trabajador.sal_cat_cient
                    movimiento.sal_plus_ant = sal_plus_bd
                    movimiento.sal_plus_act = sal_plus
                    movimiento.fecha = dt_base.datetime.today()
                    movimiento.save()
            # Esto es si el contrato es disponible
            t_contrato = (form.cleaned_data['t_contrato'])
            if t_contrato == '8':
                disponible = Disponible()
                disponible.trabajador_id = trabajador.pk
                disponible.fecha = dt_base.datetime.today()
                disponible.save()
            form.save()
            inline.save()
            if request.POST.get("guardar"):
                return redirect('GestionarTrabajador')
            elif request.POST.get("guardaradicionar"):
                return HttpResponse('AdicionarTrabajador')
    else:
        inline = NucleoFamiliarFormSet(instance=trabajador)
        if trabajador_id is None:
            form = TrabajadorAltaForm(instance=trabajador)
        else:
            form = TrabajadorForm(instance=trabajador)
    return render(request, 'Adicionar_Trabajador.html', {'inline': inline, 'form': form, 'pk': trabajador.id})


@permission_required('ges_trab.change_trabajador', login_url='home_principal')
def bajaeliminar(request, pk):
    trabajador = Trabajador.objects.get(pk=pk)

    if request.method == 'GET':
        return render(
            request, 'Baja_Trabajador.html',
            {'trabajador': trabajador, 'motivos': MOTIVOS_BAJA}
        )
    else:
        causal = request.POST.get('causa', None)
        now_date_str = datetime.now().strftime('%d/%m/%Y')
        fecha_baja_str = request.POST.get('fecha_baja', now_date_str)
        fecha_baja = datetime.strptime(fecha_baja_str, '%d/%m/%Y')
        plantilla = Plantilla.objects.filter(cargo_id=trabajador.cargo_id,
                                             departamento_id=trabajador.departamento_id).get()
        # ------------------------
        trabajador.fecha_baja = fecha_baja
        trabajador.motivo_baja = causal
        trabajador.save()
        # Aumentar disponibilidad del cargo
        plantilla.disponibles = plantilla.disponibles + 1
        plantilla.save()
        return redirect('GestionarTrabajador')


@permission_required('ges_trab.change_movimiento', login_url='home_principal')
def editar_movimiento(request, pk):
    import datetime as dt_base
    movimiento = Movimiento.objects.get(pk=pk)

    if request.method == 'POST':
        fecham = request.POST.get('fecha_movimiento')
        fechamov = dt_base.datetime.strptime(fecham, '%d/%m/%Y').strftime('%Y-%m-%d')
        select = request.POST.get('select', '')
        resolucion = request.POST.get('resolucion', '')
        tipom = resolucion + ' ' + select
        movimiento.fecha = fechamov
        movimiento.tipo = tipom
        movimiento.save()
        return redirect('ListarMovimiento')
    return render(request, 'Editar_Movimiento.html', {'movimiento': movimiento})


@permission_required('ges_trab.change_trabajador', login_url='home_principal')
def editar_baja(request, pk):
    import datetime as dt_module
    baja = Trabajador.objects.filter(fecha_baja__isnull=False).get(pk=pk)

    if request.method == 'POST':
        fechab = request.POST.get('fecha_baja')
        motivo_baja = request.POST.get('causa_baja')
        fechabaj = dt_module.datetime.strptime(fechab, '%d/%m/%Y').strftime('%Y-%m-%d')

        baja.fecha_baja = fechabaj
        baja.motivo_baja = motivo_baja

        baja.save()
        return redirect('GestionarBaja')
    return render(request, 'Editar_Baja.html', {'baja': baja, 'motivos': MOTIVOS_BAJA})


@permission_required('ges_trab.delete_nucleofamiliar', login_url='home_principal')
def eliminar_familiar(request, pk):
    nucleof = NucleoFamiliar.objects.filter(pk=pk)
    nucleof.delete()


@permission_required('ges_trab.change_trabajador', login_url='home_principal')
def daralta(request, pk):
    baja = Trabajador.objects.filter(fecha_baja__isnull=False).get(pk=pk)
    if request.method == 'GET':
        form = TrabajadorAltaBajaForm(instance=baja)
        return render(request, 'Alta_Trabajador.html', {'baja': form, 'pk': pk})
    elif request.method == 'POST':
        form = TrabajadorAltaBajaForm(request.POST)
        if form.is_valid():
            baja.update(form.cleaned_data)
            baja.update(fecha_baja=None)
            # todo verificar plantilla
            return redirect('GestionarBaja')
        return render(request, 'Alta_Trabajador.html', {'baja': form, 'pk': pk})
    else:
        return redirect('GestionarBaja')


###
# Ajax queries
###
@permission_required('ges_trab.change_trabajador', login_url='home_principal')
def salarioescala_por_escalasarial(request, pk):
    escalasalarial = EscalaSalarial.objects.filter(pk=pk)
    datos = [{'salario_escala': str(salarioescala.salario_escala), 'tarifa_horaria': str(salarioescala.tarifa_horaria),
              'id': salarioescala.id} for salarioescala in escalasalarial]
    response = [{"success": 1, "result": datos}]
    return HttpResponse(json.dumps(response), content_type='application/json')


@permission_required('ges_trab.change_trabajador', login_url='home_principal')
def cargos_disponibles(request, departamento_id):
    cargos = Cargo.objects.filter(plantilla__departamento_id=departamento_id).annotate(
        plantilla_disp=Sum('plantilla__disponibles')).exclude(plantilla_disp=0).values('id', 'nombre')
    response = [{"success": 1, "result": list(cargos)}]
    return HttpResponse(json.dumps(response), content_type='application/json')


@permission_required('ges_trab.change_trabajador', login_url='home_principal')
def calificacion_especialidad(request, calificacion_id):
    especialidades = list(Especialidad.objects.filter(calificacion_id=calificacion_id).values('id', 'nombre'))
    response = [{"success": 1, "result": especialidades}]
    return HttpResponse(json.dumps(response), content_type='application/json')


@permission_required('ges_trab.change_trabajador', login_url='home_principal')
def check_codigo(request, pk=0):
    is_available = "false"
    if check is True:
        return HttpResponse("true")
    if request.is_ajax():
        codigo_interno = request.GET.get("codigo_interno")  # Change post to get
        try:
            Alta.objects.exclude(id=pk).get(codigo_interno=codigo_interno)
        except ObjectDoesNotExist:
            is_available = "true"
    return HttpResponse(is_available)


@permission_required('ges_trab.change_trabajador', raise_exception=True)
def check_usuario(request, pk=None):
    is_available = "false"
    if check is True:
        return HttpResponse("true")
    if request.is_ajax():
        usuario = request.GET.get("usuario")  # Change post to get
        if usuario == 'Ninguno':
            return HttpResponse("true")
        try:
            Alta.objects.exclude(id=pk).get(usuario=usuario)
        except ObjectDoesNotExist:
            is_available = "true"
    return HttpResponse(is_available)


@permission_required('ges_trab.change_trabajador', raise_exception=True)
def check_ci(request, pk=None):
    is_available = "false"
    if check is True:
        return HttpResponse("true")
    if request.is_ajax():
        ci = request.GET.get("ci")  # Change post to get
        try:
            Alta.objects.exclude(id=pk).get(ci=ci)
        except ObjectDoesNotExist:
            is_available = "true"
    return HttpResponse(is_available)


@permission_required(('ges_trab.change_trabajador', 'ges_trab.change_movimiento'), raise_exception=True)
def check_plantilla(request):
    is_available = "false"
    if check is True:
        return HttpResponse("true")
    if request.is_ajax():
        org_plantilla = request.GET.get("org_plantilla")  # Change post to get
        try:
            Alta.objects.get(org_plantilla=org_plantilla)
        except ObjectDoesNotExist:
            is_available = "true"
    return HttpResponse(is_available)


###
# Web view reports
###

REPORTS = {
    # 1: 'Listado por departamentos',
    2: 'Distribución por áreas',
    3: 'Distribución por género',
    7: 'Distribución por etnia',
    4: 'Distribución por rango edades',
    5: 'Carreras por departamentos',
    6: 'Cargos por departamentos',
    8: 'Total por áreas'
}


def _listado_x_departamento(model, year=None, month=None, from_date=None, to_date=None):
    queryset = model.objects.annotate(
        unidad_nombre=F('unidad_org__nombre'),
        departamento_nombre=F('departamento__nombre'),
        especialidad_nombre=F('especialidad__nombre'),
        cargo_nombre=F('cargo__nombre')
    ).order_by('unidad_org_id', 'departamento_id')
    context = {'tipo_reporte': REPORTS, 'reporte_id': 1}
    if from_date:
        queryset = queryset.filter(fecha_contrato__range=[from_date, to_date])
        context.update({'from_date': from_date, 'to_date': to_date})
    elif year:
        queryset = queryset.filter(fecha_contrato__year=year)
        context.update({'date': date(year, 1, 1), 'year': year})
        if month:
            queryset = queryset.filter(fecha_contrato__month=month)
            context.update({'date': date(year, month, 1), 'month': month})
    else:
        current_year = date.today().year
        queryset = queryset.filter(fecha_contrato__year=current_year)
        context.update({'date': date(current_year, 1, 1), 'year': current_year})
    context['object_list'] = queryset
    return context


@permission_required('ges_trab.export_trabajador', raise_exception=True)
def altas_x_departamento(request, year=None, month=None, from_date=None, to_date=None):
    context = _listado_x_departamento(Alta, year, month, from_date, to_date)
    context['alta_baja'] = True
    return render(request, 'reports/trabajador/altas_x_departamento.html', context)


@permission_required('ges_trab.export_trabajador', raise_exception=True)
def bajas_x_departamento(request, year=None, month=None, from_date=None, to_date=None):
    context = _listado_x_departamento(BajaOther, year, month, from_date, to_date)
    context['alta_baja'] = False
    return render(request, 'reports/trabajador/bajas_x_departamento.html', context)


@permission_required('ges_trab.report_trabajador', raise_exception=True)
def dist_x_departamento(request):
    return render(request, 'reports/trabajador/layout_chart.html', {
        "tipo_reporte": REPORTS, 'reporte_id': 2, 'chart_url': 'dist-bar-drilldown'
    })


@permission_required('ges_trab.report_trabajador', raise_exception=True)
def dist_altas_x_genero(request):
    return render(request, 'reports/trabajador/layout_chart.html', {
        "tipo_reporte": REPORTS, 'reporte_id': 3, 'alta_baja': True, 'chart_url': 'gender-pie-alta'
    })


@permission_required('ges_trab.report_trabajador', raise_exception=True)
def dist_bajas_x_genero(request):
    return render(request, 'reports/trabajador/layout_chart.html', {
        "tipo_reporte": REPORTS, 'reporte_id': 3, 'alta_baja': False, 'chart_url': 'gender-pie-baja'
    })


@permission_required('ges_trab.report_trabajador', raise_exception=True)
def dist_altas_x_etnia(request):
    return render(request, 'reports/trabajador/layout_chart.html', {
        'tipo_reporte': REPORTS, 'reporte_id': 7, 'alta_baja': True, 'chart_url': 'etnia-pie-alta'
    })


@permission_required('ges_trab.report_trabajador', raise_exception=True)
def dist_bajas_x_etnia(request):
    return render(request, 'reports/trabajador/layout_chart.html', {
        'tipo_reporte': REPORTS, 'reporte_id': 7, 'alta_baja': False, 'chart_url': 'etnia-pie-baja'
    })


# todo add age average
@permission_required('ges_trab.report_trabajador', raise_exception=True)
def dist_altas_x_rango_edades(request):
    return render(request, 'reports/trabajador/dist_x_rango_edades.html', {
        "tipo_reporte": REPORTS, 'reporte_id': 4, 'alta_baja': True, 'chart_url': 'age-pyramid-alta'
    })


@permission_required('ges_trab.report_trabajador', raise_exception=True)
def dist_bajas_x_rango_edades(request):
    return render(request, 'reports/trabajador/dist_x_rango_edades.html', {
        "tipo_reporte": REPORTS, 'reporte_id': 4, 'alta_baja': False, 'chart_url': 'age-pyramid-baja'
    })


@permission_required('adm.report_especialidad', raise_exception=True)
def dist_esp_x_dep(request):
    univ = request.POST.get('univ', None)
    get_by = request.POST.get('get_by', 'dep')
    context = _request_esp_x_dep(univ, get_by)
    context.update({'tipo_reporte': REPORTS, 'reporte_id': 5, 'univ': univ, 'get_by': get_by})
    return render(request, 'reports/trabajador/dist_esp_x_dept.html', context)


@permission_required('adm.report_cargo', raise_exception=True)
def dist_cargos_x_dep(request):
    univ = request.POST.get('univ', None)
    get_by = request.POST.get('get_by', 'dep')
    context = _request_cargos_x_dep(univ, get_by)
    context.update({'tipo_reporte': REPORTS, 'reporte_id': 6, 'univ': univ, 'get_by': get_by})
    return render(request, 'reports/trabajador/dist_cargos_x_dept.html', context)


@permission_required('ges_trab.export_trabajador', raise_exception=True)
def total_x_areas(request):
    context = {}
    return render(request, 'reports/trabajador/total_x_area.html', context)


###
# Reports pdf
###
@permission_required('ges_trab.export_trabajador', raise_exception=True)
def exportar(request, pk):
    trabajador = Alta.objects.get(pk=pk)
    template_path = 'Contrato_Pdf.html'
    context = {'trabajador': trabajador, "title": "Contrato de Trabajo"}
    return generate_pisa_report(context, template_path, f"{context['title']} – {trabajador.nombre_completo}")


@permission_required('ges_trab.export_trabajador', raise_exception=True)
def exportar_acuerdo(request, pk):
    trabajador = Alta.objects.get(pk=pk)
    template_path = 'Acuerdo_Confidencialidad.html'
    context = {'trabajador': trabajador, 'title': 'Acuerdo de Confidencialidad'}
    return generate_pisa_report(context, template_path, f"{context['title']} – {trabajador.nombre_completo}")


@permission_required('ges_trab.export_trabajador', raise_exception=True)
def exportar_solic_cuenta_user(request, pk):
    trabajador = Alta.objects.get(pk=pk)
    template_path = 'Solicitud_Cuenta_Usuario.html'
    context = {'trabajador': trabajador, 'title': 'Solicitud de Cuenta de Usuario'}
    return generate_pisa_report(context, template_path, f"{context['title']} – {trabajador.nombre_completo}")


@permission_required('ges_trab.export_movimiento', raise_exception=True)
def exportar_movimiento_nomina(request, pk):
    movimiento = Movimiento.objects.get(pk=pk)
    directorrh = Alta.objects.filter(cargo_id=179).get()
    registrado_por = Alta.objects.filter(cargo_id=27, departamento_id=10).get()
    template_path = 'Movimiento_Nomina.html'
    context = {'trabajador': movimiento.trabajador, 'movimiento': movimiento,
               'elaborado': request.user, 'director': directorrh,
               'dia': movimiento.fecha.day, 'mes': movimiento.fecha.month,
               'anno': movimiento.fecha.year, 'registrado_por': registrado_por,
               'title': f'Movimiento de Nomina – {movimiento.trabajador.nombre_completo}'}
    return generate_pisa_report(context, template_path, context['title'])


@permission_required('ges_trab.export_movimiento', raise_exception=True)
def exportar_movimiento_nomina_alta(request, pk):
    trabajador = Alta.objects.get(pk=pk)
    directorrh = Alta.objects.filter(cargo_id=179).get()
    registrado_por = Alta.objects.filter(cargo_id=27, departamento_id=10).get()
    template_path = 'Movimiento_Nomina_Alta.html'
    context = {'trabajador': trabajador, 'elaborado': request.user,
               'director': directorrh, 'dia': trabajador.fecha_alta.day,
               'mes': trabajador.fecha_alta.month, 'anno': trabajador.fecha_alta.year,
               'title': f'Movimiento de Nomina – Alta {trabajador.nombre_completo}',
               'registrado_por': registrado_por}
    return generate_pisa_report(context, template_path, context['title'])


@permission_required('ges_trab.export_movimiento', raise_exception=True)
def exportar_movimiento_nomina_baja(request, pk):
    trabajador = BajaOther.objects.get(pk=pk)
    directorrh = Alta.objects.filter(cargo_id=179).get()
    registrado_por = Alta.objects.filter(cargo_id=27, departamento_id=10).get()
    template_path = 'Movimiento_Nomina_Baja.html'
    context = {'trabajador': trabajador, 'elaborado': request.user,
               'director': directorrh, 'dia': trabajador.fecha_baja.day,
               'mes': trabajador.fecha_baja.month, 'anno': trabajador.fecha_baja.year,
               'registrado_por': registrado_por,
               'title': f'Movimiento Nomina Baja – {trabajador.nombre_completo}'}
    return generate_pisa_report(context, template_path, context['title'])


@permission_required('ges_trab.export_trabajador', raise_exception=True)
def all_altas_report(request, year, month=None):
    context = _request_workers_year_month_delta(year, month=month, alta=True)
    template_path = 'reports/trabajador/export/altas_x_departamento.html'
    return generate_pisa_report(context, template_path, context['title'])


@permission_required('ges_trab.export_trabajador', raise_exception=True)
def all_bajas_report(request, year, month=None):
    context = _request_workers_year_month_delta(year, month=month)
    template_path = 'reports/trabajador/export/bajas_x_departamento.html'
    return generate_pisa_report(context, template_path, context['title'])


@permission_required('ges_trab.export_trabajador', raise_exception=True)
def exportar_altas(request):
    from_date = request.POST.get('fecha_inic', None)
    to_date = request.POST.get('fecha_fin', None)
    template_path = 'reports/trabajador/export/altas_x_departamento.html'
    context = _request_workers_date_delta(from_date, to_date, True)
    return generate_pisa_report(context, template_path, context['title'])


@permission_required('ges_trab.export_trabajador', raise_exception=True)
def exportar_bajas(request):
    from_date = request.POST.get('fecha_inic', None)
    to_date = request.POST.get('fecha_fin', None)
    template_path = 'reports/trabajador/export/bajas_x_departamento.html'
    context = _request_workers_date_delta(from_date, to_date)
    return generate_pisa_report(context, template_path, context['title'])


@permission_required('ges_trab.export_movimiento', raise_exception=True)
def exportar_movimientos(request):
    fecha_inic = request.POST['fecha_inic']
    fecha_fin = request.POST['fecha_fin']
    template_path = 'Reporte_Movimientos_Altas_Bajas.html'
    context = _request_report_movimiento(fecha_inic, fecha_fin)
    return generate_pisa_report(context, template_path, "Movimientos Altas y Bajas")


@permission_required('ges_trab.export_movimiento', raise_exception=True)
def exportar_suplemento_contrato(request, pk):
    movimiento = Movimiento.objects.get(pk=pk)
    directorrh = Trabajador.objects.filter(cargo_id=179).get()
    template_path = 'Suplemento_Contrato.html'
    context = {'trabajador': movimiento.trabajador, 'movimiento': movimiento,
               'director': directorrh, 'dia': movimiento.fecha.day,
               'mes': movimiento.fecha.month, 'anno': movimiento.fecha.year,
               'title': f'Suplemento de Contrato – {movimiento.trabajador.nombre_completo}'}
    return generate_pisa_report(context, template_path, context['title'])


TITLE_BY = {
    'emp': 'en la Empresa',
    'uni': 'por Unidad Organizacional',
    'dep': 'por Departamento'
}


@permission_required('adm.export_especialidad', raise_exception=True)
def dist_esp_x_dep_report(request):
    univ = request.POST.get('univ', None)
    get_by = request.POST.get('get_by', 'dep')
    context = _request_esp_x_dep(univ, get_by)
    context['get_by'] = get_by
    context['title'] = f'Carreras {TITLE_BY[get_by]}'
    template_name = 'reports/trabajador/export/esp_x_departamento.html'
    return generate_pisa_report(context, template_name, context['title'])


@permission_required('adm.export_cargo', raise_exception=True)
def dist_cargo_x_dep_report(request):
    univ = request.POST.get('univ', None)
    get_by = request.POST.get('get_by', 'dep')
    context = _request_cargos_x_dep(univ, get_by)
    context['get_by'] = get_by
    context['title'] = f'Cargos y Carreras {TITLE_BY[get_by]}'
    template_name = 'reports/trabajador/export/cargos_x_departamento.html'
    return generate_pisa_report(context, template_name, context['title'])


# @permission_required('ges_trab.export_trabajador', raise_exception=True)
def export_ubicacion_en_defensa(request):
    objects_list = Alta.objects.values('orga_defensa').annotate(
        count=Count('id')
    ).values('orga_defensa', 'count')
    total = Alta.objects.all().count()
    subtotal = 0
    for item in objects_list:
        subtotal += item['count']
        item['porciento'] = round(item['count'] / total * 100, 2)
    objects_list = list(objects_list)
    objects_list.append({
        'orga_defensa': 'No incorporados',
        'count': total - subtotal,
        'porciento': round((total - subtotal) / total * 100, 2)
    })
    template_name = 'reports/defensa/resumen_situacion_defensa.html'
    context = {
        'object_list': objects_list,
        'total': total,
        'title': 'Situacion en la Defensa'
    }
    return generate_pisa_report(context, template_name, context['title'])


def registro_defensa(request, org_defensa=None):
    context = _request_registro_defensa()
    context['title'] = 'Registro Militar'
    template_name = 'reports/defensa/registro_militar.html'
    return generate_pisa_report(context, template_name, context['title'])


def asignado_a_defensa(request):
    context = _request_registro_defensa()
    context['title'] = "Defensa"
    template_name = 'reports/defensa/ubicacion_en_defensa.html'
    return generate_pisa_report(context, template_name, context['title'])


def choferes_en_defensa(request):
    context = _request_registro_defensa(True)
    context['title'] = "Ubicacion en la defensa de los Choferes"
    template_name = 'reports/defensa/choferes_en_la_defensa.html'
    return generate_pisa_report(context, template_name, context['title'])


def trabajadores_x_contrato(request):
    context = _request_trabajadores_x_contrato()
    template_name = 'reports/trabajador/export/trabajadores_x_contrato.html'
    return generate_pisa_report(context, template_name, context['title'])


###
# Utility functions
###
def _request_workers_year_month_delta(year, month=None, alta=False):
    queryset = Trabajador.objects.filter(fecha_baja__isnull=alta).order_by('unidad_org', 'departamento')
    str_out = year
    if month:
        str_out = date(year, month, 1).strftime('%J, %Y')
    title = f"Reporte {'Altas' if alta else 'Bajas'} {str_out}"
    if alta:
        queryset = queryset.filter(fecha_contrato__year=year)
        if month:
            queryset = queryset.filter(fecha_contrato__month=month)
    else:
        queryset = queryset.filter(fecha_baja__year=year)
        if month:
            queryset = queryset.filter(fecha_baja__month=month)
    queryset = queryset.annotate(
        unidad_nombre=F('unidad_org__nombre'),
        departamento_nombre=F('departamento__nombre'),
        cargo_nombre=F('cargo__nombre'),
        especialidad_nombre=F('especialidad__nombre')
    )
    return {'object_list': queryset, 'title': title}


def _request_report_movimiento(fecha_inic, fecha_fin):
    sql_alta = f"""
        SELECT
            ges_trab_trabajador.id, ges_trab_trabajador.primer_nombre, ges_trab_trabajador.segundo_nombre,
            ges_trab_trabajador.apellidos, ges_trab_trabajador.codigo_interno,
            ges_trab_trabajador.categoria, ges_trab_trabajador.departamento_id
        FROM public.ges_trab_trabajador
        WHERE
            ges_trab_trabajador.fecha_contrato BETWEEN '{fecha_inic}'::DATE AND '{fecha_fin}'::DATE
        ORDER BY
            ges_trab_trabajador.fecha_contrato ASC;
    """
    result1 = Trabajador.objects.raw(sql_alta)
    trabajadores_alta = []
    for element in result1:
        trabajadores_alta.append(element)

    sql_baja = f"""
        SELECT
            ges_trab_baja.id, ges_trab_baja.primer_nombre, ges_trab_baja.segundo_nombre,
            ges_trab_baja.apellidos, ges_trab_baja.codigo_interno, ges_trab_baja.departamento_id,
            ges_trab_baja.categoria
        FROM public.ges_trab_baja
        WHERE ges_trab_baja.fecha_baja BETWEEN '{fecha_inic}'::DATE AND '{fecha_fin}'::DATE
        ORDER BY ges_trab_baja.fecha_baja ASC;
    """
    result2 = Baja.objects.raw(sql_baja)
    trabajadores_baja = []
    for element in result2:
        trabajadores_baja.append(element)

    sql_mov = f"""
        SELECT ges_trab_movimiento.id, ges_trab_trabajador.primer_nombre, ges_trab_trabajador.segundo_nombre,
            ges_trab_trabajador.apellidos, ges_trab_trabajador.codigo_interno, ges_trab_movimiento.area_ant,
            ges_trab_trabajador.categoria,ges_trab_movimiento.area_act
        FROM public.ges_trab_movimiento, public.ges_trab_trabajador
        WHERE ges_trab_trabajador.id = ges_trab_movimiento.trabajador_id AND
            ges_trab_movimiento.fecha BETWEEN '{fecha_inic}'::DATE AND '{fecha_fin}'::DATE
        ORDER BY ges_trab_movimiento.fecha ASC;
    """
    result3 = Movimiento.objects.raw(sql_mov)
    trabajadores_mov = []
    for element in result3:
        trabajadores_mov.append(element)

    return {'trabajadores_alta': trabajadores_alta, 'trabajadores_baja': trabajadores_baja,
            'trabajadores_mov': trabajadores_mov, 'fecha_inic': fecha_inic, 'fecha_fin': fecha_fin}


def _request_workers_date_delta(fecha_inic, fecha_fin, alta=False):
    queryset = Trabajador.objects.filter(
        fecha_baja__isnull=alta)
    if alta:
        queryset = queryset.filter(
            fecha_contrato__range=[fecha_inic, fecha_fin]
        )
    else:
        queryset = queryset.filter(
            fecha_baja__range=[fecha_inic, fecha_fin]
        )
    queryset = queryset.annotate(
        unidad_nombre=F('unidad_org__nombre'),
        departamento_nombre=F('departamento__nombre'),
        cargo_nombre=F('cargo__nombre'),
        especialidad_nombre=F('especialidad__nombre')).order_by('unidad_org_id', 'departamento_id')
    title = f'Reporte {"Altas" if alta else "Bajas"} ({fecha_inic} a {fecha_fin})'

    return {'object_list': queryset, 'title': title}


def _request_esp_x_dep(univ=None, get_by=None):
    queryset = Alta.objects.filter(escolaridad='Univ') if univ else Alta.objects
    queryset = queryset.exclude(Q(especialidad_id__isnull=True)).values('especialidad_id').annotate(
        count=Count('especialidad_id'),
        esp_nombre=F('especialidad__nombre')
    )
    if get_by == 'emp':
        queryset = queryset.values(
            'esp_nombre', 'especialidad_id', 'count'
        ).order_by('-count', 'esp_nombre')
    elif get_by == 'uni':
        queryset = queryset.annotate(
            uni_nombre=F('unidad_org__nombre')
        ).values(
            'esp_nombre', 'unidad_org_id', 'especialidad_id', 'count', 'uni_nombre'
        ).order_by('unidad_org_id', '-count', 'esp_nombre')
    else:
        queryset = queryset.annotate(
            uni_nombre=F('unidad_org__nombre'),
            dep_nombre=F('departamento__nombre')
        ).values(
            'esp_nombre', 'unidad_org_id', 'departamento_id',
            'especialidad_id', 'count', 'uni_nombre', 'dep_nombre'
        ).order_by('unidad_org_id', 'departamento_id', '-count', 'esp_nombre')
    return {'object_list': queryset}


def _request_cargos_x_dep(univ=None, get_by=None):
    queryset = Alta.objects.filter(escolaridad='Univ') if univ else Alta.objects
    queryset = queryset.exclude(Q(especialidad_id__isnull=True)).values('cargo_id').annotate(
        cargo_nombre=F('cargo__nombre'),
        count=Count('cargo_id'),
        esp_nombre=F('especialidad__nombre')
    )
    if get_by == 'uni':
        queryset = queryset.annotate(
            uni_nombre=F('unidad_org__nombre')).values(
            'esp_nombre', 'unidad_org_id', 'cargo_nombre',
            'cargo_id', 'count', 'uni_nombre').order_by('unidad_org_id', '-count')
    elif get_by == 'emp':
        queryset = queryset.values(
            'esp_nombre', 'cargo_nombre',
            'cargo_id', 'count').order_by('-count')
    else:
        queryset = queryset.annotate(
            uni_nombre=F('unidad_org__nombre'),
            dep_nombre=F('departamento__nombre')).values(
            'esp_nombre', 'unidad_org_id', 'departamento_id', 'cargo_nombre',
            'cargo_id', 'count', 'uni_nombre', 'dep_nombre').order_by('unidad_org_id', 'departamento_id', '-count')
    return {'object_list': queryset}


def _request_registro_defensa(org_defensa=None):
    queryset = Alta.objects.exclude(orga_defensa__in=['FEI', 'Imp']).annotate(
        dep_nombre=F('departamento__nombre'),
        cargo_nombre=F('cargo__nombre')
    )
    if org_defensa:
        queryset = queryset.filter(cargo__nombre__startswith='Chofer').order_by('primer_nombre', 'segundo_nombre', 'apellidos')
    else:
        queryset = queryset.order_by('orga_defensa', 'primer_nombre', 'segundo_nombre', 'apellidos')
        queryset = sorted(queryset, key=lambda n: (
            0 if n.orga_defensa == 'U/R' else 1 if n.orga_defensa == 'MTT' else 2 if n.orga_defensa == 'BPD-LR ' else 3))
    return {"object_list": queryset, 'rename': {
        'U/R': 'Unidades Regulares',
        'BPD-LR': 'Brigada de Producción y Defensa en Lugar de Residencia',
        'BPD-PTG': 'Brigada de Producción y Defensa para Tiempo de Guerra',
        'MTT': 'Milicias de Tropas Territoriales'
    }}


def _request_trabajadores_x_contrato():
    queryset = Alta.objects.all().annotate(
        uni_nombre=F('unidad_org__nombre'),
        dep_nombre=F('departamento__nombre'),
        cargo_nombre=F('cargo__nombre')
    ).order_by('t_contrato')
    queryset = sorted(
        queryset,
        key=lambda n: (3 if n.t_contrato == '1' or n.t_contrato == '2' else 2 if n.t_contrato == '3' or n.t_contrato == '7' else 1 if n.t_contrato == '4' else 0)
    )
    return {
        'object_list': queryset,
        'title': 'Trabajadores por Contrato, &aacute;reas, Categor&iacute;a Ocupacional',
        'rename': {
            '1': 'Indeterminado',
            '2': 'Indeterminado',
            '3': 'Determinados',
            '7': 'Determinados',
            '6': 'A Prueba',
            '4': 'Adiestramiento'
        }
    }
