from django.contrib.auth.decorators import permission_required, user_passes_test
from django.contrib.auth.models import _user_has_module_perms
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.http.response import HttpResponseRedirect
from django.http import JsonResponse
from django.db.models import F
from django.views import generic
from django.urls import reverse_lazy

from principal.decorators import module_permission_required
from rechum.views import SgeListView, SgeCreateView, SgeUpdateView, SgeDetailView, SgeDeleteView
from .form import *


# Create your views here.
def login_up(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        acceso = authenticate(username=username, password=password)
        if acceso is not None:
            if acceso.is_active:
                login(request, acceso)
                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                else:
                    return redirect('home_principal')
            else:
                context = {'info': "Usuario desactivado."}
                return render(request, 'login.html', context)
        else:
            context = {'info': "Usuario / Contraseña incorrecta"}
            return render(request, 'login.html', context)
    else:
        return render(request, 'login.html')

@module_permission_required('adm')
def home(request):
    return render(request, 'home.html')


# Unidad Organizacional
# Listar
class UnidadOrgListView(SgeListView):
    permission_required = 'adm.read_unidadorg'
    raise_exception = True
    model = UnidadOrg
    template_name = 'unidad-org/list.html'


# Crear
class UnidadOrgCreateView(SgeCreateView):
    permission_required = 'adm.add_unidadorg'
    model = UnidadOrg
    fields = ['nombre']
    template_name = 'unidad-org/create.html'
    success_url = reverse_lazy('unidadorg_create')


# Editar
class UnidadOrgUpdateView(SgeUpdateView):
    model = UnidadOrg
    fields = ['nombre']
    template_name = 'unidad-org/create.html'
    permission_required = 'adm.change_unidadorg'
    success_url = reverse_lazy('unidadorg_list')


# Detalle
class UnidadOrgDetailView(SgeDetailView):
    model = UnidadOrg
    template_name = 'unidad-org/detail.html'
    permission_required = 'adm.read_unidadorg'


# Delete
class UnidadOrgDeleteView(SgeDeleteView):
    model = UnidadOrg
    permission_required = 'adm.delete_unidadorg'
    success_url = reverse_lazy('unidadorg_list')


# Sección Sindical
class SecSinListView(SgeListView):
    permission_required = 'adm.read_seccionsindical'
    raise_exception = True
    model = SeccionSindical
    template_name = 'seccion-sindical/list.html'


class SecSinCreateView(SgeCreateView):
    permission_required = 'adm.add_seccionsindical'
    model = SeccionSindical
    fields = ['nombre']
    template_name = 'seccion-sindical/create.html'
    success_url = reverse_lazy('seccionsindical_create')


class SecSinUpdateView(SgeUpdateView):
    permission_required = 'adm.change_seccionsindical'
    model = SeccionSindical
    fields = ['nombre']
    template_name = 'seccion-sindical/create.html'
    success_url = reverse_lazy('seccionsindical_list')


class SecSinDetailView(SgeDetailView):
    permission_required = 'adm.read_seccionsindical'
    model = SeccionSindical
    template_name = 'seccion-sindical/detail.html'


class SecSinDeleteView(SgeDeleteView):
    permission_required = 'adm.delete_seccionsindical'
    model = SeccionSindical
    success_url = reverse_lazy('seccionsindical_list')


# Departamento
class DepListView(SgeListView):
    permission_required = 'adm.read_departamento'
    raise_exception = True
    model = Departamento
    template_name = 'departamento/list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        object_list = self.model.objects.all()
        if self.kwargs.get('unidad_id'):
            unidad_id = self.kwargs.get('unidad_id')
            unidad = UnidadOrg.objects.filter(pk=unidad_id)[0]
            self.extra_context = {'unidad': unidad.nombre}
            object_list = object_list.filter(unidad_id=unidad_id)
        from django.db.models import F
        object_list = object_list.annotate(
            unidad_nombre=F('unidad__nombre'),
            seccion_nombre=F('seccion__nombre')
        )
        return super().get_context_data(object_list=object_list, **kwargs)


class DepCreateView(SgeCreateView):
    permission_required = 'adm.add_departamento'
    model = Departamento
    form_class = DepartamentoForm
    template_name = 'departamento/create.html'
    success_url = reverse_lazy('departamento_create')


class DepUpdateView(SgeUpdateView):
    permission_required = 'adm.change_departamento'
    model = Departamento
    form_class = DepartamentoForm
    template_name = 'departamento/create.html'
    success_url = reverse_lazy('departamento_list')


class DepDetailView(SgeDetailView):
    permission_required = 'adm.read_departamento'
    model = Departamento
    template_name = 'departamento/detail.html'


class DepDeleteView(SgeDeleteView):
    permission_required = 'adm.delete_departamento'
    model = Departamento
    success_url = reverse_lazy('departamento_list')


# Escala Salarial
class EscSalListView(SgeListView):
    permission_required = 'adm.read_escalasalarial'
    raise_exception = True
    model = EscalaSalarial
    template_name = 'escala-salarial/list.html'


class EscSalCreateView(SgeCreateView):
    permission_required = 'adm.add_escalasalarial'
    model = EscalaSalarial
    # form_class =
    fields = '__all__'
    template_name = 'escala-salarial/create.html'
    success_url = reverse_lazy('escalasalarial_create')


class EscSalUpdateView(SgeUpdateView):
    permission_required = 'adm.change_escalasalarial'
    model = EscalaSalarial
    # form_class = UnidadOrgForm
    fields = '__all__'
    template_name = 'escala-salarial/create.html'
    success_url = reverse_lazy('escalasalarial_list')


class EscSalDetailView(SgeDetailView):
    permission_required = 'adm.read_escalasalarial'
    model = EscalaSalarial
    template_name = 'escala-salarial/detail.html'


class EscSalDeleteView(SgeDeleteView):
    model = EscalaSalarial
    permission_required = 'adm.delete_escalasalarial'
    success_url = reverse_lazy('escalasalarial_list')


# Cargo
class CargoListView(SgeListView):
    permission_required = 'adm.read_cargo'
    raise_exception = True
    model = Cargo
    template_name = 'cargo/list.html'


class CargoCreateView(SgeCreateView):
    permission_required = 'adm.add_cargo'
    model = Cargo
    fields = ['codigo', 'nombre']
    template_name = 'cargo/create.html'
    success_url = reverse_lazy('cargo_create')


class CargoUpdateView(SgeUpdateView):
    permission_required = 'adm.change_cargo'
    model = Cargo
    fields = ['codigo', 'nombre']
    template_name = 'cargo/create.html'
    success_url = reverse_lazy('cargo_list')


class CargoDetailView(SgeDetailView):
    permission_required = 'adm.read_cargo'
    model = Cargo
    template_name = 'cargo/detail.html'


class CargoDeleteView(SgeDeleteView):
    permission_required = 'adm.delete_cargo'
    model = Cargo
    success_url = reverse_lazy('cargo_list')


# Calificación
class CalListView(SgeListView):
    permission_required = 'adm.read_calificacion'
    raise_exception = True
    model = Calificacion
    template_name = 'calificacion/list.html'


class CalCreateView(SgeCreateView):
    permission_required = 'adm.add_calificacion'
    model = Calificacion
    fields = ['codigo', 'nombre']
    template_name = 'calificacion/create.html'
    success_url = reverse_lazy('calificacion_create')


class CalUpdateView(SgeUpdateView):
    permission_required = 'adm.change_calificacion'
    model = Calificacion
    fields = ['codigo', 'nombre']
    template_name = 'calificacion/create.html'
    success_url = reverse_lazy('calificacion_list')


class CalDetailView(SgeDetailView):
    permission_required = 'adm.read_calificacion'
    model = Calificacion
    template_name = 'calificacion/detail.html'


class CalDeleteView(SgeDeleteView):
    permission_required = 'adm.delete_calificacion'
    model = Calificacion
    success_url = reverse_lazy('calificacion_list')


# Unidad Organizacional
# Listar
class EspListView(SgeListView):
    permission_required = 'adm.read_especialidad'
    raise_exception = True
    model = Especialidad
    template_name = 'especialidad/list.html'


class EspCreateView(SgeCreateView):
    permission_required = 'adm.add_especialidad'
    model = Especialidad
    form_class = EspecialidadForm
    template_name = 'especialidad/create.html'
    success_url = reverse_lazy('especialidad_create')


class EspUpdateView(SgeUpdateView):
    permission_required = 'adm.change_especialidad'
    model = Especialidad
    form_class = EspecialidadForm
    template_name = 'especialidad/create.html'
    success_url = reverse_lazy('especialidad_list')


class EspDetailView(SgeDetailView):
    permission_required = 'adm.read_especialidad'
    model = Especialidad
    template_name = 'especialidad/detail.html'


class EspDeleteView(SgeDeleteView):
    permission_required = 'adm.delete_especialidad'
    model = Especialidad
    success_url = reverse_lazy('especialidad_list')


def logout_view(request):
    logout(request)


# Listar
#@permission_required('adm.read_unidad_org','home_principal')
def gestionar_unidad_org(request):
    list_unidad_org = UnidadOrg.objects.all()
    form = CalificacionForm(request.POST or None)
    context = {'list_unidad_org': list_unidad_org, 'form': form}
    return render(request, 'Gestionar_Unidad_Organizacional.html', context)

#@permission_required('adm.read_departamento','home_principal')
def gestionar_departamento(request):
    list_departamentos = Departamento.objects.all().select_related("unidad").select_related("dirige").select_related(
        "seccion")
    form = DepartamentoForm(request.POST or None)
    context = {'list_departamentos': list_departamentos, 'form': form}
    return render(request, 'Gestionar_Departamento.html', context)

#@permission_required('adm.read_calificacion','home_principal')
def gestionar_calificacion(request):
    list_calificacion = Calificacion.objects.all()
    form = CalificacionForm(request.POST or None)
    context = {'list_calificacion': list_calificacion, 'form': form}
    return render(request, 'Gestionar_Calificacion.html', context)

#@permission_required('adm.read_especialidad','home_principal')
def gestionar_especialidad(request):
    list_especialidad = Especialidad.objects.all().select_related("calificacion")
    form = EspecialidadForm(request.POST or None)
    context = {'list_especialidad': list_especialidad, 'form': form}
    return render(request, 'Gestionar_Especialidad.html', context)

#@permission_required('adm.read_seccionsindical','home_principal')
def gestionar_seccion_sindical(request):
    list_ss = SeccionSindical.objects.all()
    form = SeccionSindicalForm(request.POST or None)
    context = {'list_ss': list_ss, 'form': form}
    return render(request, 'Gestionar_Seccion_Sindical.html', context)

#@permission_required('adm.read_cargo','home_principal')
def gestionar_cargo(request):
    list_cargo = Cargo.objects.all()
    form = CargoForm(request.POST or None)
    context = {'list_cargo': list_cargo, 'form': form}
    return render(request, 'Gestionar_Cargo.html', context)


# Adicionar

#@permission_required('adm.add_unidad_org','home_principal')
def adicionar_uo(request):
    form = UnidadOrgForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/unidad_organizacional/')
    cal = UnidadOrg.objects.all()
    context = {'list_unidad_org': cal, 'form': form}
    return render(request, 'Gestionar_Unidad_Organizacional.html', context)

#@permission_required('adm.add_seccionsindical','home_principal')
def adicionar_ss(request):
    form = SeccionSindicalForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/seccion_sindical/')
    cal = SeccionSindical.objects.all()
    context = {'list_ss': cal, 'form': form}
    return render(request, 'Gestionar_Seccion_Sindical.html', context)

#@permission_required('adm.add_departamento','home_principal')
def adicionar_departamento(request):
    form = DepartamentoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/departamento/')
    cal = Departamento.objects.all().select_related("unidad").select_related("dirige").select_related(
        "seccion")
    context = {'list_departamentos': cal, 'form': form}
    return render(request, 'Gestionar_Departamento.html', context)


#@permission_required('adm.add_cargo','home_principal')
def adicionar_cargo(request):
    form = CargoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/cargo/')
    cal = Cargo.objects.all()
    context = {'list_cargo': cal, 'form': form}
    return render(request, 'Gestionar_Cargo.html', context)

#@permission_required('adm.add_calificacion','home_principal')
def adicionar_calificacion(request):
    form = CalificacionForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/calificacion/')
    cal = Calificacion.objects.all()
    context = {'list_calificacion': cal, 'form': form}
    return render(request, 'Gestionar_Calificacion.html', context)

#@permission_required('adm.add_especialidad','home_principal')
def adicionar_especialidad(request):
    form = EspecialidadForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/especialidad/')
    cal = Especialidad.objects.all().select_related("calificacion")
    context = {'list_especialidad': cal, 'form': form}
    return render(request, 'Gestionar_Especialidad.html', context)


# Editar

#@permission_required('adm.change_unidad_org','home_principal')
def editar_uo(request, pk):
    unidad = UnidadOrg.objects.get(id=pk)
    form = UnidadOrgForm(request.POST or None, instance=unidad)
    if form.is_valid():
        form.save()
        return redirect('/unidad_organizacional/')
    cal = UnidadOrg.objects.all()
    context = {'list_unidad_org': cal, 'form': form, 'edit': pk}
    return render(request, 'Gestionar_Unidad_Organizacional.html', context)

#@permission_required('adm.change_seccionsindical','home_principal')
def editar_ss(request, pk):
    seccion = SeccionSindical.objects.get(id=pk)
    form = SeccionSindicalForm(request.POST or None, instance=seccion)
    if form.is_valid():
        form.save()
        return redirect('/seccion_sindical/')
    cal = SeccionSindical.objects.all()
    context = {'list_ss': cal, 'form': form, 'edit': pk}
    return render(request, 'Gestionar_Seccion_Sindical.html', context)

#@permission_required('adm.change_departamento','home_principal')
def editar_departamento(request, pk):
    departamento = Departamento.objects.get(id=pk)
    form = DepartamentoForm(request.POST or None, instance=departamento)
    if form.is_valid():
        form.save()
        return redirect('/departamento/')
    cal = Departamento.objects.all().select_related("unidad").select_related("dirige").select_related("seccion")
    context = {'list_departamentos': cal, 'form': form, 'edit': pk}
    return render(request, 'Gestionar_Departamento.html', context)


#@permission_required('adm.change_cargo','home_principal')
def editar_cargo(request, pk):
    cargo = Cargo.objects.get(id=pk)
    form = CargoForm(request.POST or None, instance=cargo)
    if form.is_valid():
        form.save()
        return redirect('/cargo/')
    cal = Cargo.objects.all()
    context = {'list_cargo': cal, 'form': form, 'edit': pk}
    return render(request, 'Gestionar_Cargo.html', context)

#@permission_required('adm.change_calificacion','home_principal')
def editar_calificacion(request, pk):
    calificacion = Calificacion.objects.get(id=pk)
    form = CalificacionForm(request.POST or None, instance=calificacion)
    if form.is_valid():
        form.save()
        return redirect('/calificacion/')
    cal = Calificacion.objects.all()
    context = {'list_calificacion': cal, 'form': form, 'edit': pk}
    return render(request, 'Gestionar_Calificacion.html', context)

#@permission_required('adm.change_especialidad','home_principal')
def editar_especialidad(request, pk):
    especialidad = Especialidad.objects.get(id=pk)
    form = EspecialidadForm(request.POST or None, instance=especialidad)
    if form.is_valid():
        form.save()
        return redirect('/especialidad/')
    cal = Especialidad.objects.all().select_related("calificacion")
    context = {'list_especialidad': cal, 'form': form, 'edit': pk}
    return render(request, 'Gestionar_Especialidad.html', context)


# Visualizar detalle

#@permission_required('adm.read_unidad_org','home_principal')
class DetalleUo(generic.DetailView):
    model = UnidadOrg
    template_name = 'Detalle_Unidad_Organizacional.html'

#@permission_required('adm.read_seccionsindical','home_principal')
class DetalleSs(generic.DetailView):
    model = SeccionSindical
    template_name = 'Detalle_Seccion_Sindical.html'

#@permission_required('adm.read_departamento','home_principal')
class DetalleDepartamento(generic.DetailView):
    model = Departamento
    template_name = 'Detalle_Departamento.html'

#@permission_required('adm.read_cargo','home_principal')
class DetalleCargo(generic.DetailView):
    model = Cargo
    template_name = 'Detalle_Cargo.html'

#@permission_required('adm.read_calificacion','home_principal')
class DetalleCalificacion(generic.DetailView):
    model = Calificacion
    template_name = 'Detalle_Calificacion.html'

#@permission_required('adm.read_especialidad','home_principal')
class DetalleEspecialidad(generic.DetailView):
    model = Especialidad
    template_name = 'Detalle_Especialidad.html'


# Eliminar
#@permission_required('adm.delete_unidad_org','home_principal')
def eliminar_uo(request, pk):
    unidad = UnidadOrg.objects.get(id=pk)
    if request.method == 'GET':
        context = {'object': unidad}
        return render(request, 'Eliminar_Unidad_Organizacional.html', context)
    else:
        from django.db import IntegrityError
        try:
            unidad.delete()
            return redirect('/unidad_organizacional/')
        except IntegrityError:
            cal = UnidadOrg.objects.all()
            form = UnidadOrgForm(None)
            context = {'list_unidad_org': cal, 'form': form,
                       'errores': 'Imposible eliminar la Unidad Organizacional porque tiene al menos un Departamento '
                                  'asociado.'}
            return render(request, 'Gestionar_Unidad_Organizacional.html', context)

#@permission_required('adm.delete_seccionsindical','home_principal')
def eliminar_ss(request, pk):
    seccion = SeccionSindical.objects.get(id=pk)
    if request.method == 'GET':
        context = {'object': seccion}
        return render(request, 'Eliminar_Seccion_Sindical.html', context)
    else:
        from django.db import IntegrityError
        try:
            seccion.delete()
            return redirect('/seccion_sindical/')
        except IntegrityError:
            cal = SeccionSindical.objects.all()
            form = SeccionSindicalForm(None)
            context = {'list_ss': cal, 'form': form,
                       'errores': 'Imposible eliminar Sección porque tiene al menos un Departamento asociado.'}
            return render(request, 'Gestionar_Seccion_Sindical.html', context)

#@permission_required('adm.delete_departamento','home_principal')
def eliminar_departamento(request, pk):
    departamento = Departamento.objects.get(id=pk)
    if request.method == 'GET':
        context = {'object': departamento}
        return render(request, 'Eliminar_Departamento.html', context)
    else:
        from django.db import IntegrityError
        try:
            departamento.delete()
            return redirect('/departamento/')
        except IntegrityError:
            cal = Departamento.objects.all().select_related("unidad").select_related("dirige").select_related("seccion")
            form = DepartamentoForm(None)
            context = {'list_departamentos': cal, 'form': form,
                       'errores': 'Imposible eliminar Departamento porque está asociado a una plantilla.'}
            return render(request, 'Gestionar_Departamento.html', context)


#@permission_required('adm.delete_cargo','home_principal')
def eliminar_cargo(request, pk):
    cargo = Cargo.objects.get(id=pk)
    if request.method == 'GET':
        context = {'object': cargo}
        return render(request, 'Eliminar_Cargo.html', context)
    else:
        from django.db import IntegrityError
        try:
            cargo.delete()
            return redirect('/cargo/')
        except IntegrityError:
            cal = Cargo.objects.all()
            form = CargoForm(None)
            context = {'list_cargo': cal, 'form': form,
                       'errores': 'Imposible eliminar Cargo porque está asociado a una plantilla.'}
            return render(request, 'Gestionar_Cargo.html', context)

#@permission_required('adm.delete_calificacion','home_principal')
def eliminar_calificacion(request, pk):
    calificacion = Calificacion.objects.get(id=pk)
    if request.method == 'GET':
        context = {'object': calificacion}
        return render(request, 'Eliminar_Calificacion.html', context)
    else:
        from django.db import IntegrityError
        try:
            calificacion.delete()
            return redirect('/calificacion/')
        except IntegrityError:
            cal = Calificacion.objects.all()
            form = CalificacionForm(None)
            context = {'list_calificacion': cal, 'form': form,
                       'errores': 'Imposible eliminar la calificación porque está asociada a un trabajador.'}
            return render(request, 'Gestionar_Calificacion.html', context)

#@permission_required('adm.delete_especialidad','home_principal')
def eliminar_especialidad(request, pk):
    especialidad = Especialidad.objects.get(id=pk)
    if request.method == 'GET':
        context = {'object': especialidad}
        return render(request, 'Eliminar_Especialidad.html', context)
    else:
        from django.db import IntegrityError
        try:
            especialidad.delete()
            return redirect('/especialidad/')
        except IntegrityError:
            cal = Especialidad.objects.all().select_related("calificacion")
            form = EspecialidadForm(None)
            context = {'list_especialidad': cal, 'form': form,
                       'errores': 'Imposible eliminar Especialidad porque está asociada a un trabajador.'}
            return render(request, 'Gestionar_Especialidad.html', context)
