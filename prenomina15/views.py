from django.core.exceptions import FieldError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .form import *
from .models import Obra, Plano, Objeto, SalarioMax, Esp, Persona, Plan, Corte, Especial, Especialidad, Area, Trab, \
    Catalogo, Penalizaciones, Cortes_Penalizaciones, Cat, Obr, Etapas, Objetos
import json
from entrada_datos.models import Actividad
from decimal import Decimal, ROUND_HALF_UP
from .filters import PlanoFilter
from django.db import DatabaseError
from django.db.models import Subquery, F, Q
import os
from rechum import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
import datetime
from ges_trab.models import Trabajador
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import _user_has_module_perms
from rechum.my_decorators import context_add_perm, context_add_perm_menu_pren15
from itertools import chain
from django.core.cache import cache
from django.views.decorators.cache import cache_page


# Listar.


def home_pren15(request):
    # Verificando si tiene permiso para el modulo de Prenomina15
    permiso_app_adm = _user_has_module_perms(request.user, 'prenomina15')
    if permiso_app_adm:
        obras = listar_obra(request)
        context = {'request': request, 'obras': obras}
        context = context_add_perm(request, context, 'prenomina15')
        return render(request, 'home_pren15.html', context)
    else:
        return redirect('home_principal')


# ****************************************GESTIONAR*****************************************


@permission_required('prenomina15.read_obra', 'home_principal')
def gestionar_obra(request):
    obras = listar_obra(request)
    user_id = User.objects.get(username=request.user)
    list_obras = Obra.objects.all().select_related("orden_trab").select_related("gesc").filter(usuarios=request.user.id, activa=True)
    form = ObraForm(request.POST or None)
    context = {'list_obras': list_obras, 'form': form, 'obras': obras}
    context = context_add_perm(request, context, 'prenomina15', 'obra')
    return render(request, 'Gestionar_Obra.html', context)


@permission_required('prenomina15.read_obra', 'home_principal')
def gestionar_penalizacion(request, trab=None, corte=None, obra=None):
    obras = listar_obra(request)
    obra_id = obra
    if 'obra' in request.POST:
        obra_id = request.POST['obra']
    obra_nombre = Obra.objects.get(id=obra_id).nombre
    cortes = listar_cortes_pen_obra(request, obra_id)
    planos = Plano.objects.exclude(valor_pen=0.00).filter(obra_id=obra_id).order_by('trabajador')
    form = PenalizacionForm(request.POST or None)
    form.fields['trabajador'].queryset = Trabajador.objects.filter(
        id__in=Subquery(Plano.objects.filter(obra_id=obra_id).values('trabajador_id')))
    if trab and corte:
        form.fields['trabajador'].queryset = Trabajador.objects.filter(id=trab)
        planos = Plano.objects.exclude(valor_pen=0.00).filter(obra_id=obra_id, trabajador_id=trab, corte=corte)
        trab_nom = ''
        inc_p = 0
        inc_cpl = 0
        inc_cal = 0
        for pl in planos:
            inc_p = pl.incumplimiento_plano
            inc_cpl = pl.incumplimiento_cpl
            inc_cal = pl.incumplimiento_calidad
            trab_nom = pl.trabajador
            break
        form.fields['incumplimiento_plano'].initial = inc_p
        form.fields['incumplimiento_cpl'].initial = inc_cpl
        form.fields['incumplimiento_calidad'].initial = inc_cal
        context = {'planos': planos, 'form': form, 'obras': obras, 'obra': obra_id, 'cortes': cortes, 'corte': corte,
                   'trabajador': trab, 'nombre_trab': trab_nom}
    else:
        penalizaciones = listar_trabaj_pen_obra(request, planos)
        context = {'penalizaciones': penalizaciones, 'form': form, 'obras': obras, 'obra': obra_id, 'cortes': cortes,
                   'obra_nombre': obra_nombre}
        context = context_add_perm(request, context, 'prenomina15', 'obra')
        return render(request, 'Gestionar_Penalizacion.html', context)

    context = context_add_perm(request, context, 'prenomina15', 'obra')
    return render(request, 'Detalle_Penalizacion.html', context)


@permission_required('prenomina15.read_obra', 'home_principal')
def deleted_penalizaciones(request, trab=None, corte=None, obra=None):
    obras = listar_obra(request)
    obra_id = obra
    if 'obra' in request.POST:
        obra_id = request.POST['obra']
    cortes = listar_cortes_pen_obra(request, obra_id)
    form = PenalizacionForm(request.POST or None)
    form.fields['trabajador'].queryset = Trabajador.objects.filter(
        id__in=Subquery(Plano.objects.filter(obra_id=obra_id).values('trabajador_id')))
    planos = Plano.objects.exclude(valor_pen=0.00).filter(obra_id=obra_id, trabajador_id=trab, corte=corte)
    inc_p = 0
    inc_cpl = 0
    inc_cal = 0
    penalizar(request, planos, inc_p, inc_cpl, inc_cal)
    obra_nombre = Obra.objects.get(id=obra_id).nombre
    planos = Plano.objects.exclude(valor_pen=0.00).filter(obra_id=obra_id).order_by('trabajador')
    form.fields['trabajador'].queryset = Trabajador.objects.filter(
        id__in=Subquery(Plano.objects.filter(obra_id=obra_id).values('trabajador_id')))
    penalizaciones = listar_trabaj_pen_obra(request, planos)
    context = {'penalizaciones': penalizaciones, 'form': form, 'obras': obras, 'obra': obra_id, 'cortes': cortes,
               'obra_nombre': obra_nombre}
    context = context_add_perm(request, context, 'prenomina15', 'obra')
    return render(request, 'Gestionar_Penalizacion.html', context)


# self.fields['obra'].queryset = Obra.objects.filter(id=obra_id)
@permission_required('prenomina15.read_objeto', 'home_principal')
def gestionar_objeto(request, obra=None):
    obras = listar_obra(request)
    if 'obra' in request.POST:
        obra = request.POST['obra']
    obra_id = obra
    list_obj = Objeto.objects.all().select_related("obra").filter(obra__usuarios=request.user.id,
                                                                  obra_id=obra_id).order_by('codigo')
    form = ObjetoForm(request.POST or None)
    form.fields['obra'].queryset = Obra.objects.filter(id=obra_id)
    context = {'list_obj': list_obj, 'form': form, 'obras': obras}
    context = context_add_perm(request, context, 'prenomina15', 'objeto')
    return render(request, 'Gestionar_Objeto.html', context)


@permission_required('prenomina15.read_plano', 'home_principal')
def gestionar_plano(request):
    obras = listar_obra(request)
    obra_id = request.POST['obra']
    obra = Obra.objects.get(id=obra_id)
    form = PlanoForm(request.POST or None)
    form.fields['obra'].queryset = Obra.objects.filter(id=obra_id)
    form.fields['objeto'].queryset = Objeto.objects.filter(obra=obra.id).order_by('codigo')
    form.fields['actividad'].queryset = Actividad.objects.filter(orden_trab_id=obra.orden_trab_id).order_by(
        'codigo_act')
    list_planos = Plano.objects.all().select_related("actividad").select_related("objeto").select_related(
        "formato").select_related("obra").select_related("especialidad").select_related("trabajador").filter(
        obra__usuarios=request.user.id, obra_id=obra.id).order_by('fecha_ini')
    plano_filter = PlanoFilter(request.POST, queryset=list_planos)
    formrev = RevisionForm(request.POST or None)
    context = {'form': form, 'formrev': formrev, 'plano_filter': plano_filter, 'obras': obras, 'obraS': obra.nombre}
    context = context_add_perm(request, context, 'prenomina15', 'plano')
    return render(request, 'Gestionar_Plano.html', context)


@permission_required('prenomina15.read_revision', 'home_principal')
def listado_revisiones(request, pk):
    obras = listar_obra(request)
    list_rev = Revision.objects.filter(plano_id=pk)
    nombre = Plano.objects.get(id=pk).nombre
    objeto = Plano.objects.get(id=pk).objeto.codigo
    num = Plano.objects.get(id=pk).num
    rev_pago = Plano.objects.get(id=pk).rev_pago

    context = {'list_rev': list_rev,
               'obras': obras,
               'nombre': nombre,
               'objeto': objeto,
               'num': num,
               'pk': pk,
               'rev_pago': rev_pago}
    context = context_add_perm(request, context, 'prenomina15', 'revision')
    return render(request, 'Listado_Revisiones.html', context)


# ****************************************ADICIONAR*****************************************

@permission_required('prenomina15.add_obra', 'home_principal')
def adicionar_obra(request):
    obras = listar_obra(request)
    user_id = User.objects.get(username=request.user)
    form = ObraForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            obra = Obra(
                orden_trab=form.cleaned_data['orden_trab'],
                nombre=form.cleaned_data['nombre'],
                tipo=form.cleaned_data['tipo'],
                horas_a2=form.cleaned_data['horas_a2'],
                gesc=form.cleaned_data['gesc'],
                owner=request.user,
            )
            obra.save()
            obra.usuarios.add(request.user.id)
            return redirect('adicionarObra')
    context = { 'form': form, 'obras': obras}
    context = context_add_perm(request, context, 'prenomina15', 'obra')
    return render(request, 'Gestionar_Obra.html', context)


def add_penalizaciones(request, obra=None):
    obras = listar_obra(request)
    obra_id = obra
    if 'obra' in request.POST:
        obra_id = request.POST['obra']
    cortes = listar_cortes_pen_obra(request, obra_id)
    form = PenalizacionForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            pk_trab = form.cleaned_data['trabajador']
            corte = request.POST['corte']
            pen_plano = form.cleaned_data['incumplimiento_plano']
            pen_cpl = form.cleaned_data['incumplimiento_cpl']
            pen_calidad = form.cleaned_data['incumplimiento_calidad']
            planos = Plano.objects.all().filter(trabajador=pk_trab, corte=corte)
            penalizar(request, planos, pen_plano, pen_cpl, pen_calidad)
    obra_nombre = Obra.objects.get(id=obra_id).nombre
    planos = Plano.objects.exclude(valor_pen=0.00).filter(obra_id=obra_id).order_by('trabajador')
    form.fields['trabajador'].queryset = Trabajador.objects.filter(
        id__in=Subquery(Plano.objects.filter(obra_id=obra_id).values('trabajador_id')))
    penalizaciones = listar_trabaj_pen_obra(request, planos)
    context = {'penalizaciones': penalizaciones, 'form': form, 'obras': obras, 'obra': obra_id, 'cortes': cortes,
               'obra_nombre': obra_nombre}
    context = context_add_perm(request, context, 'prenomina15', 'obra')
    return render(request, 'Gestionar_Penalizacion.html', context)


