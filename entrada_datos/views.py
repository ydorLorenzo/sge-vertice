from _testbuffer import ndarray
from django.contrib.auth.models import _user_has_module_perms
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import FieldError
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.views import generic
from .form import *
from rechum.my_decorators import context_add_perm


#@permission_required('entrada_datos','home_principal')
def home_ent_dat(request):
    # Verificando si tiene permiso para el modulo de Entrada de Datos
    permiso_app_adm = _user_has_module_perms(request.user, 'entrada_datos')
    if permiso_app_adm:
        context = {'request': request}
        return render(request, 'home_ent_dat.html', context)
    else:
        return redirect('home_principal')



@permission_required('entrada_datos.read_inversionista','home_principal')
def gestionar_inversionista(request):
    list_inv = Inversionista.objects.all()
    form = InversionistaForm(request.POST or None)
    context = dict(request=request,
                   list_inv=list_inv,
                   form=form)
    context = context_add_perm(request, context, 'entrada_datos', 'inversionista')
    return render(request, 'Gestionar_Inversionista.html', context)


@permission_required('entrada_datos.read_area','home_principal')
def gestionar_area(request):
    areas = Area.objects.all()
    form = AreaForm(request.POST or None)
    context = {'request': request,
               'list_area': areas,
               'form': form}
    context = context_add_perm(request, context, 'entrada_datos', 'area')
    return render(request, 'Gestionar_Area.html', context)


@permission_required('entrada_datos.read_servicio','home_principal')
def gestionar_servicio(request):
    servicio = Servicio.objects.all()
    form = ServicioForm(request.POST or None)
    context = {'list_serv': servicio, 'form': form}
    context = context_add_perm(request, context, 'entrada_datos', 'servicio')
    return render(request, 'Gestionar_Servicio.html', context)


@permission_required('entrada_datos.read_ot','home_principal')
def gestionar_ot(request):
    servicios = Servicio.objects.all()
    areas = Area.objects.all()
    list_ot = OT.objects.all()
    form = OTForm(request.POST or None)
    formsup = SuplementoForm(request.POST or None)
    context = {'list_ot': list_ot, 'form': form, 'servicios': servicios, 'areas': areas, 'formsup': formsup}
    return render(request, 'Gestionar_OT.html', context)


@permission_required('entrada_datos.read_actividad','home_principal')
def gestionar_actividad(request):
    actividades = TipoActividad.objects.all()
    list_act = Actividad.objects.all()
    form = ActividadForm(request.POST or None)
    context = {'list_act': list_act, 'form': form, 'tipo_actividades_list': actividades}
    return render(request, 'Gestionar_Actividad.html', context)


@permission_required('entrada_datos.read_actividad','home_principal')
def gestionar_tipo_actividad(request):
    tipo_act = TipoActividad.objects.all()
    form = TipoActividadForm(request.POST or None)
    context = {'tipo_act': tipo_act, 'form': form}
    return render(request, 'Gestionar_Tipo_Actividad.html', context)


@permission_required('entrada_datos.add_inversionista','home_principal')
def adicionar_inversionista(request):
    form = InversionistaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/inversionista/')
    cal = Inversionista.objects.all()
    context = {'list_inv': cal, 'form': form}
    return render(request, 'Gestionar_Inversionista.html', context)


@permission_required('entrada_datos.add_area','home_principal')
def adicionar_area(request):
    form = AreaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/area/')
    list_area = Area.objects.all()
    context = {'list_area': list_area, 'form': form}
    return render(request, 'Gestionar_Area.html', context)


@permission_required('entrada_datos.add_servicio','home_principal')
def adicionar_servicio(request):
    form = ServicioForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/servicio/')
    list_serv = Servicio.objects.all()
    context = {'list_serv': list_serv, 'form': form}
    return render(request, 'Gestionar_Servicio.html', context)


@permission_required('entrada_datos.add_ot','home_principal')
def adicionar_ot(request):
    servicios = Servicio.objects.all()
    areas = Area.objects.all()
    form = OTForm(request.POST or None)
    if form.is_valid():
        ot = OT(
            unidad=form.cleaned_data['unidad'],
            area=Area.objects.filter(id=request.POST['area']).get(),
            tipo_servicio=Servicio.objects.filter(id=request.POST['servicio']).get(),
            inversionista=form.cleaned_data['inversionista'],
            no_contrato=form.cleaned_data['no_contrato'],
            descripcion_ot=form.cleaned_data['descripcion_ot'],
            codigo_ot=form.cleaned_data['codigo_ot']
        )
        ot.save()
        return redirect('/orden_trabajo/')
    cal = OT.objects.all()
    context = {'list_ot': cal, 'form': form, 'servicios': servicios, 'areas': areas}
    return render(request, 'Gestionar_OT.html', context)


@permission_required('entrada_datos.add_suplemento','home_principal')
def adicionar_suplemento(request):
    form = SuplementoForm(request.POST or None)
    formot = OTForm(None)
    if form.is_valid():
        suplemento = Suplemento(
            orden_trab_id=request.POST['orden_trab'],
            monto=form.cleaned_data['monto'],
            fecha=form.cleaned_data['fecha'],
            solicitud=form.cleaned_data['solicitud'],
            usuario=request.user.first_name + ' ' + request.user.last_name,
        )
        ot = OT.objects.get(id=suplemento.orden_trab_id)
        ot.valor_contrato += suplemento.monto
        try:
            suplemento.save()
        except FieldError:
            servicios = Servicio.objects.all()
            areas = Area.objects.all()
            cal = OT.objects.all()
            context = {'list_ot': cal, 'formsup': form, 'form': formot, 'servicios': servicios, 'areas': areas,
                       'errores': 'Intentelo de nuevo. Ha ocurrido un error de Base de Datos'}
            return render(request, 'Gestionar_OT.html', context)
        except DatabaseError:
            servicios = Servicio.objects.all()
            areas = Area.objects.all()
            cal = OT.objects.all()
            context = {'list_ot': cal, 'formsup': form, 'form': formot, 'servicios': servicios, 'areas': areas,
                       'errores': 'Intentelo de nuevo. Ha ocurrido un error de Base de Datos'}
            return render(request, 'Gestionar_OT.html', context)
        ot.save()
        servicios = Servicio.objects.all()
        areas = Area.objects.all()
        cal = OT.objects.all()
        context = {'list_ot': cal, 'formsup': form, 'form': formot, 'servicios': servicios, 'areas': areas}
        return render(request, 'Gestionar_OT.html', context)
    servicios = Servicio.objects.all()
    areas = Area.objects.all()
    cal = OT.objects.all()
    context = {'list_ot': cal, 'formsup': form, 'form': formot, 'servicios': servicios, 'areas': areas}
    return render(request, 'Gestionar_OT.html', context)


@permission_required('entrada_datos.add_actividad','home_principal')
def adicionar_actividad(request):
    actividades = TipoActividad.objects.all()
    form = ActividadForm(request.POST or None)
    if form.is_valid():
        actividad = Actividad(
            orden_trab=form.cleaned_data['orden_trab'],
            tipo_act=TipoActividad.objects.filter(id=request.POST['tipo_act']).get(),
            numero=form.cleaned_data['numero'],
            descripcion_act=form.cleaned_data['descripcion_act'],
            codigo_act=form.cleaned_data['codigo_act'],
            valor_act=form.cleaned_data['valor_act']
        )
        ot = OT.objects.get(id=actividad.orden_trab.id)
        ot.valor_contrato += actividad.valor_act
        if Actividad.objects.filter(orden_trab=actividad.orden_trab, codigo_act=actividad.codigo_act).count():
            cal = Actividad.objects.all()
            context = {'list_act': cal, 'form': form, 'object': actividad, 'tipo_actividades_list': actividades,
                       'errores': 'La OT seleccionada ya tiene asignado una actividad con el mismo código.'}
            return render(request, 'Gestionar_Actividad.html', context)
        else:
            try:
                actividad.save()
            except FieldError:
                cal = Actividad.objects.all()
                context = {'list_act': cal, 'form': form, 'object': actividad, 'tipo_actividades_list': actividades,
                           'errores': 'Inténtelo de nuevo. Ha ocurrido un error de Base de Datos'}
                return render(request, 'Gestionar_Actividad.html', context)
            except DatabaseError:
                cal = Actividad.objects.all()
                context = {'list_act': cal, 'form': form, 'object': actividad, 'tipo_actividades_list': actividades,
                           'errores': 'Inténtelo de nuevo. Ha ocurrido un error de Base de Datos'}
                return render(request, 'Gestionar_Actividad.html', context)
            ot.save()
            return redirect('/actividad/')
    if request.method == 'POST':
        actividades = TipoActividad.objects.all()
        list_act = Actividad.objects.all()
        context = {'list_act': list_act, 'form': form, 'tipo_actividades_list': actividades}
        return render(request, 'Gestionar_Actividad.html', context)