@permission_required('prenomina15.add_plano', 'home_principal')
def adicionar_plano(request):
    obras = listar_obra(request)
    obra_id = request.POST['obra']
    obra = Obra.objects.get(id=obra_id)
    form = PlanoForm(request.POST or None)
    form.fields['obra'].queryset = Obra.objects.filter(id=obra_id)
    form.fields['objeto'].queryset = Objeto.objects.filter(obra=obra.id).order_by('codigo')
    form.fields['actividad'].queryset = Actividad.objects.filter(orden_trab_id=obra.orden_trab_id).order_by(
        'codigo_act')

    formrev = RevisionForm(None)
    if form.is_valid():
        if Plano.objects.filter(obra=form.cleaned_data['obra'], objeto=form.cleaned_data['objeto'],
                                num=form.cleaned_data['num'], actividad=form.cleaned_data['actividad']).count():
            cal = Plano.objects.all().select_related("actividad").select_related("objeto").select_related(
                "formato").select_related("obra").select_related("especialidad").select_related("trabajador").filter(
                obra__usuarios=request.user.id, obra_id=obra_id)
            plano_filter = PlanoFilter(request.POST, queryset=cal)
            context = {'plano_filter': plano_filter, 'form': form, 'formrev': formrev,
                       'errores': 'Ya existe un plano con ese número para el objeto en esa obra.', 'obras': obras}
            context = context_add_perm(request, context, 'prenomina15', 'plano')
            return render(request, 'Gestionar_Plano.html', context)
        else:
            cat = 0
            horas_creadas_real = 0
            horas_doc = 0
            valor_plano = 0
            valor_retenido = 0
            valor_total = 0
            obra = form.cleaned_data['obra']
            esp_factor = form.cleaned_data['especialidad'].factor
            for_factor = form.cleaned_data['formato'].factor
            sal_trab = SalarioMax.objects.filter(tipo=obra.tipo,
                                                 grupo_esc=form.cleaned_data['trabajador'].escala_salarial).get()
            sal_obra = SalarioMax.objects.filter(tipo=obra.tipo, grupo_esc=obra.gesc).get()
            coe = sal_obra.sal / sal_trab.sal
            cant =  1
            horas = (obra.horas_a2 * coe).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            horas_esp = (horas * esp_factor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            horas_creadas = ((horas_esp * for_factor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) * Decimal(
                form.cleaned_data['porciento'])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            etapa = form.cleaned_data['etapa']
            tipo_doc = form.cleaned_data['tipo_doc']
            if tipo_doc == 'MD':
                horas_creadas = form.cleaned_data['especialidad'].md
            if tipo_doc == 'LC':
                horas_creadas = form.cleaned_data['especialidad'].lc
            if tipo_doc == 'PR':
                horas_creadas = form.cleaned_data['especialidad'].pr
            tarifa = Decimal(sal_trab.sal / Decimal(190.6)).quantize(Decimal('.000001'))
            valor_real = ((horas_creadas.quantize(Decimal('.01')) * tarifa).quantize(Decimal('.01'))).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP)
            # if tipo_doc == 'PL':
            #     valor_real = (horas_creadas.quantize(Decimal('.01')) * tarifa).quantize(Decimal('.01'))
            valor_retenido_real = ((horas_creadas.quantize(Decimal('.01')) * tarifa) * Decimal(0.2)).quantize(
                Decimal('.01'))
            valor_total_real = valor_real - valor_retenido_real
            if cant == 1:
                horas_creadas_real = horas_creadas
                valor_plano = valor_real
                valor_retenido = valor_retenido_real
                valor_total = valor_total_real
            else:
                cat = 1
            plano = Plano(
                num=form.cleaned_data['num'],
                objeto=form.cleaned_data['objeto'],
                nombre=form.cleaned_data['nombre'],
                formato=form.cleaned_data['formato'],
                obra=form.cleaned_data['obra'],
                cant=cant,
                corte=form.cleaned_data['corte'],
                especialidad=form.cleaned_data['especialidad'],
                trabajador=form.cleaned_data['trabajador'],
                fecha_fin=form.cleaned_data['fecha_fin'],
                fecha_ini=form.cleaned_data['fecha_ini'],
                actividad=form.cleaned_data['actividad'],
                porciento=form.cleaned_data['porciento'],
                horas_creadas=horas_creadas_real,
                tarifa=tarifa,
                valor=Decimal(valor_plano),
                valor_retenido=valor_retenido,
                valor_total=valor_total,
                estado='V',
                horas_creadas_real=horas_creadas,
                valor_real=valor_real,
                valor_retenido_real=valor_retenido_real,
                valor_total_real=valor_total_real,
                tipo_doc=tipo_doc,
                etapa=etapa
            )
            plano.save()
            if cat == 1:
                add_cat(request, plano.pk, plano.formato, plano.cant, plano.porciento)
    if request.method == 'POST':
        obras = listar_obra(request)
        cal = Plano.objects.all().select_related("actividad").select_related("objeto").select_related(
            "formato").select_related("obra").select_related("especialidad").select_related("trabajador").filter(
            obra__usuarios=request.user.id, obra_id=obra_id)
        plano_filter = PlanoFilter(request.POST, queryset=cal)
        context = {'plano_filter': plano_filter, 'form': form, 'obras': obras, 'formrev': formrev}
        context = context_add_perm(request, context, 'prenomina15', 'plano')
        return render(request, 'Gestionar_Plano.html', context)


@permission_required('prenomina15.add_objeto', 'home_principal')
def adicionar_objeto(request):
    obras = listar_obra(request)
    obra_id = request.POST['obra']
    form = ObjetoForm(request.POST or None)
    form.fields['obra'].queryset = Obra.objects.filter(id=obra_id)
    obra = Obra.objects.get(id=obra_id)
    list_obj = Objeto.objects.all().select_related("obra").filter(obra__usuarios=request.user.id,
                                                                  obra_id=obra_id).order_by('codigo')
    if request.method == 'POST':
        if form.is_valid():
            obj = Objeto(
                obra=form.cleaned_data['obra'],
                codigo=form.cleaned_data['codigo'],
                nombre=form.cleaned_data['nombre'])
            if Objeto.objects.filter(obra=obj.obra, codigo=obj.codigo).count():
                context = {'list_obj': list_obj, 'form': form, 'object': obj,
                           'errores': 'La obra: ( ' + obra.nombre + ' ) ya tiene un objeto con el código: ( ' + obj.codigo + ' ). Por Favor escoga otro código ',
                           'obras': obras}
                context = context_add_perm(request, context, 'prenomina15', 'objeto')
                return render(request, 'Gestionar_Objeto.html', context)
            else:
                try:
                    obj.save()
                except FieldError:
                    context = {'list_obj': list_obj, 'form': form, 'object': obj,
                               'errores': 'Intentelo de nuevo. Ha ocurrido un error de Base de Datos.', 'obras': obras}
                    context = context_add_perm(request, context, 'prenomina15', 'objeto')
                    return render(request, 'Gestionar_Objeto.html', context)
                except DatabaseError:
                    context = {'list_obj': list_obj, 'form': form, 'object': obj,
                               'errores': 'Intentelo de nuevo. Ha ocurrido un error de Base de Datos.', 'obras': obras}
                    context = context_add_perm(request, context, 'prenomina15', 'objeto')
                    return render(request, 'Gestionar_Objeto.html', context)

    context = {'list_obj': list_obj, 'form': form, 'obras': obras,
               'success': '!!! El objeto: (' + obra.nombre + '/' + obj.codigo + '/' + obj.nombre + ' ) ha sido creado satisfactoriamente !!!'}
    context = context_add_perm(request, context, 'prenomina15', 'objeto')
    return render(request, 'Gestionar_Objeto.html', context)


@permission_required('prenomina15.add_revision', 'home_principal')
def registrar_revision(request):
    user_id = User.objects.get(username=request.user).id
    obras = listar_obra(request)
    formrev = RevisionForm(request.POST or None)
    form = PlanoForm(None)
    plano = Plano.objects.get(id=request.POST['plano'])
    objeto = plano.objeto.codigo
    num = plano.num
    if plano.last_rev is not None:
        no_rev = plano.last_rev + 1
    else:
        no_rev = 0

    if request.method == 'POST':
        if formrev.is_valid():
            if 'Acta' in formrev.cleaned_data['entregado']:
                acta = formrev.cleaned_data['entregado']
            else:
                acta = 'Acta ' + formrev.cleaned_data['entregado']
            revision = Revision(
                plano=plano,
                no_rev=no_rev,
                fecha_revision=formrev.cleaned_data['fecha_revision'],
                entregado=acta,
                observaciones=formrev.cleaned_data['observaciones'],
                fecha_estado=formrev.cleaned_data['fecha_estado'],
                fecha_vpc=formrev.cleaned_data['fecha_vpc'],
                estado=formrev.cleaned_data['estado']
            )
            # if revision.no_rev == 0:
            #    plano.fecha_pago = revision.fecha_revision

            fecha_pago = request.POST.get("fecha_pago", None)
            if fecha_pago:
                fecha = fecha_pago.split("/")
                plano.fecha_pago = fecha[2]+'-'+fecha[1]+'-'+fecha[0]

            plano.estado = revision.estado
            plano.last_rev = revision.no_rev
            if revision.observaciones is not None:
                plano.orden_servicio = revision.observaciones
            if revision.estado == 'VPC':
                if plano.vpc == 'No':
                    orden = revision.observaciones.split(" ")
                    pos = orden.index('OS')
                    plano.os_vpc = orden[pos] + ' ' + orden[pos + 1]
                    plano.vpc = 'Si'
                    plano.fecha_vpc = revision.fecha_vpc
                    plano.rev_vpc = revision.no_rev
            try:
                revision.save()
            except FieldError:
                cal = Plano.objects.all().select_related("actividad").select_related("objeto").select_related(
                    "formato").select_related("obra").select_related("especialidad").select_related(
                    "trabajador").filter(obra__usuarios=user_id)
                plano_filter = PlanoFilter(request.GET, queryset=cal)

                context = {'plano_filter': plano_filter, 'formrev': formrev, 'form': form, 'obras': obras,
                           'errores': 'Intentelo de nuevo. Ha Ocurrido un error de Base de Datos', 'objeto': objeto,
                           'num': num, 'pk': plano.id, 'fecha_pago': fecha_pago}
                context = context_add_perm(request, context, 'prenomina15', 'plano')
                return render(request, 'Gestionar_Plano.html', context)
            except DatabaseError:
                cal = Plano.objects.all().select_related("actividad").select_related("objeto").select_related(
                    "formato").select_related("obra").select_related("especialidad").select_related(
                    "trabajador").filter(obra__usuarios=user_id)
                plano_filter = PlanoFilter(request.GET, queryset=cal)
                context = {'plano_filter': plano_filter, 'formrev': formrev, 'form': form, 'obras': obras,
                           'errores': 'Intentelo de nuevo. Ha ocurrido un error de Base de Datos', 'objeto': objeto,
                           'num': num, 'pk': plano.id, 'fecha_pago':fecha_pago}
                context = context_add_perm(request, context, 'prenomina15', 'plano')
                return render(request, 'Gestionar_Plano.html', context)
            plano.save()
            list_rev = Revision.objects.filter(plano_id=plano.id)
            nombre = plano.nombre
            context = {'list_rev': list_rev, 'formrev': formrev, 'obras': obras, 'nombre': nombre, 'objeto': objeto,
                       'num': num, 'pk': plano.id}
            context = context_add_perm(request, context, 'prenomina15', 'revision')
            return render(request, 'Listado_Revisiones.html', context)
    cal = Plano.objects.all().select_related("actividad").select_related("objeto").select_related(
        "formato").select_related("obra").select_related("especialidad").select_related("trabajador").filter(
        obra__usuarios=user_id)
    plano_filter = PlanoFilter(request.GET, queryset=cal)
    context = {'plano_filter': plano_filter, 'formrev': formrev, 'form': form, 'obras': obras, 'objeto': objeto,
               'num': num, 'pk': plano.id, 'fecha_pago': plano.fecha_pago}
    context = context_add_perm(request, context, 'prenomina15', 'plano')
    return render(request, 'Gestionar_Plano.html', context)


@permission_required('prenomina15.change_obra', 'home_principal')
def editar_obra(request, pk):
    user_id = User.objects.get(username=request.user)
    obras = listar_obra(request)
    obra = Obra.objects.get(id=pk)
    form = ObraForm(request.POST or None, instance=obra)
    if form.is_valid():
        form.save()
        return redirect('/pren/obras/')
    cal = Obra.objects.all().select_related("orden_trab").select_related("gesc").filter(owner=user_id)
    context = {'list_obras': cal, 'form': form, 'edit': pk, 'obras': obras}
    context = context_add_perm(request, context, 'prenomina15', 'obra')
    return render(request, 'Gestionar_Obra.html', context)


def edit_penalizaciones(request, pk):
    obras = listar_obra(request)
    penalizacion = Plano.objects.get(id=pk)
    form = PenalizacionForm(request.POST or None, instance=penalizacion)
    form.fields['trabajador'].queryset = Trabajador.objects.filter(unidad_org_id=2).order_by('departamento')
    cal = Plano.objects.exclude(valor_pen=0.00)
    context = {'planos': cal, 'form': form, 'obras': obras, 'edit': pk}
    if request.method == 'POST':
        if form.is_valid():
            pk_trab = form.cleaned_data['trabajador']
            corte = request.POST['corte']
            pen_plano = form.cleaned_data['incumplimiento_plano']
            pen_cpl = form.cleaned_data['incumplimiento_cpl']
            pen_calidad = form.cleaned_data['incumplimiento_calidad']
            planos = Plano.objects.all().filter(trabajador=pk_trab, corte=corte)
            penalizar(request, planos, pen_plano, pen_cpl, pen_calidad)
            cal = Plano.objects.exclude(valor_pen=0.00)
            context = {'planos': cal, 'form': form, 'obras': obras}

    context = context_add_perm(request, context, 'prenomina15', 'obra')
    return render(request, 'Gestionar_Penalizacion.html', context)


@permission_required('prenomina15.change_objeto', 'home_principal')
def editar_objeto(request, pk):
    obras = listar_obra(request)
    obj = Objeto.objects.get(id=pk)
    codigo = obj.codigo
    obra = obj.obra
    nombre = obj.nombre
    form = ObjetoForm(request.POST or None, instance=obj)
    form.fields['obra'].queryset = Obra.objects.filter(id=obra.id)
    cal = Objeto.objects.all().select_related("obra").filter(obra__usuarios=request.user.id, obra_id=obra.id).order_by(
        'codigo')
    context = {'list_obj': cal, 'form': form, 'obras': obras, 'edit': pk}
    if form.is_valid():
        if form.cleaned_data['obra'] != obra or codigo != form.cleaned_data['codigo']:
            if Objeto.objects.filter(obra=obj.obra, codigo=obj.codigo).count():
                cal = Objeto.objects.all().select_related("obra").filter(obra__usuarios=request.user.id,
                                                                         obra_id=obra.id).order_by('codigo')
                context = {'list_obj': cal, 'form': form, 'object': obj, 'obras': obras,
                           'errores': 'La Obra seleccionada ya tiene un objeto con ese código.'}

            else:
                obj.save()
                cal = Objeto.objects.all().select_related("obra").filter(obra__usuarios=request.user.id,
                                                                         obra_id=obra.id).order_by('codigo')
                context = {'list_obj': cal, 'form': form, 'obras': obras,
                           'success': '!!! El objeto: (' + obra.nombre + '/' + obj.codigo + '/' + obj.nombre + ' ) ha sido modificado satisfactoriamente !!!'}

        else:
            if nombre != form.cleaned_data['nombre']:
                obj.save()
                cal = Objeto.objects.all().select_related("obra").filter(obra__usuarios=request.user.id,
                                                                         obra_id=obra.id).order_by('codigo')
                context = {'list_obj': cal, 'form': form, 'obras': obras,
                           'success': '!!! El objeto: (' + obra.nombre + '/' + obj.codigo + '/' + obj.nombre + ' ) ha sido modificado satisfactoriamente !!!'}

            else:
                cal = Objeto.objects.all().select_related("obra").filter(obra__usuarios=request.user.id,
                                                                         obra_id=obra.id).order_by('codigo')
                context = {'list_obj': cal, 'form': form, 'obras': obras,
                           'warning': '!!! El objeto: (' + obra.nombre + '/' + obj.codigo + '/' + obj.nombre + ' ) no ha sufrido modificaciones !!!'}

    context = context_add_perm(request, context, 'prenomina15', 'objeto')
    return render(request, 'Gestionar_Objeto.html', context)


@permission_required('prenomina15.change_plano', 'home_principal')
def editar_plano(request, pk):
    user_id = User.objects.get(username=request.user).id
    plano = Plano.objects.get(id=pk)
    obras = listar_obra(request)
    obra = Obra.objects.get(id=plano.obra_id)
    form = PlanoForm(request.POST or None, instance=plano)
    form.fields['obra'].queryset = Obra.objects.filter(id=obra.id)
    form.fields['objeto'].queryset = Objeto.objects.filter(obra=obra.id).order_by('codigo')
    form.fields['actividad'].queryset = Actividad.objects.filter(orden_trab_id=obra.orden_trab_id).order_by(
        'codigo_act')
    formrev = RevisionForm(None)
    numero = plano.num
    objeto = plano.objeto_id
    act = plano.actividad_id
    obra = plano.obra_id
    horas_creadas_real = 0
    valor_plano = 0
    valor_retenido = 0
    valor_total = 0
    cal = Plano.objects.all().select_related("actividad").select_related("objeto").select_related(
        "formato").select_related("obra").select_related("especialidad").select_related("trabajador").filter(
        obra__usuarios=request.user.id, obra_id=plano.obra_id)
    plano_filter = PlanoFilter(request.POST, queryset=cal)
    context = {'plano_filter': plano_filter, 'form': form, 'edit': pk, 'formrev': formrev, 'obras': obras}

    if form.is_valid():
        for_numero = form.cleaned_data['num']
        for_objeto = form.cleaned_data['objeto'].id
        for_act = form.cleaned_data['actividad'].id
        for_obra = form.cleaned_data['obra'].id

        if (numero != for_numero) or (objeto != for_objeto) or (act != for_act) or (obra != for_obra):
            if Plano.objects.filter(num=for_numero, objeto=for_objeto, actividad=for_act, obra=for_obra).count():
                cal = Plano.objects.all().select_related("actividad").select_related("objeto").select_related(
                    "formato").select_related("obra").select_related("especialidad").select_related(
                    "trabajador").filter(obra__usuarios=request.user.id, obra_id=plano.obra_id)
                plano_filter = PlanoFilter(request.POST, queryset=cal)
                context = {'plano_filter': plano_filter, 'form': form, 'object': plano, 'formrev': formrev,
                           'obras': obras, 'errores': 'Ya existe un plano con ese número para el objeto seleccionado'}

            else:
                obra = form.cleaned_data['obra']
                esp_factor = form.cleaned_data['especialidad'].factor
                for_factor = form.cleaned_data['formato'].factor
                sal_trab = SalarioMax.objects.filter(tipo=obra.tipo,
                                                     grupo_esc=form.cleaned_data['trabajador'].escala_salarial).get()
                sal_obra = SalarioMax.objects.filter(tipo=obra.tipo, grupo_esc=obra.gesc).get()
                coe = sal_obra.sal / sal_trab.sal
                horas = (obra.horas_a2 * coe).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                horas_esp = (horas * esp_factor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                horas_creadas = ((horas_esp * for_factor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) * Decimal(
                    form.cleaned_data['porciento'])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                tipo_doc = form.cleaned_data['tipo_doc']
                if tipo_doc == 'MD':
                    horas_creadas = form.cleaned_data['especialidad'].md
                if tipo_doc == 'LC':
                    horas_creadas = form.cleaned_data['especialidad'].lc
                if tipo_doc == 'PR':
                    horas_creadas = form.cleaned_data['especialidad'].pr

                tarifa = Decimal(sal_trab.sal / Decimal(190.6)).quantize(Decimal('.000001'))
                if tipo_doc == 'PL':
                    valor_real = (horas_creadas.quantize(Decimal('.01')) * tarifa).quantize(Decimal('.01'))
                else:
                    valor_real = ((horas_creadas.quantize(Decimal('.01')) * tarifa).quantize(Decimal('.01'))).quantize(
                        Decimal('0.01'), rounding=ROUND_HALF_UP)

                valor_retenido_real = ((horas_creadas.quantize(Decimal('.01')) * tarifa) * Decimal(0.2)).quantize(
                    Decimal('.01'))
                valor_total_real = valor_real - valor_retenido_real
                horas_creadas_real = horas_creadas
                valor_plano = valor_real
                valor_retenido = valor_retenido_real
                valor_total = valor_total_real
                plano.nombre = form.cleaned_data['nombre']
                plano.formato = form.cleaned_data['formato']
                plano.corte = form.cleaned_data['corte']
                plano.especialidad = form.cleaned_data['especialidad']
                plano.trabajador = form.cleaned_data['trabajador']
                plano.fecha_fin = form.cleaned_data['fecha_fin']
                plano.fecha_ini = form.cleaned_data['fecha_ini']
                plano.horas_creadas = horas_creadas_real
                plano.tarifa = tarifa
                plano.valor = Decimal(valor_plano)
                plano.valor_retenido = valor_retenido
                plano.valor_total = valor_total
                plano.horas_creadas_real = horas_creadas
                plano.valor_real = valor_real
                plano.valor_retenido_real = valor_retenido_real
                plano.valor_total_real = valor_total_real
                if plano.valor_pen:
                    plano.valor_pen = plano.valor

                    plano.incumplimiento_plano_valor = plano.valor_pen * Decimal(
                        plano.incumplimiento_plano / Decimal(100.00)). \
                        quantize(Decimal('1.00'))
                    plano.valor_pen = plano.valor_pen - plano.incumplimiento_plano_valor

                    plano.incumplimiento_cpl_valor = plano.valor_pen * Decimal(
                        plano.incumplimiento_cpl / Decimal(100.00)). \
                        quantize(Decimal('1.00'))
                    plano.valor_pen = plano.valor_pen - plano.incumplimiento_cpl_valor

                    plano.incumplimiento_calidad_valor = plano.valor_pen * Decimal(
                        plano.incumplimiento_calidad / Decimal(100.00)). \
                        quantize(Decimal('1.00'))
                    plano.valor_pen = plano.valor_pen - plano.incumplimiento_calidad_valor

                    plano.valor_retenido = plano.valor_pen * Decimal(0.2)
                plano.etapa=form.cleaned_data['etapa']
                plano.save()
                cal = Plano.objects.all().select_related("actividad").select_related("objeto").select_related(
                    "formato").select_related("obra").select_related("especialidad").select_related(
                    "trabajador").filter(
                    obra__usuarios=request.user.id, obra_id=plano.obra_id)
                plano_filter = PlanoFilter(request.POST, queryset=cal)
                context = {'plano_filter': plano_filter, 'form': form, 'formrev': formrev, 'obras': obras}

        else:
            obra = form.cleaned_data['obra']
            esp_factor = form.cleaned_data['especialidad'].factor
            for_factor = form.cleaned_data['formato'].factor
            sal_trab = SalarioMax.objects.filter(tipo=obra.tipo,
                                                 grupo_esc=form.cleaned_data['trabajador'].escala_salarial).get()
            sal_obra = SalarioMax.objects.filter(tipo=obra.tipo, grupo_esc=obra.gesc).get()
            coe = sal_obra.sal / sal_trab.sal
            horas = (obra.horas_a2 * coe).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            horas_esp = (horas * esp_factor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            horas_creadas = ((horas_esp * for_factor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) * Decimal(
                form.cleaned_data['porciento'])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            tipo_doc = form.cleaned_data['tipo_doc']
            if tipo_doc == 'MD':
                horas_creadas = form.cleaned_data['especialidad'].md
            if tipo_doc == 'LC':
                horas_creadas = form.cleaned_data['especialidad'].lc
            if tipo_doc == 'PR':
                horas_creadas = form.cleaned_data['especialidad'].pr
            tarifa = Decimal(sal_trab.sal / Decimal(190.6)).quantize(Decimal('.000001'))
            valor_real = ((horas_creadas.quantize(Decimal('.01')) * tarifa).quantize(Decimal('.01'))).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP)
            if tipo_doc == 'PL':
                valor_real = (horas_creadas.quantize(Decimal('.01')) * tarifa).quantize(Decimal('.01'))
            valor_retenido_real = ((horas_creadas.quantize(Decimal('.01')) * tarifa) * Decimal(0.2)).quantize(
                Decimal('.01'))
            valor_total_real = valor_real - valor_retenido_real
            horas_creadas_real = horas_creadas
            valor_plano = valor_real
            valor_retenido = valor_retenido_real
            valor_total = valor_total_real
            plano.num = form.cleaned_data['num']
            plano.objeto = form.cleaned_data['objeto']
            plano.nombre = form.cleaned_data['nombre']
            plano.formato = form.cleaned_data['formato']
            plano.corte = form.cleaned_data['corte']
            plano.obra = form.cleaned_data['obra']
            plano.especialidad = form.cleaned_data['especialidad']
            plano.trabajador = form.cleaned_data['trabajador']
            plano.fecha_ini = form.cleaned_data['fecha_ini']
            plano.fecha_fin = form.cleaned_data['fecha_fin']
            plano.actividad = form.cleaned_data['actividad']
            plano.horas_creadas = horas_creadas_real
            plano.tarifa = tarifa
            plano.valor = Decimal(valor_plano)
            plano.valor_retenido = valor_retenido
            plano.valor_total = valor_total
            plano.horas_creadas_real = horas_creadas
            plano.valor_real = valor_real
            plano.valor_retenido_real = valor_retenido_real
            plano.valor_total_real = valor_total_real
            if plano.valor_pen:
                plano.valor_pen = plano.valor

                plano.incumplimiento_plano_valor = plano.valor_pen * Decimal(
                    plano.incumplimiento_plano / Decimal(100.00)). \
                    quantize(Decimal('1.00'))
                plano.valor_pen = plano.valor_pen - plano.incumplimiento_plano_valor

                plano.incumplimiento_cpl_valor = plano.valor_pen * Decimal(plano.incumplimiento_cpl / Decimal(100.00)). \
                    quantize(Decimal('1.00'))
                plano.valor_pen = plano.valor_pen - plano.incumplimiento_cpl_valor

                plano.incumplimiento_calidad_valor = plano.valor_pen * Decimal(
                    plano.incumplimiento_calidad / Decimal(100.00)). \
                    quantize(Decimal('1.00'))
                plano.valor_pen = plano.valor_pen - plano.incumplimiento_calidad_valor

                plano.valor_retenido = plano.valor_pen * Decimal(0.2)
                plano.etapa=form.cleaned_data['etapa']
            plano.save()
            cal = Plano.objects.all().select_related("actividad").select_related("objeto").select_related(
                "formato").select_related("obra").select_related("especialidad").select_related("trabajador").filter(
                obra__usuarios=request.user.id, obra_id=plano.obra_id)
            plano_filter = PlanoFilter(request.POST, queryset=cal)
            context = {'plano_filter': plano_filter, 'form': form, 'formrev': formrev, 'obras': obras}

    context = context_add_perm(request, context, 'prenomina15', 'plano')
    return render(request, 'Gestionar_Plano.html', context)


@permission_required('prenomina15.change_revision', 'home_principal')
def editar_revision(request, pk):
    obras = listar_obra(request)
    rev = Revision.objects.get(id=pk)
    plano = Plano.objects.get(id=rev.plano_id)
    estado_ant = plano.estado
    nombre = plano.nombre
    formrev = RevisionForm(request.POST or None, instance=rev)
    objeto = plano.objeto.codigo
    num = plano.num
    rev_pago = Plano.objects.get(id=rev.plano_id).rev_pago
    no_rev = rev.no_rev
    if rev_pago is None:
        pago_aprobado = 0
    elif rev_pago == no_rev and rev_pago is not None:
        pago_aprobado = 1
    else:
        pago_aprobado = 2

    if request.method == 'POST':
        if formrev.is_valid():
            if 'Acta' in formrev.cleaned_data['entregado']:
                acta = formrev.cleaned_data['entregado']
            else:
                acta = 'Acta ' + formrev.cleaned_data['entregado']
            rev.fecha_revision = formrev.cleaned_data['fecha_revision']
            rev.entregado = acta
            rev.observaciones = formrev.cleaned_data['observaciones']
            rev.fecha_estado = formrev.cleaned_data['fecha_estado']
            rev.estado = formrev.cleaned_data['estado']
            rev.fecha_vpc = formrev.cleaned_data['fecha_vpc']
            plano.estado = rev.estado

            fecha_pago = request.POST.get("fecha_pago", None)
            if fecha_pago:
                fecha = fecha_pago.split("/")
                plano.fecha_pago = fecha[2]+'-'+fecha[1]+'-'+fecha[0]

            if rev.observaciones is not None:
                plano.orden_servicio = rev.observaciones
            if rev.estado == 'VPC':
                if plano.vpc == 'No' or (plano.vpc == 'Si' and rev.no_rev == plano.rev_vpc):
                    if plano.rev_vpc is None:
                        plano.rev_vpc = rev.no_rev

                    orden = rev.observaciones.split(" ")
                    pos = orden.index('OS')
                    plano.os_vpc = orden[pos] + ' ' + orden[pos + 1]
                    plano.vpc = 'Si'
                    plano.fecha_vpc = rev.fecha_vpc

            if rev.estado != 'VPC' and estado_ant == 'VPC':
                if rev.no_rev == plano.rev_vpc:
                    plano.fecha_vpc = None
                    plano.os_vpc = None
                    plano.estado = rev.estado
                    plano.rev_vpc = None
                    plano.vpc = 'No'
                    rev.fecha_vpc = None

            # if rev.no_rev == 0:
            #    plano.fecha_pago = rev.fecha_revision
            try:
                rev.save()
            except FieldError:
                cal = Revision.objects.filter(plano_id=rev.plano_id)
                context = {'list_rev': cal, 'formrev': formrev, 'obras': obras, 'edit': rev, 'nombre': nombre,
                           'errores': 'Intentelo de nuevo. Ha ocurrido un error de Base de Datos', 'objeto': objeto,
                           'num': num, 'pk': rev.plano_id, 'fecha_pago': fecha_pago}
                context = context_add_perm(request, context, 'prenomina15', 'revision')
                return render(request, 'Listado_Revisiones.html', context)
            except DatabaseError:
                cal = Revision.objects.filter(plano_id=rev.plano_id)
                context = {'list_rev': cal, 'formrev': formrev, 'obras': obras, 'edit': rev, 'nombre': nombre,
                           'errores': 'Intentelo de nuevo. Ha ocurrido un error de Base de Datos', 'objeto': objeto,
                           'num': num, 'pk': rev.plano_id, 'fecha_pago': fecha_pago}
                context = context_add_perm(request, context, 'prenomina15', 'revision')
                return render(request, 'Listado_Revisiones.html', context)
            plano.save()
            cal = Revision.objects.filter(plano_id=rev.plano_id)
            context = {'list_rev': cal, 'formrev': formrev, 'obras': obras, 'nombre': nombre, 'objeto': objeto,
                       'num': num, 'pk': rev.plano_id, 'fecha_pago': fecha_pago}
            context = context_add_perm(request, context, 'prenomina15', 'revision')
            return render(request, 'Listado_Revisiones.html', context)
        else:
            cal = Revision.objects.filter(plano_id=rev.plano_id)
            context = {'list_rev': cal, 'formrev': formrev, 'obras': obras, 'edit': rev.id, 'nombre': nombre,
                       'objeto': objeto, 'num': num, 'pk': rev.plano_id, 'fecha_pago': plano.fecha_pago}
            context = context_add_perm(request, context, 'prenomina15', 'revision')
            return render(request, 'Listado_Revisiones.html', context)
    else:
        cal = Revision.objects.filter(plano_id=rev.plano_id)
        context = {'list_rev': cal, 'formrev': formrev, 'obras': obras, 'edit': rev.id, 'nombre': nombre,
                   'objeto': objeto, 'num': num, 'pk': rev.plano_id, 'rev_pago': rev_pago,
                   'pago_aprobado': pago_aprobado,
                   'no_rev': no_rev, 'fecha_pago': plano.fecha_pago}
        context = context_add_perm(request, context, 'prenomina15', 'revision')
        return render(request, 'Listado_Revisiones.html', context)


@permission_required('prenomina15.change_plano', 'home_principal')
def gestionar_cat(request, pk):
    obras = listar_obra(request)
    list_cat = Catalogo.objects.filter(plano_id=pk)
    plano = Plano.objects.get(id=pk)
    form = CatalogoForm(request.POST or None)

    context = {'form': form,
               'obras': obras,
               'list_cat': list_cat,
               'plano': plano,
               'pk': pk}
    context = context_add_perm(request, context, 'prenomina15', 'plano')
    return render(request, 'Gestionar_Catalogos.html', context)


@permission_required('prenomina15.delete_plano', 'home_principal')
def eliminar_cat(request, pk):
    obras = listar_obra(request)
    catalogo = Catalogo.objects.get(id=pk)
    plano = Plano.objects.get(id=catalogo.plano_id)
    list_cat = Catalogo.objects.filter(plano_id=catalogo.plano)
    form = CatalogoForm(request.POST or None)
    if request.method == 'GET':
        context = {'object': catalogo}
        return render(request, 'Eliminar_Catalogo.html', context)
    else:
        from django.db import IntegrityError
        try:
            plano.cant -= catalogo.cant
            # plano.horas_creadas -= catalogo.horas_creadas
            # plano.valor -= catalogo.valor
            # plano.valor_retenido -= catalogo.valor_retenido
            # plano.valor_total -= catalogo.valor_total
            # plano.horas_creadas_real -= catalogo.horas_creadas_real
            # plano.valor_real -= catalogo.valor_real
            # plano.valor_retenido_real -= catalogo.valor_retenido_real
            # plano.valor_total_real -= catalogo.valor_total_real
            plano.save()
            catalogo.delete()
        except IntegrityError:
            pk = plano.id
            context = {'form': form,
                       'obras': obras,
                       'list_cat': list_cat,
                       'plano': plano,
                       'pk': pk}
            context = context_add_perm(request, context, 'prenomina15', 'plano')
            return render(request, 'Gestionar_Catalogos.html', context)
    pk = plano.id
    context = {'form': form,
               'obras': obras,
               'list_cat': list_cat,
               'plano': plano,
               'pk': pk}
    context = context_add_perm(request, context, 'prenomina15', 'plano')
    return render(request, 'Gestionar_Catalogos.html', context)


@permission_required('prenomina15.change_plano', 'home_principal')
def adicionar_cat(request, pk):
    obras = listar_obra(request)
    plano = Plano.objects.get(id=pk)
    form = CatalogoForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            add_cat(request, pk, form.cleaned_data['formato'], form.cleaned_data['cant'],
                    form.cleaned_data['porciento'])
    list_cat = Catalogo.objects.filter(plano_id=pk)
    context = {'form': form,
               'obras': obras,
               'list_cat': list_cat,
               'plano': plano,
               'pk': pk}
    context = context_add_perm(request, context, 'prenomina15', 'plano')
    return render(request, 'Gestionar_Catalogos.html', context)


@permission_required('prenomina15.change_plano', 'home_principal')
def add_cat(request, pk, formato, cant, porciento):
    plano = Plano.objects.get(id=pk)
    sal_trab = SalarioMax.objects.filter(tipo=plano.obra.tipo,
                                         grupo_esc=plano.trabajador.escala_salarial).get()
    sal_obra = SalarioMax.objects.filter(tipo=plano.obra.tipo, grupo_esc=plano.obra.gesc).get()
    coe = sal_obra.sal / sal_trab.sal
    horas_creadas_real = 0
    valor_plano = 0
    valor_retenido = 0
    valor_total = 0
    esp_factor = plano.especialidad.factor
    for_factor = formato.factor
    cantn = cant
    horas = (plano.obra.horas_a2 * coe).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    horas_esp = (horas * esp_factor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    horas_creadas = ((horas_esp * for_factor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) * Decimal(
        porciento)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    tarifa = Decimal(sal_trab.sal / Decimal(190.6)).quantize(Decimal('.000001'))
    valor_real = (horas_creadas.quantize(Decimal('.01')) * tarifa).quantize(Decimal('.01'))
    valor_retenido_real = ((horas_creadas.quantize(Decimal('.01')) * tarifa) * Decimal(0.2)).quantize(
        Decimal('.01'))
    valor_total_real = valor_real - valor_retenido_real
    horas_creadas_real = horas_creadas
    valor_plano = valor_real
    valor_retenido = valor_retenido_real
    valor_total = valor_total_real
    while cantn != 0:
        cantn -= 1
        catalogo = Catalogo(
            plano=plano,
            formato=formato,
            cant=1,
            porciento=porciento,
            horas_creadas=horas_creadas_real,
            valor=Decimal(valor_plano),
            valor_retenido=valor_retenido,
            valor_total=valor_total,
            horas_creadas_real=horas_creadas,
            valor_real=valor_real,
            valor_retenido_real=valor_retenido_real,
            valor_total_real=valor_total_real
        )
        catalogo.save()
        plano.cant += catalogo.cant
        # plano.horas_creadas += catalogo.horas_creadas
        # plano.valor += catalogo.valor
        # plano.valor_retenido += catalogo.valor_retenido
        # plano.valor_total += catalogo.valor_total
        # plano.horas_creadas_real += catalogo.horas_creadas_real
        # plano.valor_real += catalogo.valor_real
        # plano.valor_retenido_real += catalogo.valor_retenido_real
        # plano.valor_total_real += catalogo.valor_total_real
        plano.save()

    return


@permission_required('prenomina15.delete_obra', 'home_principal')
def eliminar_obra(request, pk):
    user_id = User.objects.get(username=request.user).id
    obras = listar_obra(request)
    obra = Obra.objects.get(id=pk)
    if request.method == 'GET':
        context = {'object': obra}
        return render(request, 'Eliminar_Obra.html', context)
    else:
        from django.db import IntegrityError
        try:
            obra.delete()
            return redirect('/pren/obras/')
        except IntegrityError:
            cal = Obra.objects.all().select_related("orden_trab").select_related("gesc").filter(usuarios=user_id)
            form = ObraForm(None)
            context = {'list_obras': cal, 'form': form, 'obras': obras,
                       'errores': 'Imposible eliminar la Obra porque tiene al menos un Plano o un Objeto '
                                  'asociado.'}
            context = context_add_perm(request, context, 'prenomina15', 'obra')
            return render(request, 'Gestionar_Obra.html', context)


@permission_required('prenomina15.delete_objeto', 'home_principal')
def eliminar_objeto(request, pk):
    user_id = User.objects.get(username=request.user).id
    obj = Objeto.objects.get(id=pk)
    obras = listar_obra(request)
    obra = obj.obra
    form = ObjetoForm(None)
    if request.method == 'GET':
        context = {'object': obj, 'obra': obra, 'obras': obras}
        context = context_add_perm(request, context, 'prenomina15', 'objeto')
        return render(request, 'Eliminar_Objeto.html', context)
    else:
        from django.db import IntegrityError
        try:
            obj.delete()
            return redirect('gestionarObjeto', obra.id)
        except IntegrityError:
            cal = Objeto.objects.all().select_related("obra").filter(obra__usuarios=user_id)
            form = ObjetoForm(None)
            context = {'list_obj': cal, 'form': form, 'obras': obras,'obra': obra,
                       'errores': 'Imposible eliminar el Objeto porque tiene al menos un Plano asociado.'}
            context = context_add_perm(request, context, 'prenomina15', 'objeto')
            return render(request, 'Gestionar_Objeto.html', context)


@permission_required('prenomina15.delete_plano', 'home_principal')
def eliminar_plano(request, pk):
    user_id = User.objects.get(username=request.user).id
    obras = listar_obra(request)
    plano = Plano.objects.get(id=pk)
    obra = Obra.objects.get(id=plano.obra_id)
    if request.method == 'GET':
        context = {'object': plano}
        return render(request, 'Eliminar_Plano.html', context)
    else:
        from django.db import IntegrityError
        try:
            plano.delete()
            return redirect('/pren/planos/')
        except IntegrityError:
            cal = Plano.objects.all().select_related("actividad").select_related("objeto").select_related(
                "formato").select_related("obra").select_related("especialidad").select_related("trabajador").filter(
                obra__usuarios=user_id)
            form = PlanoForm(None)
            formrev = RevisionForm(None)
            context = {'list_planos': cal, 'form': form, 'obras': obras, 'obra': obra, 'formrev': formrev,
                       'errores': 'Imposible eliminar el Plano porque tiene datos asociados.'}
            context = context_add_perm(request, context, 'prenomina15', 'plano')
            return render(request, 'Gestionar_Plano.html', context)


@permission_required('prenomina15.delete_revision', 'home_principal')
def eliminar_revision(request, pk):
    obras = listar_obra(request)
    formrev = RevisionForm(request.POST or None)
    plano = Plano.objects.get(pk=pk)
    rev = Revision.objects.get(plano_id=plano.id, no_rev=plano.last_rev)
    nombre = plano.nombre
    objeto = plano.objeto.codigo
    num = plano.num
    if request.method == 'GET':
        context = {'object': plano}
        context = context_add_perm(request, context, 'prenomina15', 'revision')
        return render(request, 'Eliminar_Revision.html', context)
    else:
        try:
            if rev.no_rev == 0 and rev.estado != 'VPC':
                plano.fecha_pago = None
                plano.last_rev = None
                plano.orden_servicio = None
                plano.estado = 'SR'
            if rev.estado == 'VPC' and rev.no_rev == 0:
                plano.fecha_vpc = None
                plano.fecha_pago = None
                plano.last_rev = None
                plano.vpc = 'No'
                plano.orden_servicio = None
                plano.estado = 'SR'
                plano.rev_vpc = None
                plano.os_vpc = None
                plano.rev_vpc = None
            if rev.estado == 'VPC' and rev.no_rev != 0:
                plano.last_rev = rev.no_rev - 1
                penul_rev = Revision.objects.filter(plano_id=plano.id, no_rev=rev.no_rev - 1)
                plano.orden_servicio = penul_rev.get().observaciones
                plano.estado = penul_rev.get().estado
                if Revision.objects.filter(plano_id=plano.id, estado='VPC').count() == 1:
                    plano.fecha_vpc = None
                    plano.vpc = 'No'
                    plano.rev_vpc = None
                    plano.os_vpc = None
                    plano.rev_vpc = None
            if rev.no_rev != 0:
                plano.last_rev = rev.no_rev - 1
                observaciones = Revision.objects.filter(plano_id=plano.id, no_rev=rev.no_rev - 1)
                plano.orden_servicio = observaciones.get().observaciones
                plano.estado = observaciones.get().estado
                plano.vpc = 'No'
                plano.fecha_vpc = None
            rev.delete()
        except FieldError:
            list_rev = Revision.objects.all().filter(plano_id=pk)
            context = {'list_rev': list_rev, 'obras': obras, 'nombre': nombre, 'objeto': objeto, 'num': num, 'pk': pk,
                       'errores': 'Intentelo de nuevo. Ha ocurrido un error de Base de Datos', 'formrev': formrev}
            context = context_add_perm(request, context, 'prenomina15', 'revision')
            return render(request, 'Listado_Revisiones.html', context)
        except DatabaseError:
            list_rev = Revision.objects.all().filter(plano_id=pk)
            context = {'list_rev': list_rev, 'obras': obras, 'nombre': nombre, 'objeto': objeto, 'num': num, 'pk': pk,
                       'errores': 'Intentelo de nuevo. Ha ocurrido un error de Base de Datos', 'formrev': formrev}
            context = context_add_perm(request, context, 'prenomina15', 'revision')
            return render(request, 'Listado_Revisiones.html', context)
        plano.save()
        list_rev = Revision.objects.all().filter(plano_id=pk)
        context = {'list_rev': list_rev, 'obras': obras, 'nombre': nombre, 'objeto': objeto, 'num': num, 'pk': pk,
                   'formrev': formrev}
        context = context_add_perm(request, context, 'prenomina15', 'revision')
        return render(request, 'Listado_Revisiones.html', context)


# Buscar
def obj_por_obra(request, pk):
    objetos = Objeto.objects.filter(obra=pk).order_by('codigo')
    datos = [{'nombre': obj.nombre, 'codigo': obj.codigo, 'id': obj.id} for obj in objetos]
    response = [{"success": 1, "result": datos}]
    return HttpResponse(json.dumps(response), content_type='application/json')


def act_por_obra(request, pk):
    obra = Obra.objects.get(id=pk)
    actividades = Actividad.objects.filter(orden_trab_id=obra.orden_trab_id).order_by('codigo_act')
    datos = [{'nombre': act.descripcion_act, 'codigo': act.codigo_act, 'id': act.id} for act in actividades]
    response = [{"success": 1, "result": datos}]
    return HttpResponse(json.dumps(response), content_type='application/json')


@permission_required('prenomina15.generate_acta', 'home_principal')
def acta_entrega_planos(request):
    obras = listar_obra(request)
    fecha = ''
    list_rev = ''
    acta = ''
    obra = ''
    recibido_por = ''
    elaborado_por = ''
    if request.POST:
        fecha = request.POST['fecha']
        if fecha:
            list_rev = Revision.objects.filter(fecha_estado=fecha).select_related("plano").select_related(
                "plano__trabajador").select_related("plano__objeto").select_related(
                "plano__especialidad").select_related("plano__actividad").select_related("plano__obra").select_related(
                "plano__obra__orden_trab")
            if list_rev:
                acta = list_rev[0].entregado
                obra = list_rev[0].plano.obra.orden_trab.descripcion_ot
                recibido_por = request.POST['recibido_por']
                elaborado_por = request.user
            context = {'list_rev': list_rev, 'fecha': fecha, 'obras': obras, 'acta': acta, 'obra': obra,
                       'recibido_por': recibido_por, 'elaborado_por': elaborado_por}
            context = context_add_perm(request, context, 'prenomina15', 'acta')
            return render(request, 'Acta_Entrega.html', context)
        else:
            context = {'list_rev': list_rev, 'fecha': fecha, 'obras': obras}
            context = context_add_perm(request, context, 'prenomina15', 'acta')
            return render(request, 'Acta_Entrega.html', context)
    else:
        context = {'list_rev': list_rev, 'fecha': fecha, 'obras': obras}
        context = context_add_perm(request, context, 'prenomina15', 'acta')
        return render(request, 'Acta_Entrega.html', context)


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


@permission_required('prenomina15.read_certifico', 'home_principal')
def visualizar_certifico(request):
    obras = listar_obra(request)
    fecha_ini = request.POST['inicio']
    fecha_fin = request.POST['fin']
    obra = request.POST['obra1']
    recibido_por = request.POST['recibido_por']
    cargo = request.POST['cargo']
    org = request.POST['org']
    if fecha_ini == '' or fecha_fin == '':
        error_cert = True
        context = {'error_cert': error_cert, 'obras': obras}
        context = context_add_perm(request, context, 'prenomina15')
        return render(request, 'home_pren15.html', context)
    else:
        context = {'fecha_ini': fecha_ini, 'fecha_fin': fecha_fin, 'obras': obras, 'obra': obra,
                   'recibido_por': recibido_por, 'cargo': cargo, 'org': org,
                   'cortes': request_report_certifico(fecha_ini, fecha_fin, obra)}
        context = context_add_perm(request, context, 'prenomina15')
        return render(request, 'Exportar_Certifico.html', context)


@permission_required('prenomina15.generate_acta', 'home_principal')
def list_acta(request):
    obras = listar_obra(request)
    alpha = 0
    if 'alpha' in request.POST:
        alpha = 1
    obra_id = ''
    if 'obra_acta' in request.POST:
        obra_id = request.POST['obra_acta']
    obra = Obra.objects.get(id=obra_id)
    orden_trab = obra.orden_trab.descripcion_ot
    fecha = ''
    act = ''
    list_planos = ''
    recibido_por = ''
    elaborado_por = ''
    actas_activas = False
    list_act = Revision.objects.all().filter(entregado__contains='Acta', plano__obra_id=obra_id).distinct(
        'entregado').order_by('entregado')
    if list_act:
        act = list_act[0].entregado
        list_planos = Revision.objects.filter(entregado=act, plano__obra_id=obra_id).select_related(
            'plano').select_related(
            'plano__trabajador').select_related('plano__actividad').select_related('plano__objeto')
        fecha = list_act[0].fecha_estado
        recibido_por = request.POST['recibido_por_acta']
        elaborado_por = request.user
        actas_activas = True
        context = {'list_act': list_act, 'list_planos': list_planos, 'act': act, 'obras': obras, 'obra': obra,
                   'fecha': fecha, 'orden_trab': orden_trab, 'elaborado_por': elaborado_por,
                   'recibido_por': recibido_por,
                   'actas_activas': actas_activas, 'alpha': alpha}
        context = context_add_perm(request, context, 'prenomina15', 'acta')
        return render(request, 'Buscar_Acta.html', context)
    else:
        context = {'list_act': list_act, 'list_planos': list_planos, 'act': act, 'obras': obras, 'obra': obra,
                   'fecha': fecha, 'orden_trab': orden_trab, 'elaborado_por': elaborado_por,
                   'recibido_por': recibido_por,
                   'actas_activas': actas_activas, 'alpha': alpha}
        context = context_add_perm(request, context, 'prenomina15', 'acta')
        return render(request, 'Buscar_Acta.html', context)


@permission_required('prenomina15.read_obra', 'home_principal')
def listar_obra(request):
    obras = Obra.objects.all().filter(usuarios=request.user.id, activa=True)
    return obras



@permission_required('prenomina15.read_obra', 'home_principal')
def listar_trabaj_pen_obra(request, planos=None):
    penalizaciones = []
    for plano in planos:
        flag = False
        for pen in penalizaciones:
            if plano.trabajador == pen.trabajador and plano.corte == pen.corte:
                flag = True
                break
        if not flag:
            penalizaciones.append(Penalizaciones(trabajador_id=plano.trabajador_id,
                                                 trabajador=plano.trabajador,
                                                 corte=plano.corte,
                                                 inc_plano=plano.incumplimiento_plano,
                                                 inc_cpl=plano.incumplimiento_cpl,
                                                 inc_calidad=plano.incumplimiento_calidad))
    return penalizaciones


def penalizar(request, planos, pen_plano=None, pen_cpl=None, pen_calidad=None):
    for plano in planos:

        plano.valor_pen = plano.valor_real

        plano.incumplimiento_plano = pen_plano
        incumplimiento_plano = Decimal(pen_plano / Decimal(100.00)).quantize(Decimal('1.00'))
        plano.incumplimiento_plano_valor = plano.valor_pen * incumplimiento_plano
        plano.valor_pen = plano.valor_pen - plano.incumplimiento_plano_valor

        plano.incumplimiento_cpl = pen_cpl
        incumplimiento_cpl = Decimal(pen_cpl / Decimal(100.00)).quantize(Decimal('1.00'))
        plano.incumplimiento_cpl_valor = plano.valor_pen * incumplimiento_cpl
        plano.valor_pen = plano.valor_pen - plano.incumplimiento_cpl_valor

        plano.incumplimiento_calidad = pen_calidad
        incumplimiento_calidad = Decimal(pen_calidad / Decimal(100.00)).quantize(Decimal('1.00'))
        plano.incumplimiento_calidad_valor = plano.valor_pen * incumplimiento_calidad
        plano.valor_pen = plano.valor_pen - plano.incumplimiento_calidad_valor

        plano.valor = plano.valor_pen
        plano.valor_retenido = plano.valor * Decimal(0.2)
        plano.valor_total = plano.valor - plano.valor_retenido
        plano.valor_pen = (
                plano.incumplimiento_plano_valor + plano.incumplimiento_cpl_valor + plano.incumplimiento_calidad_valor)

        plano.save()
        if plano.cant != 1:
            catalogo = Catalogo.objects.all().filter(plano_id=plano.id)
            for cat in catalogo:
                cat.valor_pen = cat.valor_real

                cat.incumplimiento_plano_valor = cat.valor_pen * incumplimiento_plano
                cat.valor_pen = cat.valor_pen - cat.incumplimiento_plano_valor

                cat.incumplimiento_cpl_valor = cat.valor_pen * incumplimiento_cpl
                cat.valor_pen = cat.valor_pen - cat.incumplimiento_cpl_valor

                cat.incumplimiento_calidad_valor = cat.valor_pen * incumplimiento_calidad
                cat.valor_pen = cat.valor_pen - cat.incumplimiento_calidad_valor

                cat.valor = cat.valor_pen
                cat.valor_retenido = cat.valor * Decimal(0.2)
                cat.valor_total = cat.valor - cat.valor_retenido
                cat.valor_pen = (
                        cat.incumplimiento_plano_valor + cat.incumplimiento_cpl_valor + cat.incumplimiento_calidad_valor)

                cat.save()
    return


@permission_required('prenomina15.read_obra', 'home_principal')
def listar_cortes_pen_obra(request, obra=None):
    planos = Plano.objects.all().filter(obra_id=obra)
    cortes = []
    for plano in planos:
        flag = False
        for corte in cortes:
            if plano.corte == corte.corte:
                flag = True
                break
        if not flag:
            cortes.append(Cortes_Penalizaciones(corte=plano.corte))
    return cortes


@permission_required('prenomina15.read_acta', 'home_principal')
def buscar_acta(request, obra_id, recibido_por=None, alpha=None):
    obras = listar_obra(request)
    obra = Obra.objects.get(id=obra_id)
    list_act = Revision.objects.all().filter(entregado__contains='Acta', plano__obra_id=obra.id).distinct(
        'entregado').order_by('entregado')
    acta = request.POST['acta']
    list_planos = Revision.objects.filter(entregado=acta, plano__obra_id=obra.id).select_related(
        'plano').select_related(
        'plano__trabajador').select_related('plano__actividad').select_related('plano__objeto')
    act = list_planos[0].entregado
    fecha = list_planos[0].fecha_estado
    actas_activas = True
    elaborado_por = request.user
    context = {'list_act': list_act, 'list_planos': list_planos, 'act': act, 'obras': obras, 'obra': obra,
               'fecha': fecha, 'elaborado_por': elaborado_por, 'recibido_por': recibido_por,
               'actas_activas': actas_activas, 'alpha': alpha}
    context = context_add_perm(request, context, 'prenomina15', 'acta')
    return render(request, 'Buscar_Acta.html', context)


@permission_required('prenomina15.export_dato', 'home_principal')
def exportar_datos(request):
    obras = listar_obra(request)
    fecha_ini = request.POST['fecha_inic']
    fecha_fin = request.POST['fecha_fin']
    obra = request.POST['obra1']
    if fecha_ini == '' or fecha_fin == '':
        error_add = True
        context = {'error_add': error_add, 'obras': obras}
        context = context_add_perm(request, context, 'prenomina15')
        return render(request, 'home_pren15.html', context)
    else:
        context = request_report(fecha_ini, fecha_fin, obra, request)
        context = context_add_perm(request, context, 'prenomina15')
        return render(request, 'Exportar_Datos.html', context)


@permission_required('prenomina15.export_dato', 'home_principal')
def control_planos(request):
    obras = listar_obra(request)
    fecha_ini = request.POST['fecha_inic']
    fecha_fin = request.POST['fecha_fin']
    obra = request.POST['obra1']
    if fecha_ini == '' or fecha_fin == '':
        error_add = True
        context = {'error_add': error_add, 'obras': obras}
        context = context_add_perm(request, context, 'prenomina15')
        return render(request, 'home_pren15.html', context)
    else:
        context = request_report_cp(fecha_ini, fecha_fin, obra, request)
        context = context_add_perm(request, context, 'prenomina15')
        return render(request, 'Control_Planos.html', context)


@permission_required('prenomina15.export_acta', 'home_principal')
def exportar_acta_entrega(request, obra_id, acta, rp, alpha):
    list_rev = Revision.objects.filter(entregado=acta, plano__obra_id=obra_id).select_related("plano").select_related(
        "plano__trabajador").select_related("plano__objeto").select_related(
        "plano__especialidad").select_related("plano__actividad").select_related("plano__obra").select_related(
        "plano__obra__orden_trab").order_by('no_rev', 'plano__especialidad__siglas', 'plano__trabajador__primer_nombre')
    elaborado_por = request.user
    acta = list_rev[0].entregado
    fecha = list_rev[0].fecha_estado
    obra = list_rev[0].plano.obra.orden_trab.descripcion_ot
    context = {'list_rev': list_rev, 'elaborado_por': elaborado_por, 'acta': acta, 'obra': obra, 'recibido_por': rp,
               'fecha': fecha, 'alpha': alpha}
    template_path = 'Acta_Entrega_template.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Acta_Entrega_Planos.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisastatus = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisastatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisastatus.err,
                                                                               html))
    return response


@permission_required('prenomina15.export_certifico', 'home_principal')
def exportar_certifico(request, obra, fecha_ini, fecha_fin, recibido_por, cargo, org):
    obras = listar_obra(request)
    nombre = Obra.objects.get(id=obra).orden_trab.descripcion_ot
    diccionario = {'01': 'Enero', '02': 'Febrero', '03': 'Marzo', '04': 'Abril', '05': 'Mayo', '06': 'Junio',
                   '07': 'Julio', '08': 'Agosto', '09': 'Septiembre', '10': 'Octubre', '11': 'Noviembre',
                   '12': 'Diciembre'}
    anno = fecha_fin[0:4]
    mes = diccionario[fecha_fin[5:7]]
    director = Trabajador.objects.get(cargo=164)
    template_path = 'Exportar_Certifico_template.html'
    context = {'cortes': request_report_certifico(fecha_ini, fecha_fin, obra), 'obras': obras, 'fecha_ini': fecha_ini,
               'fecha_fin': fecha_fin, 'nombre': nombre, 'anno': anno, 'mes': mes, 'director': director,
               'recibido_por': recibido_por, 'cargo': cargo, 'org': org}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte_Certifico.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisastatus = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisastatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisastatus.err,
                                                                               html))
    return response


@permission_required('prenomina15.export_prenomina', 'home_principal')
def exportar_prenomina(request):
    obras = listar_obra(request)
    fecha_ini = request.POST['fecha_inic']
    fecha_fin = request.POST['fecha_fin']
    obra = request.POST['obra1']
    if fecha_ini == '' or fecha_fin == '':
        error_pren = True
        context = {'error_pren': error_pren, 'obras': obras}
        context = context_add_perm(request, context, 'prenomina15')
        return render(request, 'home_pren15.html', context)
    else:
        context = request_report_pren(fecha_ini, fecha_fin, obra, request)
        context = context_add_perm(request, context, 'prenomina15')
        return render(request, 'Exportar_Prenomina.html', context)


@permission_required('prenomina15.export_prenomina', 'home_principal')
def exportar_comp_trab(request):
    obras = listar_obra(request)
    fecha_ini = request.POST['fecha_inic']
    fecha_fin = request.POST['fecha_fin']
    if fecha_ini == '' or fecha_fin == '':
        error_comp_trab = True
        context = {'error_comp_trab': error_comp_trab, 'obras': obras}
        context = context_add_perm(request, context, 'prenomina15')
        return render(request, 'home_pren15.html', context)
    else:
        context = request_report_pren_trab(fecha_ini, fecha_fin, request)
        context = context_add_perm(request, context, 'prenomina15')
        return render(request, 'Compendio_trabajador.html', context)


@permission_required('prenomina15.export_prenomina', 'home_principal')
def exportar_comp_obras(request):
    obras = listar_obra(request)
    fecha_ini = request.POST['fecha_inic']
    fecha_fin = request.POST['fecha_fin']
    if fecha_ini == '' or fecha_fin == '':
        error_comp_serv = True
        context = {'error_comp_serv': error_comp_serv, 'obras': obras}
        context = context_add_perm(request, context, 'prenomina15')
        return render(request, 'home_pren15.html', context)
    else:
        context = request_report_pren_serv(fecha_ini, fecha_fin, request)
        context = context_add_perm(request, context, 'prenomina15')
        return render(request, 'Compendio_servicio.html', context)



@permission_required('prenomina15.export_anexo', 'home_principal')
def exportar_anexo(request):
    obras = listar_obra(request)
    fecha_ini = request.POST['fecha1']
    fecha_fin = request.POST['fecha2']
    obra = request.POST['obra1']
    horas = request.POST['total_hrs']
    if fecha_ini == '' or fecha_fin == '':
        error_anexo = True
        context = {'error_anexo': error_anexo, 'obras': obras}
        context = context_add_perm(request, context, 'prenomina15')
        return render(request, 'home_pren15.html', context)
    else:
        context = request_report_anexo(fecha_ini, fecha_fin, obra, horas, request)
        context = context_add_perm_menu_pren15(request, context)
        return render(request, 'Exportar_Anexo2.html', context)


def request_report(fecha_inic, fecha_fin, obra, request):
    sql = """
        SELECT
            ges_trab_trabajador.primer_nombre, ges_trab_trabajador.segundo_nombre,prenomina15_plano.fecha_vpc,
            ges_trab_trabajador.apellidos, adm_cargo.nombre as nom_cargo,
            adm_escalasalarial.grupo, prenomina15_salariomax.sal, prenomina15_plano.id,
            prenomina15_plano.formato_id, prenomina15_plano.porciento,
            prenomina15_plano.tarifa, prenomina15_plano.cant,
            entrada_datos_actividad.codigo_act, prenomina15_plano.horas_creadas,
            prenomina15_plano.valor, prenomina15_plano.tipo_doc,
            prenomina15_plano.valor_total, prenomina15_plano.valor_retenido,
            prenomina15_plano.nombre,
            prenomina15_plano.num,
            prenomina15_objeto.codigo,
            prenomina15_plano.last_rev, prenomina15_plano.fecha_pago,
            prenomina15_especialidad.nombre as nombre_esp,
            prenomina15_plano.trabajador_id, prenomina15_plano.id,
            prenomina15_objeto.nombre as nombre_obj, prenomina15_plano.corte,
            prenomina15_plano.horas_creadas_real,
            prenomina15_plano.valor_real, prenomina15_plano.valor_retenido_real,
            prenomina15_plano.valor_total_real,
            prenomina15_plano.vpc, prenomina15_especialidad.siglas
        from
            public.ges_trab_trabajador, public.prenomina15_plano, public.adm_cargo,
            public.adm_escalasalarial, public.prenomina15_salariomax, public.prenomina15_obra,
            public.prenomina15_formato, public.entrada_datos_actividad, public.prenomina15_objeto,
            public.prenomina15_especialidad
        where
            ges_trab_trabajador.id = prenomina15_plano.trabajador_id and
            adm_cargo.id = ges_trab_trabajador.cargo_id and
            prenomina15_salariomax.grupo_esc_id = adm_escalasalarial.id and
            adm_escalasalarial.id = ges_trab_trabajador.escala_salarial_id and
            prenomina15_plano.obra_id = '{}' and
            prenomina15_obra.tipo = prenomina15_salariomax.tipo and
            prenomina15_formato.id = prenomina15_plano.formato_id and
            entrada_datos_actividad.id = prenomina15_plano.actividad_id and
            prenomina15_objeto.id = prenomina15_plano.objeto_id and
            prenomina15_plano.especialidad_id = prenomina15_especialidad.id and
            (prenomina15_plano.fecha_pago BETWEEN '{}'::DATE AND '{}'::DATE or
            prenomina15_plano.fecha_vpc BETWEEN '{}'::DATE AND '{}'::DATE)
        group by
            prenomina15_plano.vpc, prenomina15_especialidad.nombre,
            ges_trab_trabajador.primer_nombre, ges_trab_trabajador.segundo_nombre,
            ges_trab_trabajador.apellidos, adm_cargo.nombre,
            adm_escalasalarial.grupo, prenomina15_salariomax.sal,
            prenomina15_formato.id, prenomina15_plano.porciento, prenomina15_plano.id,
            prenomina15_plano.tarifa, entrada_datos_actividad.codigo_act,
            prenomina15_plano.horas_creadas, prenomina15_plano.valor, prenomina15_plano.tipo_doc,
            prenomina15_plano.valor_total, prenomina15_plano.valor_retenido,
            prenomina15_plano.nombre, prenomina15_plano.num,
            prenomina15_especialidad.siglas, prenomina15_objeto.codigo,
            prenomina15_plano.last_rev, prenomina15_plano.fecha_pago,
            prenomina15_plano.fecha_vpc, prenomina15_plano.trabajador_id,
            prenomina15_plano.id, prenomina15_objeto.nombre, prenomina15_plano.corte,
            prenomina15_plano.horas_creadas_real, prenomina15_plano.valor_real,
            prenomina15_plano.valor_retenido_real, prenomina15_plano.valor_total_real
        order by
            prenomina15_especialidad.nombre,
            adm_escalasalarial.grupo DESC,
            ges_trab_trabajador.primer_nombre,
            ges_trab_trabajador.segundo_nombre,
            ges_trab_trabajador.apellidos,
            prenomina15_plano.num;
        """.format(obra, fecha_inic, fecha_fin, fecha_inic, fecha_fin)
    obras = listar_obra(request)
    result = Plano.objects.raw(sql)
    especialidades = []
    personas = []
    planos = []

    for element in result:
        flag = False
        for esp in especialidades:
            if esp.nombre == element.nombre_esp:
                flag = True
                break
        if not flag:
            especialidades.append(Esp(nombre=element.nombre_esp, personas=[], cant=0))
    for element in result:
        flag = False
        for per in personas:
            if per.no == element.trabajador_id:
                if per.especialidad == element.nombre_esp:
                    flag = True
                    break
        if not flag:
            personas.append(
                Persona(no=element.trabajador_id,
                        nombre=element.primer_nombre + ' ' + element.segundo_nombre + ' ' + element.apellidos,
                        planos=[], cargo=element.nom_cargo, ge=element.grupo, sal_max=element.sal,
                        tarifa=element.tarifa, total_horas=0, total_pagar=0, total_retenido=0, total_valor=0, cant=0,
                        especialidad=element.nombre_esp, retenido_ant=0, pagar=0))

    for element in result:
        val = ''
        pagar = ''
        retenido = 0
        pago_ant = 0
        horas_creadas = 0
        valor_retenido_real = 0
        valor_total_real = 0
        horas_creadas_real = 0
        list_cant = []
        catalogo = []
        cantidad = element.cant - 1
        inicio = datetime.datetime.strptime(fecha_inic, "%Y-%m-%d").date()
        fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        fecha_pago = datetime.datetime.strptime(str(element.fecha_pago), "%Y-%m-%d").date()
        if element.fecha_vpc is not None:
            fecha_vpc = datetime.datetime.strptime(str(element.fecha_vpc), "%Y-%m-%d").date()
            if inicio <= fecha_pago <= fin and inicio <= fecha_vpc <= fin:
                val = 0  # el caso 0 es para cuando se paga el plano 100 %
                horas_creadas = element.horas_creadas
                pagar = element.valor_real
                horas_creadas_real = element.horas_creadas_real
            if (fecha_pago < inicio or fecha_pago > fin) and inicio <= fecha_vpc <= fin:
                val = 1  # el caso 1 es para cuando se paga el plano 20 %
                pagar = 0
                pago_ant = element.valor_retenido
                horas_creadas = 0
            if inicio <= fecha_pago <= fin and (fecha_vpc < inicio or fecha_vpc > fin):
                val = 2  # el caso 2 es para cuando se paga el plano 80 %
                pagar = element.valor_total_real
                valor_total_real = element.valor_total_real
                retenido = element.valor_retenido_real
                valor_retenido_real = element.valor_retenido_real
                horas_creadas = element.horas_creadas_real
                horas_creadas_real = element.horas_creadas_real
        else:
            if inicio <= fecha_pago <= fin:
                val = 2  # el caso 2 es para cuando se paga el plano 80 %
                pagar = element.valor_total_real
                valor_total_real = element.valor_total_real
                retenido = element.valor_retenido_real
                valor_retenido_real = element.valor_retenido_real
                horas_creadas = element.horas_creadas_real
                horas_creadas_real = element.horas_creadas_real
        while cantidad != 0:
            list_cant.append(1)
            cantidad -= 1
        if element.cant != 1:
            catalogos = Catalogo.objects.all().filter(plano_id=element.id)
            for cat in catalogos:

                catalogo.append(Cat(formato=cat.formato, porciento=int(float(cat.porciento) * 100), horas_creadas=cat.horas_creadas,
                                    horas_creadas_real=cat.horas_creadas_real, valor_retenido=cat.valor_retenido,
                                    valor_retenido_real=cat.valor_retenido_real, valor=cat.valor,
                                    valor_real=cat.valor_real, valor_total=cat.valor_total,
                                    valor_total_real=cat.valor_total_real))
        planos.append(
            Plan(nombre=element.nombre, codigo=element.num, objeto=element.codigo, etapa=element.codigo_act,
                 formato=element.formato.formato, porciento=int(float(element.porciento) * 100),
                 horas_creadas=horas_creadas, nombre_obj=element.nombre_obj,
                 valor=element.valor, valor_total=element.valor_total, retenido=retenido, reten_ant=pago_ant,
                 rev=element.last_rev, vpc=element.vpc, trabajador_id=element.trabajador_id,
                 ult_rev=element.last_rev, especialidad=element.nombre_esp, caso=val, pagar=pagar, cant=element.cant,
                 corte=element.corte, horas_creadas_real=horas_creadas_real, valor_real=element.valor_real,
                 valor_retenido_real=valor_retenido_real, valor_total_real=valor_total_real, list_cant=list_cant,
                 tarifa=element.tarifa, sigla=element.siglas, tipo_doc=element.tipo_doc, catalogo=catalogo))

    for per in personas:
        for plano in planos:
            if plano.trabajador_id == per.no and plano.especialidad == per.especialidad:
                per.planos.append(plano)
                if plano.caso != 1:
                    per.cant += 1
                    per.total_valor += plano.valor_real
                per.total_horas += plano.horas_creadas
                per.total_retenido += plano.valor_retenido_real
                per.pagar += plano.pagar
                if plano.caso == 1:
                    per.retenido_ant += plano.reten_ant
                if plano.cant != 1:
                    for c in plano.catalogo:
                        if plano.caso == 0:
                            per.total_valor += c.valor_real
                            per.total_horas += c.horas_creadas
                            per.pagar += c.valor_real
                        if plano.caso == 1:
                            per.total_retenido += c.valor_retenido
                            per.retenido_ant += c.valor_retenido_real
                            per.pagar += plano.pagar
                            per.total_horas += plano.horas_creadas
                        if plano.caso == 2:
                            per.total_valor += c.valor_real
                            per.total_horas += c.horas_creadas
                            per.total_retenido += c.valor_retenido_real
                            per.pagar += c.valor_total_real

    total_planos = 0
    for esp in especialidades:
        for per in personas:
            if per.especialidad == esp.nombre:
                esp.personas.append(per)
                esp.cant += per.cant
        total_planos += esp.cant

    completo = Plano.objects.all().filter(fecha_vpc__range=(fecha_inic, fecha_fin),
                                          fecha_pago__range=(fecha_inic, fecha_fin), obra=obra).count()
    retenido = Plano.objects.all().filter(fecha_vpc__range=(fecha_inic, fecha_fin), obra=obra).count() - completo

    return {'especialidades': especialidades, 'fecha_inic': fecha_inic, 'fecha_fin': fecha_fin, 'obras': obras,
            'total_planos': total_planos, 'completo': completo, 'retenido': retenido}

def request_report_cp(fecha_inic, fecha_fin, obra, request):
    result = Plano.objects.annotate(
        nombre_obj=F('objeto__nombre')
    ).filter(obra=obra).filter(
        Q(fecha_pago__range=[fecha_inic, fecha_fin]) | Q(fecha_vpc__range=[fecha_inic, fecha_fin])
    ).order_by(
        'objeto__codigo', 'num', 'etapa'
    )
    print(result.query)

    obras = listar_obra(request)
    etapas = []
    objetos = []

    for element in result:
        flag = False
        for etapa in etapas:
            if etapa.nombre == element.etapa:
                flag = True
                break
        if not flag:
            etapas.append(Etapas(nombre=element.etapa,
                                objetos=[], cant=0, total_planos_plan=0, total_planos_real=0,
                                total_planos_vpc_90=0, total_planos_vpc_100=0, total_planos_vpc_ret=0,
                                total_planos_vpc_ret_ant=0))
    for element in result:
        flag = False
        for objeto in objetos:
            if objeto.codigo == element.objeto.codigo:
                if objeto.etapa == element.etapa:
                    flag = True
                    break
        if not flag:
            objetos.append(
                Objetos(nombre=element.objeto.nombre, codigo=element.objeto.codigo, etapa=element.etapa,
                                total_planos_plan=0, total_planos_real=0,
                                total_planos_vpc_90=0, total_planos_vpc_100=0, total_planos_vpc_ret=0,
                                total_planos_vpc_ret_ant=0))

    for element in result:
        total_planos_plan = 0
        total_planos_real = 0
        total_planos_vpc_90 = 0
        total_planos_vpc_100 = 0
        total_planos_vpc_ret = 0
        total_planos_vpc_ret_ant = 0
        val = ''
        inicio = datetime.datetime.strptime(fecha_inic, "%Y-%m-%d").date()
        fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        fecha_pago = datetime.datetime.strptime(str(element.fecha_pago), "%Y-%m-%d").date()
        plano_fecha_ini = datetime.datetime.strptime(str(element.fecha_ini), "%Y-%m-%d").date()
        plano_fecha_fin = datetime.datetime.strptime(str(element.fecha_fin), "%Y-%m-%d").date()
        if element.fecha_vpc is not None:
            fecha_vpc = datetime.datetime.strptime(str(element.fecha_vpc), "%Y-%m-%d").date()
            if inicio <= fecha_pago <= fin and inicio <= fecha_vpc <= fin:
                val = 0  # el caso 0 es para cuando se paga el plano 100 %
                total_planos_real = 1
                total_planos_vpc_100 = 1
                if inicio <= plano_fecha_fin <= fin:
                   total_planos_plan = 1

            if (fecha_pago < inicio or fecha_pago > fin) and inicio <= fecha_vpc <= fin:
                val = 1  # el caso 1 es para cuando se paga el plano 20 %
                total_planos_vpc_ret_ant = 1
            if inicio <= fecha_pago <= fin and (fecha_vpc < inicio or fecha_vpc > fin):
                val = 2  # el caso 2 es para cuando se paga el plano 80 %
                total_planos_real = 1
                total_planos_vpc_90 = 1
                if inicio <= plano_fecha_fin <= fin:
                   total_planos_plan = 1

        else:
            if inicio <= fecha_pago <= fin:
                val = 2  # el caso 2 es para cuando se paga el plano 80 %
                total_planos_real = 1
                total_planos_vpc_90 = 1
                if inicio <= plano_fecha_fin <= fin:
                   total_planos_plan = 1

        for objeto in objetos:
            if objeto.codigo == element.objeto.codigo and objeto.etapa == element.etapa:
                objeto.total_planos_plan += total_planos_plan
                objeto.total_planos_real += total_planos_real
                objeto.total_planos_vpc_90 += total_planos_vpc_90
                objeto.total_planos_vpc_100 += total_planos_vpc_100
                objeto.total_planos_vpc_ret += total_planos_vpc_ret
                objeto.total_planos_vpc_ret_ant += total_planos_vpc_ret_ant

    for etapa in etapas:
        for objeto in objetos:
            if objeto.etapa == etapa.nombre:
                etapa.objetos.append(objeto)
                etapa.total_planos_plan += objeto.total_planos_plan
                etapa.total_planos_real += objeto.total_planos_real
                etapa.total_planos_vpc_90 += objeto.total_planos_vpc_90
                etapa.total_planos_vpc_100 += objeto.total_planos_vpc_100
                etapa.total_planos_vpc_ret += objeto.total_planos_vpc_ret
                etapa.total_planos_vpc_ret_ant += objeto.total_planos_vpc_ret_ant

    total_planos_plan = 0
    total_planos_real = 0
    total_planos_vpc_90 = 0
    total_planos_vpc_100 = 0
    total_planos_vpc_ret = 0
    total_planos_vpc_ret_ant = 0
    for etapa in etapas:
        total_planos_plan += etapa.total_planos_plan
        total_planos_real += etapa.total_planos_real
        total_planos_vpc_90 += etapa.total_planos_vpc_90
        total_planos_vpc_100 += etapa.total_planos_vpc_100
        total_planos_vpc_ret += etapa.total_planos_vpc_ret
        total_planos_vpc_ret_ant += etapa.total_planos_vpc_ret_ant

    completo = Plano.objects.all().filter(fecha_vpc__range=(fecha_inic, fecha_fin),
                                          fecha_pago__range=(fecha_inic, fecha_fin), obra=obra).count()
    retenido = Plano.objects.all().filter(fecha_vpc__range=(fecha_inic, fecha_fin), obra=obra).count() - completo

    return {'etapas': etapas, 'fecha_inic': fecha_inic, 'fecha_fin': fecha_fin, 'obras': obras,
            'completo': completo, 'retenido': retenido, 'total_planos_plan': total_planos_plan,
            'total_planos_real': total_planos_real, 'total_planos_vpc_90': total_planos_vpc_90,
            'total_planos_vpc_100': total_planos_vpc_100, 'total_planos_vpc_ret': total_planos_vpc_ret,
            'total_planos_vpc_ret_ant': total_planos_vpc_ret_ant}

def request_report_certifico(fecha_ini, fecha_fin, obra):
    corte = Plano.objects.filter(corte__isnull=False, obra=obra).order_by('fecha_pago').values('corte').distinct()
    cortes = []
    diccionario = {'01': 'Enero', '02': 'Febrero', '03': 'Marzo', '04': 'Abril', '05': 'Mayo', '06': 'Junio',
                   '07': 'Julio', '08': 'Agosto', '09': 'Septiembre', '10': 'Octubre', '11': 'Noviembre',
                   '12': 'Diciembre'}
    for element in corte:
        flag = False
        var1 = element['corte']
        var_corte = var1[0:11]
        for i in cortes:
            if i.nombre == var_corte:
                flag = True
                break
        if not flag:
            descrip = var1[0:2] + ' de ' + diccionario[var1[3:5]] + ' al ' + var1[6:8] + ' de ' + diccionario[
                var1[9:11]]
            total = Plano.objects.all().filter(corte__contains=var_corte, obra=obra).count()
            vpc = Plano.objects.all().filter(vpc='Si', corte__contains=var_corte, obra=obra,
                                             fecha_vpc__lte=fecha_fin).count()
            pendientes = total - vpc
            vpc_mes = Plano.objects.all().filter(vpc='Si', corte__contains=var_corte, obra=obra,
                                                 fecha_vpc__range=(fecha_ini, fecha_fin)).count()
            cortes.append(Corte(nombre=var_corte, descripcion=descrip, especialidades=[], total=total,
                                pendiente=pendientes, vpc_mes=vpc_mes))

    for corte in cortes:
        corte_esp = Plano.objects.filter(corte__icontains=corte.nombre, obra=obra).values('especialidad').distinct()
        for i in corte_esp:
            flag = False
            temp = Especialidad.objects.get(id=i['especialidad'])
            for esp in corte.especialidades:
                if esp.sigla == temp.siglas:
                    flag = True
                    break
            if not flag:
                total = Plano.objects.all().filter(corte__contains=corte.nombre, obra=obra,
                                                   especialidad__siglas=temp.siglas).count()
                vpc = Plano.objects.all().filter(vpc='Si', corte__contains=corte.nombre, obra=obra,
                                                 fecha_vpc__lte=fecha_fin, especialidad__siglas=temp.siglas).count()
                pendientes = total - vpc
                vpc_mes = Plano.objects.all().filter(vpc='Si', corte__contains=corte.nombre, obra=obra,
                                                     fecha_vpc__range=(fecha_ini, fecha_fin),
                                                     especialidad__siglas=temp.siglas).count()
                corte.especialidades.append(
                    Especial(nombre_esp=temp.nombre, sigla=temp.siglas, planos_vpc=[], total=total,
                             vpc=vpc_mes, pendiente=pendientes))

    for corte in cortes:
        for esp in corte.especialidades:
            listado_planos_vpc = Plano.objects.all().filter(vpc='Si', corte__contains=corte.nombre, obra=obra,
                                                            fecha_vpc__range=(fecha_ini, fecha_fin),
                                                            especialidad__siglas=esp.sigla).select_related(
                "actividad").select_related("objeto").select_related(
                "formato").select_related("obra").select_related("especialidad").select_related("trabajador").order_by(
                'fecha_vpc')
            for plano in listado_planos_vpc:
                esp.planos_vpc.append(plano)
    return cortes


def request_report_pren(fecha_inic, fecha_fin, obra, request):
    sql = """
        SELECT
            ges_trab_trabajador.primer_nombre,
            ges_trab_trabajador.segundo_nombre,
            prenomina15_plano.fecha_vpc,
            ges_trab_trabajador.apellidos,
            adm_escalasalarial.grupo,
            prenomina15_salariomax.sal,
            prenomina15_plano.id,
            prenomina15_plano.formato_id,
            prenomina15_plano.porciento,
            prenomina15_plano.tipo_doc,
            prenomina15_plano.tarifa,
            prenomina15_plano.cant,
            entrada_datos_actividad.codigo_act,
            prenomina15_plano.horas_creadas,
            prenomina15_plano.valor,
            prenomina15_plano.valor_total,
            prenomina15_plano.valor_retenido,
            prenomina15_plano.nombre,
            prenomina15_plano.num,
            prenomina15_objeto.codigo,
            prenomina15_plano.last_rev,
            prenomina15_plano.fecha_pago,
            prenomina15_especialidad.nombre AS nombre_esp,
            prenomina15_plano.trabajador_id,
            prenomina15_plano.id,
            prenomina15_objeto.nombre AS nombre_obj,
            prenomina15_plano.corte,
            prenomina15_plano.horas_creadas_real,
            prenomina15_plano.valor_real,
            prenomina15_plano.valor_retenido_real,
            prenomina15_plano.valor_total_real,
            prenomina15_plano.vpc,
            prenomina15_plano.incumplimiento_plano,
            prenomina15_plano.incumplimiento_cpl,
            prenomina15_plano.incumplimiento_calidad,
            prenomina15_plano.incumplimiento_plano_valor,
            prenomina15_plano.incumplimiento_cpl_valor,
            prenomina15_plano.incumplimiento_calidad_valor,
            prenomina15_plano.valor_pen,
            ges_trab_trabajador.departamento_id,
            adm_departamento.nombre AS nombre_dpto,
            adm_departamento.codigo,
            ges_trab_trabajador.codigo_interno,
            ges_trab_trabajador.ci,
            ges_trab_trabajador.categoria,
            ges_trab_trabajador.cargo_id,
            ges_trab_trabajador.salario_escala,
            ges_trab_trabajador.cies,
            ges_trab_trabajador.incre_res,
            adm_cargo.nombre AS nombre_cargo,
            ges_trab_trabajador.sal_cat_cient,
            ges_trab_trabajador.antiguedad,
            ges_trab_trabajador.salario_total,
            prenomina15_especialidad.siglas
        FROM
            ges_trab_trabajador,
            prenomina15_plano,
            adm_cargo,
            adm_escalasalarial,
            prenomina15_salariomax,
            prenomina15_obra,
            prenomina15_formato,
            entrada_datos_actividad,
            prenomina15_objeto,
            prenomina15_especialidad,
            adm_departamento
        WHERE
            ges_trab_trabajador.id = prenomina15_plano.trabajador_id AND
            prenomina15_salariomax.grupo_esc_id = adm_escalasalarial.id AND
            ges_trab_trabajador.cargo_id = adm_cargo.id AND
            adm_escalasalarial.id = ges_trab_trabajador.escala_salarial_id AND
            adm_departamento.id = ges_trab_trabajador.departamento_id AND
            prenomina15_plano.obra_id = '{}' AND
            prenomina15_obra.tipo = prenomina15_salariomax.tipo AND
            prenomina15_formato.id = prenomina15_plano.formato_id AND
            entrada_datos_actividad.id = prenomina15_plano.actividad_id AND
            prenomina15_objeto.id = prenomina15_plano.objeto_id AND
            prenomina15_plano.especialidad_id = prenomina15_especialidad.id AND
            (prenomina15_plano.fecha_pago BETWEEN '{}'::DATE AND '{}'::DATE
            OR prenomina15_plano.fecha_vpc BETWEEN '{}'::DATE AND '{}'::DATE)
        GROUP BY
            prenomina15_especialidad.siglas, prenomina15_plano.vpc,adm_departamento.codigo,
            ges_trab_trabajador.departamento_id, nombre_dpto, prenomina15_especialidad.nombre,
            ges_trab_trabajador.primer_nombre,
            ges_trab_trabajador.segundo_nombre, ges_trab_trabajador.apellidos,
            ges_trab_trabajador.categoria, ges_trab_trabajador.cargo_id,
            adm_escalasalarial.grupo, prenomina15_salariomax.sal,
            prenomina15_formato.id, ges_trab_trabajador.ci, adm_cargo.nombre,prenomina15_plano.id,
            prenomina15_plano.porciento, prenomina15_plano.tipo_doc, prenomina15_plano.tarifa,
            entrada_datos_actividad.codigo_act, ges_trab_trabajador.cies,
            prenomina15_plano.horas_creadas, prenomina15_plano.valor,
            prenomina15_plano.valor_total, ges_trab_trabajador.salario_escala,
            prenomina15_plano.valor_retenido, prenomina15_plano.nombre,
            prenomina15_plano.num, ges_trab_trabajador.codigo_interno,
            prenomina15_objeto.codigo, prenomina15_plano.last_rev,
            prenomina15_plano.fecha_pago, prenomina15_plano.fecha_vpc,
            ges_trab_trabajador.cies, ges_trab_trabajador.incre_res,
            ges_trab_trabajador.sal_cat_cient, ges_trab_trabajador.antiguedad,
            prenomina15_plano.trabajador_id, prenomina15_plano.id,
            prenomina15_objeto.nombre,
            prenomina15_plano.corte,
            prenomina15_plano.incumplimiento_plano,
            prenomina15_plano.incumplimiento_cpl,
            prenomina15_plano.incumplimiento_calidad,
            prenomina15_plano.incumplimiento_plano_valor,
            prenomina15_plano.incumplimiento_cpl_valor,
            prenomina15_plano.incumplimiento_calidad_valor,
            prenomina15_plano.valor_pen,
            ges_trab_trabajador.salario_total,
            prenomina15_plano.horas_creadas_real,
            prenomina15_plano.valor_real,
            prenomina15_plano.valor_retenido_real,
            prenomina15_plano.valor_total_real
        ORDER BY
            adm_departamento.codigo,
            adm_escalasalarial.grupo DESC,
            prenomina15_especialidad.nombre,
            ges_trab_trabajador.primer_nombre,
            ges_trab_trabajador.segundo_nombre,
            ges_trab_trabajador.apellidos,
            prenomina15_plano.num;
        """.format(obra, fecha_inic, fecha_fin, fecha_inic, fecha_fin)

    obras = listar_obra(request)
    result = Plano.objects.raw(sql)
    areas = []
    personas = []
    planos = []
    for element in result:
        flag = False
        for area in areas:
            if area.codigo == element.codigo:
                flag = True
                break
        if not flag:
            areas.append(Area(nombre=element.nombre_dpto, codigo=element.codigo, personas=[], cant=0,
                              horas_creadas_total=0, setrt=0, inc_res_30=0, cies=0, ant=0, maest=0,
                              total_dev_30=0, cant_planos=0, total_horas=0, sal_res15=0, sal_res15_plano=0,
                              ret=0, ret_ant=0, impacto=0, sal_tot_dev=0, incumplimiento_plano_valor=0,
                              incumplimiento_cpl_valor=0, incumplimiento_calidad_valor=0, valor_pen=0))

    no_loop = 0
    for element in result:
        flag = False
        for per in personas:
            if per.no == element.codigo_interno:
                if per.dpto == element.codigo:
                    flag = True
                break
        if not flag:
            no_loop += 1
            tarifa_se = (element.salario_escala / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                            rounding=ROUND_HALF_UP)
            tarifa_pa = (element.incre_res / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                       rounding=ROUND_HALF_UP)
            if element.antiguedad != 0.00:
                tarifa_ant = (element.antiguedad / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                             rounding=ROUND_HALF_UP)
            else:
                tarifa_ant = Decimal(0.00)
            tarifa_cies = (element.cies / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                    rounding=ROUND_HALF_UP)
            if element.sal_cat_cient != 0.00:
                tarifa_maest = (element.sal_cat_cient / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                                  rounding=ROUND_HALF_UP)
            else:
                tarifa_maest = Decimal(0.00)
            personas.append(
                Trab(no=element.codigo_interno, trab_id=element.trabajador_id,
                     nombre=element.primer_nombre + ' ' + element.segundo_nombre + ' ' + element.apellidos,
                     planos=[], ge=element.grupo, sal_max=element.sal, categoria=element.categoria,
                     tarifa=element.tarifa, total_horas=0, total_pagar=0, total_retenido=0, total_valor=0,
                     cant=0, dpto=element.codigo, retenido_ant=0, pagar=0, ci=element.ci,
                     sal_escala=element.salario_escala, cies=element.cies, incre_res=element.incre_res,
                     antig=element.antiguedad, maestria=element.sal_cat_cient, tarifa_se=tarifa_se,
                     tarifa_pa=tarifa_pa, tarifa_ant=tarifa_ant, tarifa_cies=tarifa_cies,
                     tarifa_maest=tarifa_maest, salario_total=element.salario_total, se_real=0.00,
                     pa_real=0.00, cies_real=0.00, ant_real=0.00, maest_real=0.00, total_dev=0.00, impacto=0.00,
                     sal_dev_total=0.00, cargo=element.nombre_cargo, incumplimiento_plano=0, incumplimiento_cpl=0,
                     incumplimiento_calidad=0, incumplimiento_plano_valor=0, incumplimiento_cpl_valor=0,
                     incumplimiento_calidad_valor=0, total_valor_pen=0, sal_res15=0, no_loop=no_loop))
    for element in result:
        val = ''
        pagar = ''
        retenido = 0
        pago_ant = 0
        horas_creadas = 0
        valor_retenido_real = 0
        valor_total_real = 0
        horas_creadas_real = 0
        list_cant = []
        catalogo = []
        cantidad = element.cant - 1
        inicio = datetime.datetime.strptime(fecha_inic, "%Y-%m-%d").date()
        fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        fecha_pago = datetime.datetime.strptime(str(element.fecha_pago), "%Y-%m-%d").date()
        if element.fecha_vpc is not None:
            fecha_vpc = datetime.datetime.strptime(str(element.fecha_vpc), "%Y-%m-%d").date()
            if inicio <= fecha_pago <= fin and inicio <= fecha_vpc <= fin:
                val = 0  # el caso 0 es para cuando se paga el plano 100 %
                horas_creadas = element.horas_creadas
                pagar = element.valor_real
                horas_creadas_real = element.horas_creadas_real
            if (fecha_pago < inicio or fecha_pago > fin) and inicio <= fecha_vpc <= fin:
                val = 1  # el caso 1 es para cuando se paga el plano 20 %
                pagar = 0
                pago_ant = element.valor_retenido
                valor_retenido_real = element.valor_retenido_real
                horas_creadas = 0
            if inicio <= fecha_pago <= fin and (fecha_vpc < inicio or fecha_vpc > fin):
                val = 2  # el caso 2 es para cuando se paga el plano 80 %
                pagar = element.valor_total_real
                valor_total_real = element.valor_total_real
                retenido = element.valor_retenido
                valor_retenido_real = element.valor_retenido_real
                horas_creadas = element.horas_creadas
                horas_creadas_real = element.horas_creadas_real
        else:
            if inicio <= fecha_pago <= fin:
                val = 2  # el caso 2 es para cuando se paga el plano 80 %
                pagar = element.valor_total_real
                valor_total_real = element.valor_total_real
                retenido = element.valor_retenido
                valor_retenido_real = element.valor_retenido_real
                horas_creadas = element.horas_creadas
                horas_creadas_real = element.horas_creadas_real
        while cantidad != 0:
            list_cant.append(1)
            cantidad -= 1
        if element.cant != 1:
            catalogos = Catalogo.objects.all().filter(plano_id=element.id)
            for cat in catalogos:
                catalogo.append(Cat(formato=cat.formato, porciento=int(float(cat.porciento) * 100), horas_creadas=cat.horas_creadas,
                                    horas_creadas_real=cat.horas_creadas_real, valor_retenido=cat.valor_retenido,
                                    valor_retenido_real=cat.valor_retenido_real, valor=cat.valor,
                                    valor_real=cat.valor_real, valor_total=cat.valor_total,
                                    valor_total_real=cat.valor_total_real,
                                    incumplimiento_plano=element.incumplimiento_plano,
                                    incumplimiento_plano_valor=cat.incumplimiento_plano_valor,
                                    incumplimiento_cpl=element.incumplimiento_cpl,
                                    incumplimiento_cpl_valor=cat.incumplimiento_cpl_valor,
                                    incumplimiento_calidad=element.incumplimiento_calidad,
                                    incumplimiento_calidad_valor=cat.incumplimiento_calidad_valor,
                                    valor_pen=cat.valor_pen))
        planos.append(
            Plan(nombre=element.nombre, codigo=element.num, objeto=element.codigo, etapa=element.codigo_act,
                 formato=element.formato.formato, porciento=int(float(element.porciento) * 100),
                 horas_creadas=horas_creadas, nombre_obj=element.nombre_obj,
                 valor=element.valor, valor_total=element.valor_total, retenido=retenido, reten_ant=pago_ant,
                 rev=element.last_rev, vpc=element.vpc, trabajador_id=element.trabajador_id,
                 ult_rev=element.last_rev, especialidad=element.nombre_esp, caso=val, pagar=pagar, cant=element.cant,
                 corte=element.corte, horas_creadas_real=horas_creadas_real, valor_real=element.valor_real,
                 valor_retenido_real=valor_retenido_real, valor_total_real=valor_total_real, list_cant=list_cant,
                 tarifa=element.tarifa, sigla=element.siglas, tipo_doc=element.tipo_doc,
                 incumplimiento_plano=element.incumplimiento_plano, incumplimiento_cpl=element.incumplimiento_cpl,
                 incumplimiento_calidad=element.incumplimiento_calidad,
                 incumplimiento_plano_valor=element.incumplimiento_plano_valor,
                 incumplimiento_cpl_valor=element.incumplimiento_cpl_valor,
                 incumplimiento_calidad_valor=element.incumplimiento_calidad_valor,
                 valor_pen=element.valor_pen, catalogo=catalogo))
    for per in personas:
        for plano in planos:
            if plano.trabajador_id == per.trab_id:
                per.planos.append(plano)
                if plano.caso != 1:
                    per.cant += 1
                    per.total_valor += plano.valor_real
                    per.sal_res15 += plano.valor

                per.total_horas += plano.horas_creadas
                per.total_retenido += plano.retenido
                per.pagar += plano.pagar
                if plano.caso == 1:
                    per.retenido_ant += plano.reten_ant
                per.incumplimiento_plano = plano.incumplimiento_plano
                per.incumplimiento_cpl = plano.incumplimiento_cpl
                per.incumplimiento_calidad = plano.incumplimiento_calidad
                per.incumplimiento_plano_valor += plano.incumplimiento_plano_valor
                per.incumplimiento_cpl_valor += plano.incumplimiento_cpl_valor
                per.incumplimiento_calidad_valor += plano.incumplimiento_calidad_valor
                per.total_valor_pen += plano.valor_pen
                if plano.cant != 1:
                    for c in plano.catalogo:
                        if plano.caso == 0:
                            per.total_valor += c.valor_real
                            per.total_horas += c.horas_creadas
                            per.pagar += c.valor
                            per.sal_res15 += c.valor
                        if plano.caso == 1:
                            per.total_retenido += c.valor_retenido
                            per.retenido_ant += c.valor_retenido
                            per.pagar += plano.pagar
                            per.total_horas += plano.horas_creadas
                        if plano.caso == 2:
                            per.total_valor += c.valor_real
                            per.total_horas += c.horas_creadas
                            per.total_retenido += c.valor_retenido
                            per.pagar += c.valor_total
                            per.sal_res15 += c.valor
                        per.incumplimiento_plano = plano.incumplimiento_plano
                        per.incumplimiento_cpl = plano.incumplimiento_cpl
                        per.incumplimiento_calidad = plano.incumplimiento_calidad
                        per.incumplimiento_plano_valor += c.incumplimiento_plano_valor
                        per.incumplimiento_cpl_valor += c.incumplimiento_cpl_valor
                        per.incumplimiento_calidad_valor += c.incumplimiento_calidad_valor
                        per.total_valor_pen += c.valor_pen
    total_planos = 0
    for area in areas:
        for per in personas:
            if per.dpto == area.codigo:
                area.personas.append(per)
                area.cant += per.cant
        total_planos += area.cant
    completo = Plano.objects.all().filter(fecha_vpc__range=(fecha_inic, fecha_fin),
                                          fecha_pago__range=(fecha_inic, fecha_fin), obra=obra).count()
    retenido = Plano.objects.all().filter(fecha_vpc__range=(fecha_inic, fecha_fin), obra=obra).count() - completo
    for area in areas:
        for per in area.personas:
            per.se_real = Decimal(per.tarifa_se * per.total_horas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.pa_real = Decimal(per.tarifa_pa * per.total_horas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.cies_real = Decimal(per.tarifa_cies * per.total_horas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.ant_real = Decimal(per.tarifa_ant * per.total_horas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.maest_real = Decimal(Decimal(per.tarifa_maest) * per.total_horas).quantize(Decimal('.01'),
                                                                                           rounding=ROUND_HALF_UP)
            per.total_dev = per.se_real + per.pa_real + per.cies_real + per.maest_real + per.ant_real
            per.impacto = (per.sal_res15 - per.total_dev - per.total_retenido) + per.retenido_ant
            per.sal_dev_total = per.impacto + per.total_dev
            area.horas_creadas_total += per.total_horas
            area.setrt += per.se_real
            area.inc_res_30 += per.pa_real
            area.cies += per.cies_real
            area.ant += per.ant_real
            area.maest += per.maest_real
            area.total_dev_30 += per.total_dev
            area.cant_planos += per.cant
            area.total_horas += per.total_horas
            area.sal_res15_plano += per.total_valor
            area.sal_res15 += per.sal_res15
            area.ret += per.total_retenido
            area.ret_ant += per.retenido_ant
            area.impacto += per.impacto
            area.sal_total_dev += per.sal_dev_total
            area.incumplimiento_plano_valor += per.incumplimiento_plano_valor
            area.incumplimiento_cpl_valor += per.incumplimiento_cpl_valor
            area.incumplimiento_calidad_valor += per.incumplimiento_calidad_valor
            area.valor_pen += per.total_valor_pen
    horas = 0
    setrt = 0
    inc_res_30 = 0
    cies = 0
    ant = 0
    maest = 0
    total_dev_30 = 0
    cant_planos = 0
    sal_res15_plano = 0
    sal_res15 = 0
    inc_plano = 0
    inc_cpl = 0
    inc_calidad = 0
    ret = 0
    ret_ant = 0
    impacto = 0
    sal_total_dev = 0
    for area in areas:
        horas += area.horas_creadas_total
        setrt += area.setrt
        inc_res_30 += area.inc_res_30
        cies += area.cies
        ant += area.ant
        maest += area.maest
        total_dev_30 += area.total_dev_30
        cant_planos += area.cant_planos
        sal_res15_plano += area.sal_res15_plano
        inc_plano += area.incumplimiento_plano_valor
        inc_cpl += area.incumplimiento_cpl_valor
        inc_calidad += area.incumplimiento_calidad_valor
        sal_res15 += area.sal_res15
        ret += area.ret
        ret_ant += area.ret_ant
        impacto += area.impacto
        sal_total_dev += area.sal_total_dev
    return {'areas': areas, 'fecha_inic': fecha_inic, 'fecha_fin': fecha_fin, 'obras': obras,
            'total_planos': total_planos, 'completo': completo, 'retenido': retenido, 'horas': horas, 'setrt': setrt,
            'inc_res_30': inc_res_30, 'cies': cies, 'ant': ant, 'maest': maest, 'total_dev_30': total_dev_30,
            'cant_planos': cant_planos, 'sal_res15_plano': sal_res15_plano, 'ret': ret, 'ret_ant': ret_ant,
            'impacto': impacto, 'sal_total_dev': sal_total_dev, 'sal_res15': sal_res15, 'inc_plano': inc_plano,
            'inc_cpl': inc_cpl, 'inc_calidad': inc_calidad}



def request_report_pren_trab(fecha_inic, fecha_fin, request):
    sql = """
        SELECT
            ges_trab_trabajador.primer_nombre,
            ges_trab_trabajador.segundo_nombre,
            prenomina15_plano.fecha_vpc,
            ges_trab_trabajador.apellidos,
            adm_escalasalarial.grupo,
            prenomina15_salariomax.sal,
            prenomina15_plano.id,
            prenomina15_plano.obra_id,
            prenomina15_plano.formato_id,
            prenomina15_plano.porciento,
            prenomina15_plano.tipo_doc,
            prenomina15_plano.tarifa,
            prenomina15_plano.cant,
            entrada_datos_actividad.codigo_act,
            prenomina15_plano.horas_creadas,
            prenomina15_plano.valor,
            prenomina15_plano.valor_total,
            prenomina15_plano.valor_retenido,
            prenomina15_plano.nombre,
            prenomina15_plano.num,
            prenomina15_objeto.codigo,
            prenomina15_plano.last_rev,
            prenomina15_plano.fecha_pago,
            prenomina15_especialidad.nombre AS nombre_esp,
            prenomina15_plano.trabajador_id,
            prenomina15_plano.id,
            prenomina15_objeto.nombre AS nombre_obj,
            prenomina15_plano.corte,
            prenomina15_plano.horas_creadas_real,
            prenomina15_plano.valor_real,
            prenomina15_plano.valor_retenido_real,
            prenomina15_plano.valor_total_real,
            prenomina15_plano.vpc,
            prenomina15_plano.incumplimiento_plano,
            prenomina15_plano.incumplimiento_cpl,
            prenomina15_plano.incumplimiento_calidad,
            prenomina15_plano.incumplimiento_plano_valor,
            prenomina15_plano.incumplimiento_cpl_valor,
            prenomina15_plano.incumplimiento_calidad_valor,
            prenomina15_plano.valor_pen,
            ges_trab_trabajador.departamento_id,
            adm_departamento.nombre AS nombre_dpto,
            adm_departamento.codigo,
            ges_trab_trabajador.codigo_interno,
            ges_trab_trabajador.ci,
            ges_trab_trabajador.categoria,
            ges_trab_trabajador.cargo_id,
            ges_trab_trabajador.salario_escala,
            ges_trab_trabajador.cies,
            ges_trab_trabajador.incre_res,
            adm_cargo.nombre AS nombre_cargo,
            ges_trab_trabajador.sal_cat_cient,
            ges_trab_trabajador.antiguedad,
            ges_trab_trabajador.salario_total,
            prenomina15_especialidad.siglas
        FROM
            ges_trab_trabajador,
            prenomina15_plano,
            adm_cargo,
            adm_escalasalarial,
            prenomina15_salariomax,
            prenomina15_obra,
            prenomina15_formato,
            entrada_datos_actividad,
            prenomina15_objeto,
            prenomina15_especialidad,
            adm_departamento
        WHERE
            ges_trab_trabajador.id = prenomina15_plano.trabajador_id AND
            prenomina15_salariomax.grupo_esc_id = adm_escalasalarial.id AND
            ges_trab_trabajador.cargo_id = adm_cargo.id AND
            adm_escalasalarial.id = ges_trab_trabajador.escala_salarial_id AND
            adm_departamento.id = ges_trab_trabajador.departamento_id AND
            prenomina15_obra.tipo = prenomina15_salariomax.tipo AND
            prenomina15_formato.id = prenomina15_plano.formato_id AND
            entrada_datos_actividad.id = prenomina15_plano.actividad_id AND
            prenomina15_objeto.id = prenomina15_plano.objeto_id AND
            prenomina15_plano.especialidad_id = prenomina15_especialidad.id AND
            (prenomina15_plano.fecha_pago BETWEEN '{}'::DATE AND '{}'::DATE
            OR prenomina15_plano.fecha_vpc BETWEEN '{}'::DATE AND '{}'::DATE)
        GROUP BY
            prenomina15_especialidad.siglas, prenomina15_plano.vpc,adm_departamento.codigo,
            ges_trab_trabajador.departamento_id, nombre_dpto, prenomina15_especialidad.nombre,
            ges_trab_trabajador.primer_nombre,
            ges_trab_trabajador.segundo_nombre, ges_trab_trabajador.apellidos,
            ges_trab_trabajador.categoria, ges_trab_trabajador.cargo_id,
            adm_escalasalarial.grupo, prenomina15_salariomax.sal,
            prenomina15_formato.id, ges_trab_trabajador.ci, adm_cargo.nombre,prenomina15_plano.id,
            prenomina15_plano.porciento, prenomina15_plano.tipo_doc, prenomina15_plano.tarifa,
            entrada_datos_actividad.codigo_act, ges_trab_trabajador.cies,
            prenomina15_plano.horas_creadas, prenomina15_plano.valor,
            prenomina15_plano.valor_total, ges_trab_trabajador.salario_escala,
            prenomina15_plano.valor_retenido, prenomina15_plano.nombre,
            prenomina15_plano.num, ges_trab_trabajador.codigo_interno,
            prenomina15_objeto.codigo, prenomina15_plano.last_rev,
            prenomina15_plano.fecha_pago, prenomina15_plano.fecha_vpc,
            ges_trab_trabajador.cies, ges_trab_trabajador.incre_res,
            ges_trab_trabajador.sal_cat_cient, ges_trab_trabajador.antiguedad,
            prenomina15_plano.trabajador_id, prenomina15_plano.id,
            prenomina15_objeto.nombre,
            prenomina15_plano.corte,
            prenomina15_plano.incumplimiento_plano,
            prenomina15_plano.incumplimiento_cpl,
            prenomina15_plano.incumplimiento_calidad,
            prenomina15_plano.incumplimiento_plano_valor,
            prenomina15_plano.incumplimiento_cpl_valor,
            prenomina15_plano.incumplimiento_calidad_valor,
            prenomina15_plano.valor_pen,
            ges_trab_trabajador.salario_total,
            prenomina15_plano.horas_creadas_real,
            prenomina15_plano.valor_real,
            prenomina15_plano.valor_retenido_real,
            prenomina15_plano.valor_total_real,
            prenomina15_plano.obra_id
        ORDER BY
            adm_departamento.codigo,
            adm_escalasalarial.grupo DESC,
            ges_trab_trabajador.primer_nombre,
            ges_trab_trabajador.segundo_nombre,
            ges_trab_trabajador.apellidos,
            prenomina15_plano.obra_id;
        """.format(fecha_inic, fecha_fin, fecha_inic, fecha_fin)

    obras = listar_obra(request)
    result = Plano.objects.raw(sql)
    areas = []
    personas = []
    planos = []
    obrs = []
    for element in result:
        flag = False
        for area in areas:
            if area.codigo == element.codigo:
                flag = True
                break
        if not flag:
            areas.append(Area(nombre=element.nombre_dpto, codigo=element.codigo, personas=[], cant=0,
                              horas_creadas_total=0, setrt=0, inc_res_30=0, cies=0, ant=0, maest=0,
                              total_dev_30=0, cant_planos=0, total_horas=0, sal_res15=0, sal_res15_plano=0,
                              ret=0, ret_ant=0, impacto=0, sal_tot_dev=0, incumplimiento_plano_valor=0,
                              incumplimiento_cpl_valor=0, incumplimiento_calidad_valor=0, valor_pen=0))
    no_loop = 0
    for element in result:
        flag = False
        for per in personas:
            if per.no == element.codigo_interno:
                if per.dpto == element.codigo:
                    flag = True
                break
        if not flag:
            no_loop += 1
            tarifa_se = (element.salario_escala / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                            rounding=ROUND_HALF_UP)
            tarifa_pa = (element.incre_res / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                       rounding=ROUND_HALF_UP)
            if element.antiguedad != 0.00:
                tarifa_ant = (element.antiguedad / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                             rounding=ROUND_HALF_UP)
            else:
                tarifa_ant = Decimal(0.00)
            tarifa_cies = (element.cies / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                    rounding=ROUND_HALF_UP)
            if element.sal_cat_cient != 0.00:
                tarifa_maest = (element.sal_cat_cient / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                                  rounding=ROUND_HALF_UP)
            else:
                tarifa_maest = Decimal(0.00)
            personas.append(
                Trab(no=element.codigo_interno, trab_id=element.trabajador_id,
                     nombre=element.primer_nombre + ' ' + element.segundo_nombre + ' ' + element.apellidos,
                     obras=[], planos=[], ge=element.grupo, sal_max=element.sal, categoria=element.categoria,
                     tarifa=element.tarifa, total_horas=0, total_pagar=0, total_retenido=0, total_valor=0,
                     cant=0, dpto=element.codigo, retenido_ant=0, pagar=0, ci=element.ci,
                     sal_escala=element.salario_escala, cies=element.cies, incre_res=element.incre_res,
                     antig=element.antiguedad, maestria=element.sal_cat_cient, tarifa_se=tarifa_se,
                     tarifa_pa=tarifa_pa, tarifa_ant=tarifa_ant, tarifa_cies=tarifa_cies,
                     tarifa_maest=tarifa_maest, salario_total=element.salario_total, se_real=0.00,
                     pa_real=0.00, cies_real=0.00, ant_real=0.00, maest_real=0.00, total_dev=0.00, impacto=0.00,
                     sal_dev_total=0.00, cargo=element.nombre_cargo, incumplimiento_plano=0, incumplimiento_cpl=0,
                     incumplimiento_calidad=0, incumplimiento_plano_valor=0, incumplimiento_cpl_valor=0,
                     incumplimiento_calidad_valor=0, total_valor_pen=0, sal_res15=0, no_loop=no_loop))

    for element in result:
        val = ''
        pagar = ''
        retenido = 0
        pago_ant = 0
        horas_creadas = 0
        valor_retenido_real = 0
        valor_total_real = 0
        horas_creadas_real = 0
        list_cant = []
        catalogo = []
        cantidad = element.cant - 1
        inicio = datetime.datetime.strptime(fecha_inic, "%Y-%m-%d").date()
        fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        fecha_pago = datetime.datetime.strptime(str(element.fecha_pago), "%Y-%m-%d").date()
        if element.fecha_vpc is not None:
            fecha_vpc = datetime.datetime.strptime(str(element.fecha_vpc), "%Y-%m-%d").date()
            if inicio <= fecha_pago <= fin and inicio <= fecha_vpc <= fin:
                val = 0  # el caso 0 es para cuando se paga el plano 100 %
                horas_creadas = element.horas_creadas
                pagar = element.valor_real
                horas_creadas_real = element.horas_creadas_real
            if (fecha_pago < inicio or fecha_pago > fin) and inicio <= fecha_vpc <= fin:
                val = 1  # el caso 1 es para cuando se paga el plano 20 %
                pagar = 0
                pago_ant = element.valor_retenido
                valor_retenido_real = element.valor_retenido_real
                horas_creadas = 0
            if inicio <= fecha_pago <= fin and (fecha_vpc < inicio or fecha_vpc > fin):
                val = 2  # el caso 2 es para cuando se paga el plano 80 %
                pagar = element.valor_total_real
                valor_total_real = element.valor_total_real
                retenido = element.valor_retenido
                valor_retenido_real = element.valor_retenido_real
                horas_creadas = element.horas_creadas
                horas_creadas_real = element.horas_creadas_real
        else:
            if inicio <= fecha_pago <= fin:
                val = 2  # el caso 2 es para cuando se paga el plano 80 %
                pagar = element.valor_total_real
                valor_total_real = element.valor_total_real
                retenido = element.valor_retenido
                valor_retenido_real = element.valor_retenido_real
                horas_creadas = element.horas_creadas
                horas_creadas_real = element.horas_creadas_real
        while cantidad != 0:
            list_cant.append(1)
            cantidad -= 1
        if element.cant != 1:
            catalogos = Catalogo.objects.all().filter(plano_id=element.id)
            for cat in catalogos:
                catalogo.append(
                    Cat(formato=cat.formato, porciento=int(float(cat.porciento) * 100), horas_creadas=cat.horas_creadas,
                        horas_creadas_real=cat.horas_creadas_real, valor_retenido=cat.valor_retenido,
                        valor_retenido_real=cat.valor_retenido_real, valor=cat.valor,
                        valor_real=cat.valor_real, valor_total=cat.valor_total,
                        valor_total_real=cat.valor_total_real,
                        incumplimiento_plano=element.incumplimiento_plano,
                        incumplimiento_plano_valor=cat.incumplimiento_plano_valor,
                        incumplimiento_cpl=element.incumplimiento_cpl,
                        incumplimiento_cpl_valor=cat.incumplimiento_cpl_valor,
                        incumplimiento_calidad=element.incumplimiento_calidad,
                        incumplimiento_calidad_valor=cat.incumplimiento_calidad_valor,
                        valor_pen=cat.valor_pen))
        planos.append(
            Plan(nombre=element.nombre, codigo=element.num, objeto=element.codigo, etapa=element.codigo_act,
                 formato=element.formato.formato, porciento=int(float(element.porciento) * 100),
                 horas_creadas=horas_creadas, nombre_obj=element.nombre_obj,
                 valor=element.valor, valor_total=element.valor_total, retenido=retenido, reten_ant=pago_ant,
                 rev=element.last_rev, vpc=element.vpc, trabajador_id=element.trabajador_id,
                 ult_rev=element.last_rev, especialidad=element.nombre_esp, caso=val, pagar=pagar, cant=element.cant,
                 corte=element.corte, horas_creadas_real=horas_creadas_real, valor_real=element.valor_real,
                 valor_retenido_real=valor_retenido_real, valor_total_real=valor_total_real, list_cant=list_cant,
                 tarifa=element.tarifa, sigla=element.siglas, tipo_doc=element.tipo_doc,
                 incumplimiento_plano=element.incumplimiento_plano, incumplimiento_cpl=element.incumplimiento_cpl,
                 incumplimiento_calidad=element.incumplimiento_calidad,
                 incumplimiento_plano_valor=element.incumplimiento_plano_valor,
                 incumplimiento_cpl_valor=element.incumplimiento_cpl_valor,
                 incumplimiento_calidad_valor=element.incumplimiento_calidad_valor,
                 valor_pen=element.valor_pen, catalogo=catalogo, obra=element.obra))

    for per in personas:
        for plano in planos:
            if plano.trabajador_id == per.trab_id:
                flag = False
                for obr in per.obras:
                    if plano.obra.id == obr.id_obra:
                        flag = True
                        obr.horas_creadas += plano.horas_creadas
                        if plano.caso != 1:
                            obr.sal_res15 += plano.valor
                        if plano.caso == 2:
                            obr.retenido += plano.retenido
                        if plano.caso == 0:
                            obr.valor_total += plano.valor_real
                        if plano.caso == 1:
                            obr.retenido_ant += plano.reten_ant
                        if plano.cant != 1:
                            for c in plano.catalogo:
                                if plano.caso == 0:
                                    obr.valor_total += c.valor_real
                                    obr.horas_creadas += c.horas_creadas
                                if plano.caso == 1:
                                    obr.retenido += c.retenido
                                    obr.retenido_ant += c.valor_retenido
                                    obr.horas_creadas += plano.horas_creadas
                                if plano.caso == 2:
                                    obr.valor_total += c.valor_real
                                    obr.horas_creadas += c.horas_creadas
                                    obr.retenido += c.valor_retenido
                                if plano.caso != 1:
                                    obr.sal_res15 += c.valor
                        break
                if not flag:
                    o_hc = plano.horas_creadas
                    o_vt = 0
                    s_r15 = 0
                    o_ret = plano.retenido
                    o_ret_ant = 0
                    if plano.caso != 1:
                        s_r15 += plano.valor
                    if plano.caso == 0:
                        o_vt = plano.valor_real
                    if plano.caso == 2:
                        o_ret = plano.retenido
                    if plano.caso == 1:
                        o_ret_ant = plano.reten_ant
                    if plano.cant != 1:
                        for c in plano.catalogo:
                            if plano.caso == 0:
                                o_vt = c.valor_real
                                o_hc += c.horas_creadas
                            if plano.caso == 1:
                                o_ret += c.retenido
                                o_ret_ant += c.valor_retenido
                                o_hc += plano.horas_creadas
                            if plano.caso == 2:
                                o_hc += c.horas_creadas
                                o_ret_ant += c.valor_retenido
                            if plano.caso != 1:
                                s_r15 += c.valor
                    per.obras.append(
                        Obr(id_obra=plano.obra.id, obra=plano.obra.nombre, planos=[], no=0,
                            horas_creadas=o_hc,
                            strt=0, inc_r30=0, cies=0, ant=0, valor_total=o_vt,
                            maest=0, devengado=0, impacto=0, total=0, sal_res15=s_r15, retenido=o_ret, retenido_ant=o_ret_ant))
                per.planos.append(plano)
                if plano.caso != 1:
                    per.cant += 1
                    per.total_valor += plano.valor_real
                    per.sal_res15 += plano.valor

                per.total_horas += plano.horas_creadas
                per.total_retenido += plano.retenido
                per.pagar += plano.pagar
                if plano.caso == 1:
                    per.retenido_ant += plano.reten_ant
                per.incumplimiento_plano = plano.incumplimiento_plano
                per.incumplimiento_cpl = plano.incumplimiento_cpl
                per.incumplimiento_calidad = plano.incumplimiento_calidad
                per.incumplimiento_plano_valor += plano.incumplimiento_plano_valor
                per.incumplimiento_cpl_valor += plano.incumplimiento_cpl_valor
                per.incumplimiento_calidad_valor += plano.incumplimiento_calidad_valor
                per.total_valor_pen += plano.valor_pen

                if plano.cant != 1:
                    for c in plano.catalogo:
                        if plano.caso == 0:
                            per.total_valor += c.valor_real
                            per.total_horas += c.horas_creadas
                            per.pagar += c.valor
                        if plano.caso == 1:
                            per.total_retenido += c.retenido
                            per.retenido_ant += c.valor_retenido
                            per.pagar += plano.pagar
                            per.total_horas += plano.horas_creadas
                        if plano.caso == 2:
                            per.total_valor += c.valor_real
                            per.total_horas += c.horas_creadas
                            per.total_retenido += c.valor_retenido
                            per.pagar += c.valor_total

                        per.incumplimiento_plano = plano.incumplimiento_plano
                        per.incumplimiento_cpl = plano.incumplimiento_cpl
                        per.incumplimiento_calidad = plano.incumplimiento_calidad
                        per.incumplimiento_plano_valor += c.incumplimiento_plano_valor
                        per.incumplimiento_cpl_valor += c.incumplimiento_cpl_valor
                        per.incumplimiento_calidad_valor += c.incumplimiento_calidad_valor
                        per.total_valor_pen += c.valor_pen
                        per.sal_res15 += c.valor

    for per in personas:
        for obr in per.obras:
            obr.strt = Decimal(per.tarifa_se * obr.horas_creadas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            obr.inc_r30 = Decimal(per.tarifa_pa * obr.horas_creadas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            obr.cies = Decimal(Decimal(per.tarifa_cies) * obr.horas_creadas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            obr.ant = Decimal(Decimal(per.tarifa_ant) * obr.horas_creadas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            obr.maest = Decimal(Decimal(per.tarifa_maest) * obr.horas_creadas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            obr.devengado = obr.strt + obr.inc_r30 + obr.cies + obr.ant + obr.maest
            obr.impacto = (obr.sal_res15 - obr.devengado - obr.retenido) + obr.retenido_ant
            obr.total = obr.impacto + obr.devengado


    total_planos = 0
    for area in areas:
        for per in personas:
            if per.dpto == area.codigo:
                area.personas.append(per)
                area.cant += per.cant
        total_planos += area.cant

    completo = Plano.objects.all().filter(fecha_vpc__range=(fecha_inic, fecha_fin),
                                          fecha_pago__range=(fecha_inic, fecha_fin)).count()
    retenido = Plano.objects.all().filter(fecha_vpc__range=(fecha_inic, fecha_fin)).count() - completo

    for area in areas:
        for per in area.personas:
            per.se_real = Decimal(per.tarifa_se * per.total_horas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.pa_real = Decimal(per.tarifa_pa * per.total_horas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.cies_real = Decimal(per.tarifa_cies * per.total_horas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.ant_real = Decimal(per.tarifa_ant * per.total_horas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.maest_real = Decimal(Decimal(per.tarifa_maest) * per.total_horas).quantize(Decimal('.01'),
                                                                                           rounding=ROUND_HALF_UP)
            per.total_dev = per.se_real + per.pa_real + per.cies_real + per.maest_real + per.ant_real
            per.impacto = (per.sal_res15 - per.total_dev - per.total_retenido) + per.retenido_ant
            per.sal_dev_total = per.impacto + per.total_dev
            area.horas_creadas_total += per.total_horas
            area.setrt += per.se_real
            area.inc_res_30 += per.pa_real
            area.cies += per.cies_real
            area.ant += per.ant_real
            area.maest += per.maest_real
            area.total_dev_30 += per.total_dev
            area.cant_planos += per.cant
            area.total_horas += per.total_horas
            area.sal_res15_plano += per.sal_res15
            area.sal_res15 += per.sal_res15
            area.ret += per.total_retenido
            area.ret_ant += per.retenido_ant
            area.impacto += per.impacto
            area.sal_total_dev += per.sal_dev_total
            area.incumplimiento_plano_valor += per.incumplimiento_plano_valor
            area.incumplimiento_cpl_valor += per.incumplimiento_cpl_valor
            area.incumplimiento_calidad_valor += per.incumplimiento_calidad_valor
            area.valor_pen += per.total_valor_pen

    horas = 0
    setrt = 0
    inc_res_30 = 0
    cies = 0
    ant = 0
    maest = 0
    total_dev_30 = 0
    cant_planos = 0
    sal_res15_plano = 0
    sal_res15 = 0
    inc_plano = 0
    inc_cpl = 0
    inc_calidad = 0
    ret = 0
    ret_ant = 0
    impacto = 0
    sal_total_dev = 0
    for area in areas:
        horas += area.horas_creadas_total
        setrt += area.setrt
        inc_res_30 += area.inc_res_30
        cies += area.cies
        ant += area.ant
        maest += area.maest
        total_dev_30 += area.total_dev_30
        cant_planos += area.cant_planos
        sal_res15_plano += area.sal_res15_plano
        inc_plano += area.incumplimiento_plano_valor
        inc_cpl += area.incumplimiento_cpl_valor
        inc_calidad += area.incumplimiento_calidad_valor
        sal_res15 += area.sal_res15
        ret += area.ret
        ret_ant += area.ret_ant
        impacto += area.impacto
        sal_total_dev += area.sal_total_dev

    return {'areas': areas, 'fecha_inic': fecha_inic, 'fecha_fin': fecha_fin, 'obras': obras,
            'total_planos': total_planos, 'completo': completo, 'retenido': retenido, 'horas': horas, 'setrt': setrt,
            'inc_res_30': inc_res_30, 'cies': cies, 'ant': ant, 'maest': maest, 'total_dev_30': total_dev_30,
            'cant_planos': cant_planos, 'sal_res15_plano': sal_res15_plano, 'ret': ret, 'ret_ant': ret_ant,
            'impacto': impacto, 'sal_total_dev': sal_total_dev, 'sal_res15': sal_res15, 'inc_plano': inc_plano,
            'inc_cpl': inc_cpl, 'inc_calidad': inc_calidad}

def request_report_pren_serv(fecha_inic, fecha_fin, request):
    sql = """
        SELECT
            ges_trab_trabajador.primer_nombre,
            ges_trab_trabajador.segundo_nombre,
            prenomina15_plano.fecha_vpc,
            ges_trab_trabajador.apellidos,
            adm_escalasalarial.grupo,
            prenomina15_salariomax.sal,
            prenomina15_plano.id,
            prenomina15_plano.obra_id,
            prenomina15_plano.formato_id,
            prenomina15_plano.porciento,
            prenomina15_plano.tipo_doc,
            prenomina15_plano.tarifa,
            prenomina15_plano.cant,
            entrada_datos_actividad.codigo_act,
            prenomina15_plano.horas_creadas,
            prenomina15_plano.valor,
            prenomina15_plano.valor_total,
            prenomina15_plano.valor_retenido,
            prenomina15_plano.nombre,
            prenomina15_plano.num,
            prenomina15_objeto.codigo,
            prenomina15_plano.last_rev,
            prenomina15_plano.fecha_pago,
            prenomina15_especialidad.nombre AS nombre_esp,
            prenomina15_plano.trabajador_id,
            prenomina15_plano.id,
            prenomina15_objeto.nombre AS nombre_obj,
            prenomina15_plano.corte,
            prenomina15_plano.horas_creadas_real,
            prenomina15_plano.valor_real,
            prenomina15_plano.valor_retenido_real,
            prenomina15_plano.valor_total_real,
            prenomina15_plano.vpc,
            prenomina15_plano.incumplimiento_plano,
            prenomina15_plano.incumplimiento_cpl,
            prenomina15_plano.incumplimiento_calidad,
            prenomina15_plano.incumplimiento_plano_valor,
            prenomina15_plano.incumplimiento_cpl_valor,
            prenomina15_plano.incumplimiento_calidad_valor,
            prenomina15_plano.valor_pen,
            ges_trab_trabajador.departamento_id,
            adm_departamento.nombre AS nombre_dpto,
            adm_departamento.codigo,
            ges_trab_trabajador.codigo_interno,
            ges_trab_trabajador.ci,
            ges_trab_trabajador.categoria,
            ges_trab_trabajador.cargo_id,
            ges_trab_trabajador.salario_escala,
            ges_trab_trabajador.cies,
            ges_trab_trabajador.incre_res,
            adm_cargo.nombre AS nombre_cargo,
            ges_trab_trabajador.sal_cat_cient,
            ges_trab_trabajador.antiguedad,
            ges_trab_trabajador.salario_total,
            prenomina15_especialidad.siglas
        FROM
            ges_trab_trabajador,
            prenomina15_plano,
            adm_cargo,
            adm_escalasalarial,
            prenomina15_salariomax,
            prenomina15_obra,
            prenomina15_formato,
            entrada_datos_actividad,
            prenomina15_objeto,
            prenomina15_especialidad,
            adm_departamento
        WHERE
            ges_trab_trabajador.id = prenomina15_plano.trabajador_id AND
            prenomina15_salariomax.grupo_esc_id = adm_escalasalarial.id AND
            ges_trab_trabajador.cargo_id = adm_cargo.id AND
            adm_escalasalarial.id = ges_trab_trabajador.escala_salarial_id AND
            adm_departamento.id = ges_trab_trabajador.departamento_id AND
            prenomina15_obra.tipo = prenomina15_salariomax.tipo AND
            prenomina15_formato.id = prenomina15_plano.formato_id AND
            entrada_datos_actividad.id = prenomina15_plano.actividad_id AND
            prenomina15_objeto.id = prenomina15_plano.objeto_id AND
            prenomina15_plano.especialidad_id = prenomina15_especialidad.id AND
            (prenomina15_plano.fecha_pago BETWEEN '{}'::DATE AND '{}'::DATE
            OR prenomina15_plano.fecha_vpc BETWEEN '{}'::DATE AND '{}'::DATE)
        GROUP BY
            prenomina15_especialidad.siglas, prenomina15_plano.vpc,adm_departamento.codigo,
            ges_trab_trabajador.departamento_id, nombre_dpto, prenomina15_especialidad.nombre,
            ges_trab_trabajador.primer_nombre,
            ges_trab_trabajador.segundo_nombre, ges_trab_trabajador.apellidos,
            ges_trab_trabajador.categoria, ges_trab_trabajador.cargo_id,
            adm_escalasalarial.grupo, prenomina15_salariomax.sal,
            prenomina15_formato.id, ges_trab_trabajador.ci, adm_cargo.nombre,prenomina15_plano.id,
            prenomina15_plano.porciento, prenomina15_plano.tipo_doc, prenomina15_plano.tarifa,
            entrada_datos_actividad.codigo_act, ges_trab_trabajador.cies,
            prenomina15_plano.horas_creadas, prenomina15_plano.valor,
            prenomina15_plano.valor_total, ges_trab_trabajador.salario_escala,
            prenomina15_plano.valor_retenido, prenomina15_plano.nombre,
            prenomina15_plano.num, ges_trab_trabajador.codigo_interno,
            prenomina15_objeto.codigo, prenomina15_plano.last_rev,
            prenomina15_plano.fecha_pago, prenomina15_plano.fecha_vpc,
            ges_trab_trabajador.cies, ges_trab_trabajador.incre_res,
            ges_trab_trabajador.sal_cat_cient, ges_trab_trabajador.antiguedad,
            prenomina15_plano.trabajador_id, prenomina15_plano.id,
            prenomina15_objeto.nombre,
            prenomina15_plano.corte,
            prenomina15_plano.incumplimiento_plano,
            prenomina15_plano.incumplimiento_cpl,
            prenomina15_plano.incumplimiento_calidad,
            prenomina15_plano.incumplimiento_plano_valor,
            prenomina15_plano.incumplimiento_cpl_valor,
            prenomina15_plano.incumplimiento_calidad_valor,
            prenomina15_plano.valor_pen,
            ges_trab_trabajador.salario_total,
            prenomina15_plano.horas_creadas_real,
            prenomina15_plano.valor_real,
            prenomina15_plano.valor_retenido_real,
            prenomina15_plano.valor_total_real,
            prenomina15_plano.obra_id
        ORDER BY
            adm_departamento.codigo,
            adm_escalasalarial.grupo DESC,
            ges_trab_trabajador.primer_nombre,
            ges_trab_trabajador.segundo_nombre,
            ges_trab_trabajador.apellidos,
            prenomina15_plano.obra_id,
            prenomina15_plano.num;
        """.format(fecha_inic, fecha_fin, fecha_inic, fecha_fin)

    obras = listar_obra(request)
    result = Plano.objects.raw(sql)
    areas = []
    personas = []
    planos = []
    obrs = []
    for element in result:
        flag = False
        for area in areas:
            if area.codigo == element.codigo:
                flag = True
                break
        if not flag:
            areas.append(Area(nombre=element.nombre_dpto, codigo=element.codigo, personas=[], cant=0,
                              horas_creadas_total=0, setrt=0, inc_res_30=0, cies=0, ant=0, maest=0,
                              total_dev_30=0, cant_planos=0, total_horas=0, sal_res15=0, sal_res15_plano=0,
                              ret=0, ret_ant=0, impacto=0, sal_tot_dev=0, incumplimiento_plano_valor=0,
                              incumplimiento_cpl_valor=0, incumplimiento_calidad_valor=0, valor_pen=0))

    for element in result:
        flag = False
        for obr in obrs:
            if obr.id_obra == element.obra.id:
                flag = True
                break
        if not flag:
            obrs.append(Obr(id_obra=element.obra.id, obra=element.obra.nombre, planos=[], no=0,
                            horas_creadas=0, strt=0, inc_r30=0, cies=0, ant=0,
                            maest=0, devengado=0, impacto=0, total=0, sal_res15=0, retenido=0, retenido_ant=0, valor_total=0))
    no_loop = 0
    for element in result:
        flag = False
        for per in personas:
            if per.no == element.codigo_interno:
                if per.dpto == element.codigo:
                    flag = True
                break
        if not flag:
            no_loop += 1
            tarifa_se = (element.salario_escala / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                            rounding=ROUND_HALF_UP)
            tarifa_pa = (element.incre_res / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                       rounding=ROUND_HALF_UP)
            if element.antiguedad != 0.00:
                tarifa_ant = (element.antiguedad / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                             rounding=ROUND_HALF_UP)
            else:
                tarifa_ant = Decimal(0.00)
            tarifa_cies = (element.cies / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                    rounding=ROUND_HALF_UP)
            if element.sal_cat_cient != 0.00:
                tarifa_maest = (element.sal_cat_cient / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                                  rounding=ROUND_HALF_UP)
            else:
                tarifa_maest = Decimal(0.00)
            personas.append(
                Trab(no=element.codigo_interno, trab_id=element.trabajador_id,
                     nombre=element.primer_nombre + ' ' + element.segundo_nombre + ' ' + element.apellidos,
                     obras=[], planos=[], ge=element.grupo, sal_max=element.sal, categoria=element.categoria,
                     tarifa=element.tarifa, total_horas=0, total_pagar=0, total_retenido=0, total_valor=0,
                     cant=0, dpto=element.codigo, retenido_ant=0, pagar=0, ci=element.ci,
                     sal_escala=element.salario_escala, cies=element.cies, incre_res=element.incre_res,
                     antig=element.antiguedad, maestria=element.sal_cat_cient, tarifa_se=tarifa_se,
                     tarifa_pa=tarifa_pa, tarifa_ant=tarifa_ant, tarifa_cies=tarifa_cies,
                     tarifa_maest=tarifa_maest, salario_total=element.salario_total, se_real=0.00,
                     pa_real=0.00, cies_real=0.00, ant_real=0.00, maest_real=0.00, total_dev=0.00, impacto=0.00,
                     sal_dev_total=0.00, cargo=element.nombre_cargo, incumplimiento_plano=0, incumplimiento_cpl=0,
                     incumplimiento_calidad=0, incumplimiento_plano_valor=0, incumplimiento_cpl_valor=0,
                     incumplimiento_calidad_valor=0, total_valor_pen=0, sal_res15=0, no_loop=no_loop))

    for element in result:
        val = ''
        pagar = ''
        retenido = 0
        pago_ant = 0
        horas_creadas = 0
        valor_retenido_real = 0
        valor_total_real = 0
        horas_creadas_real = 0
        list_cant = []
        catalogo = []
        cantidad = element.cant - 1
        inicio = datetime.datetime.strptime(fecha_inic, "%Y-%m-%d").date()
        fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        fecha_pago = datetime.datetime.strptime(str(element.fecha_pago), "%Y-%m-%d").date()
        if element.fecha_vpc is not None:
            fecha_vpc = datetime.datetime.strptime(str(element.fecha_vpc), "%Y-%m-%d").date()
            if inicio <= fecha_pago <= fin and inicio <= fecha_vpc <= fin:
                val = 0  # el caso 0 es para cuando se paga el plano 100 %
                horas_creadas = element.horas_creadas
                pagar = element.valor_real
                horas_creadas_real = element.horas_creadas_real
            if (fecha_pago < inicio or fecha_pago > fin) and inicio <= fecha_vpc <= fin:
                val = 1  # el caso 1 es para cuando se paga el plano 20 %
                pagar = 0
                pago_ant = element.valor_retenido
                valor_retenido_real = element.valor_retenido_real
                horas_creadas = 0
            if inicio <= fecha_pago <= fin and (fecha_vpc < inicio or fecha_vpc > fin):
                val = 2  # el caso 2 es para cuando se paga el plano 80 %
                pagar = element.valor_total_real
                valor_total_real = element.valor_total_real
                retenido = element.valor_retenido
                valor_retenido_real = element.valor_retenido_real
                horas_creadas = element.horas_creadas
                horas_creadas_real = element.horas_creadas_real
        else:
            if inicio <= fecha_pago <= fin:
                val = 2  # el caso 2 es para cuando se paga el plano 80 %
                pagar = element.valor_total_real
                valor_total_real = element.valor_total_real
                retenido = element.valor_retenido
                valor_retenido_real = element.valor_retenido_real
                horas_creadas = element.horas_creadas
                horas_creadas_real = element.horas_creadas_real
        while cantidad != 0:
            list_cant.append(1)
            cantidad -= 1
        if element.cant != 1:
            catalogos = Catalogo.objects.all().filter(plano_id=element.id)
            for cat in catalogos:
                catalogo.append(
                    Cat(formato=cat.formato, porciento=int(float(cat.porciento) * 100), horas_creadas=cat.horas_creadas,
                        horas_creadas_real=cat.horas_creadas_real, valor_retenido=cat.valor_retenido,
                        valor_retenido_real=cat.valor_retenido_real, valor=cat.valor,
                        valor_real=cat.valor_real, valor_total=cat.valor_total,
                        valor_total_real=cat.valor_total_real,
                        incumplimiento_plano=element.incumplimiento_plano,
                        incumplimiento_plano_valor=cat.incumplimiento_plano_valor,
                        incumplimiento_cpl=element.incumplimiento_cpl,
                        incumplimiento_cpl_valor=cat.incumplimiento_cpl_valor,
                        incumplimiento_calidad=element.incumplimiento_calidad,
                        incumplimiento_calidad_valor=cat.incumplimiento_calidad_valor,
                        valor_pen=cat.valor_pen))
        planos.append(
            Plan(nombre=element.nombre, codigo=element.num, objeto=element.codigo, etapa=element.codigo_act,
                 formato=element.formato.formato, porciento=int(float(element.porciento) * 100),
                 horas_creadas=horas_creadas, nombre_obj=element.nombre_obj,
                 valor=element.valor, valor_total=element.valor_total, retenido=retenido, reten_ant=pago_ant,
                 rev=element.last_rev, vpc=element.vpc, trabajador_id=element.trabajador_id,
                 ult_rev=element.last_rev, especialidad=element.nombre_esp, caso=val, pagar=pagar, cant=element.cant,
                 corte=element.corte, horas_creadas_real=horas_creadas_real, valor_real=element.valor_real,
                 valor_retenido_real=valor_retenido_real, valor_total_real=valor_total_real, list_cant=list_cant,
                 tarifa=element.tarifa, sigla=element.siglas, tipo_doc=element.tipo_doc,
                 incumplimiento_plano=element.incumplimiento_plano, incumplimiento_cpl=element.incumplimiento_cpl,
                 incumplimiento_calidad=element.incumplimiento_calidad,
                 incumplimiento_plano_valor=element.incumplimiento_plano_valor,
                 incumplimiento_cpl_valor=element.incumplimiento_cpl_valor,
                 incumplimiento_calidad_valor=element.incumplimiento_calidad_valor,
                 valor_pen=element.valor_pen, catalogo=catalogo, obra=element.obra))

    for per in personas:
        for plano in planos:
            if plano.trabajador_id == per.trab_id:
                flag = False
                for obr in per.obras:
                    if plano.obra.id == obr.id_obra:
                        flag = True
                        obr.horas_creadas += plano.horas_creadas
                        if plano.caso != 1:
                            obr.sal_res15 += plano.valor
                        if plano.caso == 2:
                            obr.retenido += plano.retenido
                        if plano.caso == 0:
                            obr.valor_total += plano.valor_real
                        if plano.caso == 1:
                            obr.retenido_ant += plano.reten_ant
                        if plano.cant != 1:
                            for c in plano.catalogo:
                                if plano.caso == 0:
                                    obr.valor_total += c.valor_real
                                    obr.horas_creadas += c.horas_creadas
                                if plano.caso == 1:
                                    obr.retenido += c.retenido
                                    obr.retenido_ant += c.valor_retenido
                                    obr.horas_creadas += plano.horas_creadas
                                if plano.caso == 2:
                                    obr.valor_total += c.valor_real
                                    obr.horas_creadas += c.horas_creadas
                                    obr.retenido += c.valor_retenido
                                if plano.caso != 1:
                                    obr.sal_res15 += c.valor
                        break
                if not flag:
                    o_hc = plano.horas_creadas
                    o_vt = 0
                    s_r15 = 0
                    o_ret = plano.retenido
                    o_ret_ant = 0
                    if plano.caso != 1:
                        s_r15 += plano.valor
                    if plano.caso == 0:
                        o_vt = plano.valor_real
                    if plano.caso == 2:
                        o_ret = plano.retenido
                    if plano.caso == 1:
                        o_ret_ant = plano.reten_ant
                    if plano.cant != 1:
                        for c in plano.catalogo:
                            if plano.caso == 0:
                                o_vt = c.valor_real
                                o_hc += c.horas_creadas
                            if plano.caso == 1:
                                o_ret += c.retenido
                                o_ret_ant += c.valor_retenido
                                o_hc += plano.horas_creadas
                            if plano.caso == 2:
                                o_hc += c.horas_creadas
                                o_ret_ant += c.valor_retenido
                            if plano.caso != 1:
                                s_r15 += c.valor
                    per.obras.append(
                        Obr(id_obra=plano.obra.id, obra=plano.obra.nombre, planos=[], no=0,
                            horas_creadas=o_hc,
                            strt=0, inc_r30=0, cies=0, ant=0, valor_total=o_vt,
                            maest=0, devengado=0, impacto=0, total=0, sal_res15=s_r15, retenido=o_ret, retenido_ant=o_ret_ant))
                per.planos.append(plano)
                if plano.caso != 1:
                    per.cant += 1
                    per.total_valor += plano.valor_real
                    per.sal_res15 += plano.valor

                per.total_horas += plano.horas_creadas
                per.total_retenido += plano.retenido
                per.pagar += plano.pagar
                if plano.caso == 1:
                    per.retenido_ant += plano.reten_ant
                per.incumplimiento_plano = plano.incumplimiento_plano
                per.incumplimiento_cpl = plano.incumplimiento_cpl
                per.incumplimiento_calidad = plano.incumplimiento_calidad
                per.incumplimiento_plano_valor += plano.incumplimiento_plano_valor
                per.incumplimiento_cpl_valor += plano.incumplimiento_cpl_valor
                per.incumplimiento_calidad_valor += plano.incumplimiento_calidad_valor
                per.total_valor_pen += plano.valor_pen

                if plano.cant != 1:
                    for c in plano.catalogo:
                        if plano.caso == 0:
                            per.total_valor += c.valor_real
                            per.total_horas += c.horas_creadas
                            per.pagar += c.valor
                        if plano.caso == 1:
                            per.total_retenido += c.retenido
                            per.retenido_ant += c.valor_retenido
                            per.pagar += plano.pagar
                            per.total_horas += plano.horas_creadas
                        if plano.caso == 2:
                            per.total_valor += c.valor_real
                            per.total_horas += c.horas_creadas
                            per.total_retenido += c.valor_retenido
                            per.pagar += c.valor_total

                        per.incumplimiento_plano = plano.incumplimiento_plano
                        per.incumplimiento_cpl = plano.incumplimiento_cpl
                        per.incumplimiento_calidad = plano.incumplimiento_calidad
                        per.incumplimiento_plano_valor += c.incumplimiento_plano_valor
                        per.incumplimiento_cpl_valor += c.incumplimiento_cpl_valor
                        per.incumplimiento_calidad_valor += c.incumplimiento_calidad_valor
                        per.total_valor_pen += c.valor_pen
                        per.sal_res15 += c.valor

    for per in personas:
        for obr in per.obras:
            obr.strt = Decimal(per.tarifa_se * obr.horas_creadas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            obr.inc_r30 = Decimal(per.tarifa_pa * obr.horas_creadas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            obr.cies = Decimal(Decimal(per.tarifa_cies) * obr.horas_creadas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            obr.ant = Decimal(Decimal(per.tarifa_ant) * obr.horas_creadas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            obr.maest = Decimal(Decimal(per.tarifa_maest) * obr.horas_creadas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            obr.devengado = obr.strt + obr.inc_r30 + obr.cies + obr.ant + obr.maest
            obr.impacto = (obr.sal_res15 - obr.devengado - obr.retenido) + obr.retenido_ant
            obr.total = obr.impacto + obr.devengado
    for per in personas:
        for obrap in per.obras:
            for obr in obrs:
                if obrap.id_obra == obr.id_obra:
                    obr.sal_res15 += obrap.sal_res15
                    obr.horas_creadas += obrap.horas_creadas
                    obr.retenido += obrap.retenido
                    obr.retenido_ant += obrap.retenido_ant
                    obr.strt += obrap.strt
                    obr.inc_r30 += obrap.inc_r30
                    obr.cies += obrap.cies
                    obr.ant += obrap.ant
                    obr.maest += obrap.maest
                    obr.devengado += obrap.devengado
                    obr.impacto += obrap.impacto
                    obr.total += obrap.total


    total_planos = 0
    for area in areas:
        for per in personas:
            if per.dpto == area.codigo:
                area.personas.append(per)
                area.cant += per.cant
        total_planos += area.cant

    completo = Plano.objects.all().filter(fecha_vpc__range=(fecha_inic, fecha_fin),
                                          fecha_pago__range=(fecha_inic, fecha_fin)).count()
    retenido = Plano.objects.all().filter(fecha_vpc__range=(fecha_inic, fecha_fin)).count() - completo

    for area in areas:
        for per in area.personas:
            per.se_real = Decimal(per.tarifa_se * per.total_horas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.pa_real = Decimal(per.tarifa_pa * per.total_horas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.cies_real = Decimal(per.tarifa_cies * per.total_horas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.ant_real = Decimal(per.tarifa_ant * per.total_horas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.maest_real = Decimal(Decimal(per.tarifa_maest) * per.total_horas).quantize(Decimal('.01'),
                                                                                           rounding=ROUND_HALF_UP)
            per.total_dev = per.se_real + per.pa_real + per.cies_real + per.maest_real + per.ant_real
            per.impacto = (per.sal_res15 - per.total_dev - per.total_retenido) + per.retenido_ant
            per.sal_dev_total = per.impacto + per.total_dev
            area.horas_creadas_total += per.total_horas
            area.setrt += per.se_real
            area.inc_res_30 += per.pa_real
            area.cies += per.cies_real
            area.ant += per.ant_real
            area.maest += per.maest_real
            area.total_dev_30 += per.total_dev
            area.cant_planos += per.cant
            area.total_horas += per.total_horas
            area.sal_res15_plano += per.sal_res15
            area.sal_res15 += per.sal_res15
            area.ret += per.total_retenido
            area.ret_ant += per.retenido_ant
            area.impacto += per.impacto
            area.sal_total_dev += per.sal_dev_total
            area.incumplimiento_plano_valor += per.incumplimiento_plano_valor
            area.incumplimiento_cpl_valor += per.incumplimiento_cpl_valor
            area.incumplimiento_calidad_valor += per.incumplimiento_calidad_valor
            area.valor_pen += per.total_valor_pen

    horas = 0
    setrt = 0
    inc_res_30 = 0
    cies = 0
    ant = 0
    maest = 0
    total_dev_30 = 0
    cant_planos = 0
    sal_res15_plano = 0
    sal_res15 = 0
    inc_plano = 0
    inc_cpl = 0
    inc_calidad = 0
    ret = 0
    ret_ant = 0
    impacto = 0
    sal_total_dev = 0
    for area in areas:
        horas += area.horas_creadas_total
        setrt += area.setrt
        inc_res_30 += area.inc_res_30
        cies += area.cies
        ant += area.ant
        maest += area.maest
        total_dev_30 += area.total_dev_30
        cant_planos += area.cant_planos
        sal_res15_plano += area.sal_res15_plano
        inc_plano += area.incumplimiento_plano_valor
        inc_cpl += area.incumplimiento_cpl_valor
        inc_calidad += area.incumplimiento_calidad_valor
        sal_res15 += area.sal_res15
        ret += area.ret
        ret_ant += area.ret_ant
        impacto += area.impacto
        sal_total_dev += area.sal_total_dev

    return {'areas': areas, 'fecha_inic': fecha_inic, 'fecha_fin': fecha_fin, 'obras': obras, 'obrs': obrs,
            'total_planos': total_planos, 'completo': completo, 'retenido': retenido, 'horas': horas, 'setrt': setrt,
            'inc_res_30': inc_res_30, 'cies': cies, 'ant': ant, 'maest': maest, 'total_dev_30': total_dev_30,
            'cant_planos': cant_planos, 'sal_res15_plano': sal_res15_plano, 'ret': ret, 'ret_ant': ret_ant,
            'impacto': impacto, 'sal_total_dev': sal_total_dev, 'sal_res15': sal_res15, 'inc_plano': inc_plano,
            'inc_cpl': inc_cpl, 'inc_calidad': inc_calidad}






def request_report_anexo(fecha_inic, fecha_fin, obra, horas, request):
    sql = """
    SELECT
        ges_trab_trabajador.primer_nombre,
        ges_trab_trabajador.segundo_nombre,
        prenomina15_plano.fecha_vpc,
        ges_trab_trabajador.apellidos,
        adm_escalasalarial.grupo,
        prenomina15_salariomax.sal,
        prenomina15_plano.formato_id,
        prenomina15_plano.porciento,
        prenomina15_plano.tarifa,
        prenomina15_plano.cant,
        entrada_datos_actividad.codigo_act,
        prenomina15_plano.horas_creadas,
        prenomina15_plano.valor,
        prenomina15_plano.valor_total,
        prenomina15_plano.valor_retenido,
        prenomina15_plano.nombre,
        prenomina15_plano.num,
        prenomina15_objeto.codigo,
        prenomina15_plano.last_rev,
        prenomina15_plano.fecha_pago,
        prenomina15_especialidad.nombre AS nombre_esp,
        prenomina15_plano.trabajador_id,
        prenomina15_plano.id,
        prenomina15_objeto.nombre AS nombre_obj,
        prenomina15_plano.corte,
        prenomina15_plano.horas_creadas_real,
        prenomina15_plano.valor_real,
        prenomina15_plano.valor_retenido_real,
        prenomina15_plano.valor_total_real,
        prenomina15_plano.vpc, ges_trab_trabajador.departamento_id,
        adm_departamento.nombre AS nombre_dpto,
        adm_departamento.codigo,
        ges_trab_trabajador.codigo_interno,
        ges_trab_trabajador.ci,
        ges_trab_trabajador.categoria,
        ges_trab_trabajador.cargo_id,
        ges_trab_trabajador.salario_escala,
        ges_trab_trabajador.cies,
        ges_trab_trabajador.incre_res,
        adm_cargo.nombre AS nombre_cargo,
        ges_trab_trabajador.sal_cat_cient,
        ges_trab_trabajador.antiguedad,
        ges_trab_trabajador.salario_total,
        prenomina15_especialidad.siglas,
        prenomina15_plano.id
    FROM 
        ges_trab_trabajador, prenomina15_plano, adm_cargo,
        adm_escalasalarial, prenomina15_salariomax, prenomina15_obra,
        prenomina15_formato, entrada_datos_actividad, prenomina15_objeto,
        prenomina15_especialidad, adm_departamento
    WHERE 
        ges_trab_trabajador.id = prenomina15_plano.trabajador_id and
        prenomina15_salariomax.grupo_esc_id = adm_escalasalarial.id and
        ges_trab_trabajador.cargo_id = adm_cargo.id and
        adm_escalasalarial.id = ges_trab_trabajador.escala_salarial_id and
        adm_departamento.id = ges_trab_trabajador.departamento_id and
        prenomina15_plano.obra_id = '{}' and
        prenomina15_obra.tipo = prenomina15_salariomax.tipo and 
        prenomina15_formato.id = prenomina15_plano.formato_id and
        entrada_datos_actividad.id = prenomina15_plano.actividad_id and
        prenomina15_objeto.id = prenomina15_plano.objeto_id and
        prenomina15_plano.especialidad_id = prenomina15_especialidad.id and
        (prenomina15_plano.fecha_pago BETWEEN '{}'::DATE AND '{}'::DATE OR
        prenomina15_plano.fecha_vpc BETWEEN '{}'::DATE AND '{}'::DATE)
    GROUP BY
        prenomina15_plano.vpc,adm_departamento.codigo, ges_trab_trabajador.departamento_id,
        nombre_dpto, prenomina15_especialidad.nombre, ges_trab_trabajador.primer_nombre,
        ges_trab_trabajador.segundo_nombre, ges_trab_trabajador.apellidos,
        ges_trab_trabajador.categoria, ges_trab_trabajador.cargo_id,
        adm_escalasalarial.grupo, prenomina15_salariomax.sal, prenomina15_formato.id,
        ges_trab_trabajador.ci, adm_cargo.nombre,
        prenomina15_plano.porciento, prenomina15_plano.tarifa,
        entrada_datos_actividad.codigo_act, ges_trab_trabajador.cies,
        prenomina15_plano.horas_creadas, prenomina15_plano.valor,
        prenomina15_plano.valor_total, ges_trab_trabajador.salario_escala,
        prenomina15_plano.valor_retenido, prenomina15_plano.nombre,
        prenomina15_plano.num, ges_trab_trabajador.codigo_interno,
        prenomina15_objeto.codigo, prenomina15_plano.last_rev,
        prenomina15_plano.fecha_pago, prenomina15_plano.fecha_vpc,
        ges_trab_trabajador.cies, ges_trab_trabajador.incre_res,
        ges_trab_trabajador.sal_cat_cient, ges_trab_trabajador.antiguedad,
        prenomina15_plano.trabajador_id, prenomina15_plano.id, prenomina15_objeto.nombre,
        prenomina15_plano.corte, ges_trab_trabajador.salario_total,
        prenomina15_especialidad.siglas,
        prenomina15_plano.horas_creadas_real,
        prenomina15_plano.valor_real,
        prenomina15_plano.valor_retenido_real,
        prenomina15_plano.valor_total_real,
        prenomina15_plano.id
    ORDER BY
        prenomina15_especialidad.nombre,
        adm_escalasalarial.grupo DESC,
        ges_trab_trabajador.primer_nombre,
        ges_trab_trabajador.segundo_nombre,
        ges_trab_trabajador.apellidos,
        prenomina15_plano.num;
    """.format(obra, fecha_inic, fecha_fin, fecha_inic, fecha_fin)

    obras = listar_obra(request)
    result = Plano.objects.raw(sql)
    areas = []
    personas = []
    planos = []
    for element in result:
        flag = False
        for area in areas:
            if area.codigo == element.codigo:
                flag = True
                break
        if not flag:
            areas.append(Area(nombre=element.nombre_dpto, codigo=element.codigo, personas=[], cant=0,
                              horas_creadas_total=0, setrt=0, inc_res_30=0, cies=0, ant=0, maest=0,
                              total_dev_30=0, cant_planos=0, total_horas=0, sal_res15=0, sal_res15_plano=0,
                              ret=0, ret_ant=0, impacto=0, sal_tot_dev=0, incumplimiento_plano_valor=0,
                              incumplimiento_cpl_valor=0, incumplimiento_calidad_valor=0, valor_pen=0))

    for element in result:
        flag = False
        for per in personas:
            if per.no == element.codigo_interno:
                if per.dpto == element.codigo:
                    flag = True
                break
        if not flag:
            tarifa_se = (element.salario_escala / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                            rounding=ROUND_HALF_UP)
            tarifa_pa = (element.incre_res / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                       rounding=ROUND_HALF_UP)
            if element.antiguedad != 0.00:
                tarifa_ant = (element.antiguedad / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                             rounding=ROUND_HALF_UP)
            else:
                tarifa_ant = Decimal(0.00)
            tarifa_cies = (element.cies / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                    rounding=ROUND_HALF_UP)
            if element.sal_cat_cient != 0.00:
                tarifa_maest = (element.sal_cat_cient / Decimal(190.60)).quantize(Decimal('.000000001'),
                                                                                  rounding=ROUND_HALF_UP)
            else:
                tarifa_maest = Decimal(0.00)
            personas.append(
                Trab(no=element.codigo_interno, trab_id=element.trabajador_id,
                     nombre=element.primer_nombre + ' ' + element.segundo_nombre + ' ' + element.apellidos,
                     planos=[], ge=element.grupo, sal_max=element.sal, categoria=element.categoria,
                     tarifa=element.tarifa, total_horas=0, total_pagar=0, total_retenido=0, total_valor=0,
                     cant=0,
                     dpto=element.codigo, retenido_ant=0, pagar=0, ci=element.ci,
                     sal_escala=element.salario_escala, cies=element.cies, incre_res=element.incre_res,
                     antig=element.antiguedad, maestria=element.sal_cat_cient, tarifa_se=tarifa_se,
                     tarifa_pa=tarifa_pa, tarifa_ant=tarifa_ant, tarifa_cies=tarifa_cies,
                     tarifa_maest=tarifa_maest, salario_total=element.salario_total, se_real=0.00,
                     pa_real=0.00, cies_real=0.00, ant_real=0.00, maest_real=0.00, total_dev=0.00, impacto=0.00,
                     sal_dev_total=0.00, cargo=element.nombre_cargo, incumplimiento_plano=0, incumplimiento_cpl=0,
                     incumplimiento_calidad=0, incumplimiento_plano_valor=0, incumplimiento_cpl_valor=0,
                     incumplimiento_calidad_valor=0, total_valor_pen=0, sal_res15=0))

    for element in result:
        val = ''
        pagar = ''
        retenido = 0
        pago_ant = 0
        horas_creadas = 0
        valor_retenido_real = 0
        valor_total_real = 0
        horas_creadas_real = 0
        list_cant = []
        catalogo = []
        cantidad = element.cant - 1
        inicio = datetime.datetime.strptime(fecha_inic, "%Y-%m-%d").date()
        fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        fecha_pago = datetime.datetime.strptime(str(element.fecha_pago), "%Y-%m-%d").date()
        if element.fecha_vpc is not None:
            fecha_vpc = datetime.datetime.strptime(str(element.fecha_vpc), "%Y-%m-%d").date()
            if inicio <= fecha_pago <= fin and inicio <= fecha_vpc <= fin:
                val = 0  # el caso 0 es para cuando se paga el plano 100 %
                horas_creadas = element.horas_creadas
                pagar = element.valor
                horas_creadas_real = element.horas_creadas_real
            if (fecha_pago < inicio or fecha_pago > fin) and inicio <= fecha_vpc <= fin:
                val = 1  # el caso 1 es para cuando se paga el plano 20 %
                pagar = 0
                pago_ant = element.valor_retenido
                valor_retenido_real = element.valor_retenido_real
                horas_creadas = 0
            if inicio <= fecha_pago <= fin and (fecha_vpc < inicio or fecha_vpc > fin):
                val = 2  # el caso 2 es para cuando se paga el plano 80 %
                pagar = element.valor_total
                valor_total_real = element.valor_total_real
                retenido = element.valor_retenido
                valor_retenido_real = element.valor_retenido_real
                horas_creadas = element.horas_creadas
                horas_creadas_real = element.horas_creadas_real
        else:
            if inicio <= fecha_pago <= fin:
                val = 2  # el caso 2 es para cuando se paga el plano 80 %
                pagar = element.valor_total
                valor_total_real = element.valor_total_real
                retenido = element.valor_retenido
                valor_retenido_real = element.valor_retenido_real
                horas_creadas = element.horas_creadas
                horas_creadas_real = element.horas_creadas_real
        while cantidad != 0:
            list_cant.append(1)
            cantidad -= 1
        if element.cant != 1:
            catalogos = Catalogo.objects.all().filter(plano_id=element.id)
            for cat in catalogos:

                catalogo.append(Cat(formato=cat.formato, porciento=int(float(cat.porciento) * 100), horas_creadas=cat.horas_creadas,
                                    horas_creadas_real=cat.horas_creadas_real, valor_retenido=cat.valor_retenido,
                                    valor_retenido_real=cat.valor_retenido_real, valor=cat.valor,
                                    valor_real=cat.valor_real, valor_total=cat.valor_total,
                                    valor_total_real=cat.valor_total_real,
                                    incumplimiento_plano=element.incumplimiento_plano,
                                    incumplimiento_plano_valor=cat.incumplimiento_plano_valor,
                                    incumplimiento_cpl=element.incumplimiento_cpl,
                                    incumplimiento_cpl_valor=cat.incumplimiento_cpl_valor,
                                    incumplimiento_calidad=element.incumplimiento_calidad,
                                    incumplimiento_calidad_valor=cat.incumplimiento_calidad_valor,
                                    valor_pen=cat.valor_pen))
        planos.append(
            Plan(nombre=element.nombre, codigo=element.num, objeto=element.codigo, etapa=element.codigo_act,
                 formato=element.formato.formato, porciento=int(float(element.porciento) * 100),
                 horas_creadas=horas_creadas, nombre_obj=element.nombre_obj,
                 valor=element.valor, valor_total=element.valor_total, retenido=retenido, reten_ant=pago_ant,
                 rev=element.last_rev, vpc=element.vpc, trabajador_id=element.trabajador_id,
                 ult_rev=element.last_rev, especialidad=element.nombre_esp, caso=val, pagar=pagar, cant=element.cant,
                 corte=element.corte, horas_creadas_real=horas_creadas_real, valor_real=element.valor_real,
                 valor_retenido_real=valor_retenido_real, valor_total_real=valor_total_real, list_cant=list_cant,
                 sigla=element.siglas, tarifa=0, tipo_doc=element.tipo_doc,
                 incumplimiento_plano=element.incumplimiento_plano, incumplimiento_cpl=element.incumplimiento_cpl,
                 incumplimiento_calidad=element.incumplimiento_calidad,
                 incumplimiento_plano_valor=element.incumplimiento_plano_valor,
                 incumplimiento_cpl_valor=element.incumplimiento_cpl_valor,
                 incumplimiento_calidad_valor=element.incumplimiento_calidad_valor,
                 valor_pen=element.valor_pen, catalogo=catalogo))

    for per in personas:
        for plano in planos:
            if plano.trabajador_id == per.trab_id:
                per.planos.append(plano)
                if plano.caso != 1:
                    per.cant += 1
                    per.total_valor += plano.valor_real
                per.total_horas += plano.horas_creadas
                per.total_retenido += plano.retenido
                per.pagar += plano.pagar
                if plano.caso == 1:
                    per.retenido_ant += plano.reten_ant
                per.incumplimiento_plano = plano.incumplimiento_plano
                per.incumplimiento_cpl = plano.incumplimiento_cpl
                per.incumplimiento_calidad = plano.incumplimiento_calidad
                per.incumplimiento_plano_valor += plano.incumplimiento_plano_valor
                per.incumplimiento_cpl_valor += plano.incumplimiento_cpl_valor
                per.incumplimiento_calidad_valor += plano.incumplimiento_calidad_valor
                per.total_valor_pen += plano.valor_pen
                per.sal_res15 = per.pagar
                if plano.cant != 1:
                    for c in plano.catalogo:
                        if plano.caso == 0:
                            per.total_valor += c.valor_real
                            per.total_horas += c.horas_creadas
                            per.pagar += c.valor
                        if plano.caso == 1:
                            per.total_retenido += c.retenido
                            per.retenido_ant += c.valor_retenido
                            per.pagar += plano.pagar
                            per.total_horas += plano.horas_creadas
                        if plano.caso == 2:
                            per.total_valor += c.valor_real
                            per.total_horas += c.horas_creadas
                            per.total_retenido += c.valor_retenido
                            per.pagar += c.valor_total

                        per.incumplimiento_plano = plano.incumplimiento_plano
                        per.incumplimiento_cpl = plano.incumplimiento_cpl
                        per.incumplimiento_calidad = plano.incumplimiento_calidad
                        per.incumplimiento_plano_valor += c.incumplimiento_plano_valor
                        per.incumplimiento_cpl_valor += c.incumplimiento_cpl_valor
                        per.incumplimiento_calidad_valor += c.incumplimiento_calidad_valor
                        per.total_valor_pen += c.valor_pen
                        per.sal_res15 = per.pagar

    total_planos = 0
    for area in areas:
        for per in personas:
            if per.dpto == area.codigo:
                area.personas.append(per)
                area.cant += per.cant
        total_planos += area.cant

    completo = Plano.objects.all().filter(fecha_vpc__range=(fecha_inic, fecha_fin),
                                          fecha_pago__range=(fecha_inic, fecha_fin)).count()
    retenido = Plano.objects.all().filter(fecha_vpc__range=(fecha_inic, fecha_fin)).count() - completo

    for area in areas:
        for per in area.personas:
            per.se_real = Decimal(per.tarifa_se * per.total_horas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.pa_real = Decimal(per.tarifa_pa * per.total_horas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.cies_real = Decimal(per.tarifa_cies * per.total_horas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.ant_real = Decimal(per.tarifa_ant * per.total_horas).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.maest_real = Decimal(Decimal(per.tarifa_maest) * per.total_horas).quantize(Decimal('.01'),
                                                                                           rounding=ROUND_HALF_UP)
            per.total_dev = per.se_real + per.pa_real + per.cies_real + per.maest_real + per.ant_real
            per.impacto = (per.total_valor - per.total_dev - per.total_retenido - per.total_valor_pen) + per.retenido_ant
            per.sal_dev_total = per.impacto + per.total_dev
            per.eval = int((per.total_horas / Decimal(horas)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP) * 100)
            per.tarifa_30 = (per.salario_total / Decimal(190.60)).quantize(Decimal('.000001'), rounding=ROUND_HALF_UP)
            per.dif_30_15 = (per.total_valor - per.total_retenido - per.total_dev - per.total_valor_pen) + per.retenido_ant
            per.vac = (per.dif_30_15 * Decimal(0.0909)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.otros = ((per.dif_30_15 + per.vac) * Decimal(0.19)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            per.dif_sal = per.dif_30_15 + per.vac + per.otros
            if per.total_horas != 0:
                area.horas_creadas_total += per.total_horas
            area.setrt += per.se_real
            area.inc_res_30 += per.pa_real
            area.cies += per.cies_real
            area.ant += per.ant_real
            area.maest += per.maest_real
            area.total_dev_30 += per.total_dev
            area.cant_planos += per.cant
            area.total_horas += per.total_horas
            area.sal_res15_plano += per.total_valor
            # area.sal_res15 += per.pagar
            area.sal_res15 += per.sal_res15
            area.ret += per.total_retenido
            area.ret_ant += per.retenido_ant
            area.impacto += per.impacto
            area.sal_total_dev += per.sal_dev_total
            area.total_vac += per.vac
            area.total_otros += per.otros
            area.total_dif_sal += per.dif_sal
            area.valor_pen += per.total_valor_pen

    horas = 0
    setrt = 0
    inc_res_30 = 0
    cies = 0
    ant = 0
    maest = 0
    total_dev_30 = 0
    cant_planos = 0
    sal_res15_plano = 0
    sal_res15 = 0
    penalizacion = 0
    ret = 0
    ret_ant = 0
    impacto = 0
    sal_total_dev = 0
    total_vac = 0
    total_otros = 0
    total_dif_sal = 0
    for area in areas:
        total_vac += area.total_vac
        total_otros += area.total_otros
        total_dif_sal += area.total_dif_sal
        horas += area.horas_creadas_total
        setrt += area.setrt
        inc_res_30 += area.inc_res_30
        cies += area.cies
        ant += area.ant
        maest += area.maest
        total_dev_30 += area.total_dev_30
        cant_planos += area.cant_planos
        sal_res15_plano += area.sal_res15_plano
        penalizacion += area.valor_pen
        sal_res15 += area.sal_res15
        ret += area.ret
        ret_ant += area.ret_ant
        impacto += area.impacto
        sal_total_dev += area.sal_total_dev

    return {'areas': areas, 'fecha_inic': fecha_inic, 'fecha_fin': fecha_fin, 'obras': obras, 'total_vac': total_vac,
            'total_planos': total_planos, 'completo': completo, 'retenido': retenido, 'horas': horas, 'setrt': setrt,
            'inc_res_30': inc_res_30, 'cies': cies, 'ant': ant, 'maest': maest, 'total_dev_30': total_dev_30,
            'cant_planos': cant_planos, 'sal_res15_plano': sal_res15_plano, 'ret': ret, 'ret_ant': ret_ant,
            'impacto': impacto, 'sal_total_dev': sal_total_dev, 'total_otros': total_otros,
            'sal_total_dev': sal_total_dev,
            'penalizacion': penalizacion, 'total_dif_sal': total_dif_sal}