@permission_required('entrada_datos.add_tipo_actividad','home_principal')
def adicionar_tipo_actividad(request):
    form = TipoActividadForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/tipo_actividad/')
    tipo_act = TipoActividad.objects.all()
    context = {'tipo_act': tipo_act, 'form': form}
    return render(request, 'Gestionar_Tipo_Actividad.html', context)


@permission_required('entrada_datos.change_inversionista','home_principal')
def editar_inversionista(request, pk):
    inversionista = Inversionista.objects.get(id=pk)
    form = InversionistaForm(request.POST or None, instance=inversionista)
    if form.is_valid():
        form.save()
        return redirect('/inversionista/')
    cal = Inversionista.objects.all()
    context = {'request': request,
               'list_inv': cal,
               'form': form,
               'edit': pk}
    context = context_add_perm(request, context, 'inversionista')
    return render(request, 'Gestionar_Inversionista.html', context)


@permission_required('entrada_datos.change_ot','home_principal')
def editar_ot(request, pk):
    ot = OT.objects.get(id=pk)
    form = OTForm(request.POST or None, instance=ot)
    if form.is_valid():
        form.save()
        return redirect('/orden_trabajo/')
    cal = OT.objects.all()
    context = {'list_ot': cal, 'form': form, 'edit': pk}
    return render(request, 'Gestionar_OT.html', context)


@permission_required('entrada_datos.cange_actividad','home_principal')
def editar_actividad(request, pk):
    actividades = TipoActividad.objects.all()
    actividad = Actividad.objects.get(id=pk)
    form = ActividadForm(request.POST or None, instance=actividad)
    if form.is_valid():
        form.save()
        return redirect('/actividad/')
    cal = Actividad.objects.all()
    context = {'list_act': cal, 'form': form, 'edit': pk, 'tipo_actividades_list': actividades}
    return render(request, 'Gestionar_Actividad.html', context)


@permission_required('entrada_datos.delete_inversionista','home_principal')
def eliminar_inversionista(request, pk):
    inversionista = Inversionista.objects.get(id=pk)
    if request.method == 'GET':
        context = {'object': inversionista}
        return render(request, 'Eliminar_Inversionista.html', context)
    else:
        from django.db import IntegrityError
        try:
            inversionista.delete()
            return redirect('/inversionista/')
        except IntegrityError:
            cal = Inversionista.objects.all()
            form = InversionistaForm(None)
            errores = 'Imposible eliminar Inversionista porque está asociado a una OT'
            context = {'request': request,
                       'list_inv': cal,
                       'form': form,
                       'errores': errores}
            context = context_add_perm(request, context, 'inversionista')

            return render(request, 'Gestionar_Inversionista.html', context)


@permission_required('entrada_datos.delete_area','home_principal')
def eliminar_area(request, pk):
    area = Area.objects.get(id=pk)
    if request.method == 'GET':
        context = {'object': area}
        return render(request, 'Eliminar_Area.html', context)
    else:
        from django.db import IntegrityError
        try:
            area.delete()
            return redirect('/area/')
        except IntegrityError:
            cal = Area.objects.all()
            form = AreaForm(None)
            context = {'list_area': cal, 'form': form,
                       'errores': 'Imposible eliminar Área porque tiene asociada al menos una OT'}
            context = context_add_perm(request, context, 'area')
            return render(request, 'Gestionar_Area.html', context)


@permission_required('entrada_datos.delete_servicio','home_principal')
def eliminar_servicio(request, pk):
    serv = Servicio.objects.get(id=pk)
    if request.method == 'GET':
        context = {'object': serv}
        return render(request, 'Eliminar_Servicio.html', context)
    else:
        from django.db import IntegrityError
        try:
            serv.delete()
            return redirect('/servicio/')
        except IntegrityError:
            cal = Servicio.objects.all()
            form = ServicioForm(None)
            context = {'list_serv': cal, 'form': form,
                       'errores': 'Imposible eliminar Servicio porque tiene asociada al menos una OT'}
            context = context_add_perm(request, context, 'servicio')
            return render(request, 'Gestionar_Servicio.html', context)


@permission_required('entrada_datos.delete_ot','home_principal')
def eliminar_ot(request, pk):
    servicios = Servicio.objects.all()
    areas = Area.objects.all()
    ot = OT.objects.get(id=pk)
    formsup = SuplementoForm(None)
    if request.method == 'GET':
        context = {'object': ot}
        return render(request, 'Eliminar_OT.html', context)
    else:
        from django.db import IntegrityError
        try:
            ot.delete()
            return redirect('/orden_trabajo/')
        except IntegrityError:
            cal = OT.objects.all()
            form = OTForm(None)
            context = {'list_ot': cal, 'form': form,
                       'errores': 'Imposible eliminar Orden de trabajo porque tiene asociado actividades',
                       'servicios': servicios, 'areas': areas, 'formsup': formsup}
            return render(request, 'Gestionar_OT.html', context)


@permission_required('entrada_datos.delete_actividad','home_principal')
def eliminar_actividad(request, pk):
    actividades = TipoActividad.objects.all()
    actividad = Actividad.objects.get(id=pk)
    if request.method == 'GET':
        context = {'object': actividad}
        return render(request, 'Eliminar_Actividad.html', context)
    else:
        from django.db import IntegrityError
        try:
            if actividad.activa:
                list_act = Actividad.objects.all()
                form = ActividadForm(None)
                context = {'list_act': list_act, 'form': form,
                           'errores': 'Imposible eliminar actividad con producción en proceso para próximo mes.',
                           'tipo_actividades_list': actividades}
                return render(request, 'Gestionar_Actividad.html', context)
            else:
                actividad.delete()
                return redirect('/actividad/')
        except IntegrityError:
            cal = Actividad.objects.all()
            form = ActividadForm(None)
            context = {'list_act': cal, 'form': form, 'errores': 'Imposible eliminar Actividad'}
            return render(request, 'Gestionar_Actividad.html', context)


@permission_required('entrada_datos.delete_tipo_actividad','home_principal')
def eliminar_tipo_actividad(request, pk):
    tipo_acti = TipoActividad.objects.get(id=pk)
    if request.method == 'GET':
        context = {'object': tipo_acti}
        return render(request, 'Eliminar_Tipo_Actividad.html', context)
    else:
        from django.db import IntegrityError
        try:
            tipo_acti.delete()
            return redirect('/tipo_actividad/')
        except IntegrityError:
            tipo_act = TipoActividad.objects.all()
            form = TipoActividadForm(None)
            context = {'tipo_act': tipo_act, 'form': form,
                       'errores': 'Imposible eliminar tipo de actividad porque tiene asociada al menos una actividad'}
            return render(request, 'Gestionar_Tipo_Actividad.html', context)


class DetalleInversionista(generic.DetailView):
    model = Inversionista
    template_name = 'Detalle_Inversionista.html'


@permission_required('entrada_datos.read_ot','home_principal')
def detalle_ot(request, pk):
    ot = OT.objects.get(id=pk)
    context = {'ot': ot}
    return render(request, 'Detalle_OT.html', context)


@permission_required('entrada_datos_read_suplemento','home_principal')
def listado_suplementos(request, pk):
    list_sup = Suplemento.objects.filter(orden_trab_id=pk)
    ot = OT.objects.get(id=pk)
    context = {'list_sup': list_sup, 'ot': ot}
    return render(request, 'Listado_Suplemento.html', context)
























