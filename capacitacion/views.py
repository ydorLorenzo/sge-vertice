from django.shortcuts import render
from django.urls import reverse_lazy

from .models import *
from principal.decorators import module_permission_required
from rechum.views import SgeListView, SgeCreateView, SgeUpdateView, SgeDetailView, SgeDeleteView


@module_permission_required('capacitacion')
def home(request):
    return render(request, 'home_cap.html')


# Actividad Capacitación
# Listar
class ModoFormacionListView(SgeListView):
    permission_required = 'capacitacion.read_modoformacion'
    raise_exception = True
    model = ModoFormacion
    template_name = 'mod-form/list.html'


# Crear
class ModoFormacionCreateView(SgeCreateView):
    permission_required = 'capacitacion.add_modoformacion'
    model = ModoFormacion
    fields = '__all__'
    template_name = 'mod-form/create.html'
    success_url = reverse_lazy('modoformacion_create')


# Editar
class ModoFormacionUpdateView(SgeUpdateView):
    permission_required = 'capacitacion.change_modoformacion'
    model = ModoFormacion
    fields = '__all__'
    template_name = 'mod-form/create.html'
    success_url = reverse_lazy('modoformacion_list')


# Detalle
class ModoFormacionDetailView(SgeDetailView):
    permission_required = 'capacitacion.read_modoformacion'
    model = ModoFormacion
    template_name = 'mod-form/detail.html'


# Delete
class ModoFormacionDeleteView(SgeDeleteView):
    permission_required = 'capacitacion.delete_modoformacion'
    model = ModoFormacion
    success_url = reverse_lazy('modoformacion_list')

# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////

# Tipos de Actividad de Capacitación
# Listar
class TipoActividadCapacitacionListView(SgeListView):
    permission_required = 'capacitacion.read_tipoactividadcapacitacion'
    raise_exception = True
    model = TipoActividadCapacitacion
    template_name = 'tipo-act-cap/list.html'


# Crear
class TipoActividadCapacitacionCreateView(SgeCreateView):
    permission_required = 'capacitacion.add_tipoactividadcapacitacion'
    model = TipoActividadCapacitacion
    fields = '__all__'
    template_name = 'tipo-act-cap/create.html'
    success_url = reverse_lazy('tipoactividadcapacitacion_create')


# Editar
class TipoActividadCapacitacionDetailView(SgeUpdateView):
    permission_required = 'capacitacion.read_tipoactividadcapacitacion'
    model = TipoActividadCapacitacion
    fields = '__all__'
    template_name = 'tipo-act-cap/detail.html'
    success_url = reverse_lazy('tipoactividadcapacitacion_list')


# Detalle
class TipoActividadCapacitacionUpdateView(SgeDetailView):
    permission_required = 'capacitacion.change_tipoactividadcapacitacion'
    model = TipoActividadCapacitacion
    template_name = 'tipo-act-cap/create.html'


# Delete
class TipoActividadCapacitacionDeleteView(SgeDeleteView):
    permission_required = 'capacitacion.delete_actividadcapacitacion'
    model = TipoActividadCapacitacion
    success_url = reverse_lazy('tipoactividadcapacitacion_list')

# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////

# Actividad Capacitación
# Listar
class ActividadCapacitacionListView(SgeListView):
    permission_required = 'capacitacion.read_actividadcapacitacion'
    raise_exception = True
    model = ActividadCapacitacion
    template_name = 'act-cap/list.html'


# Crear
class ActividadCapacitacionCreateView(SgeCreateView):
    permission_required = 'capacitacion.add_actividadcapacitacion'
    model = ActividadCapacitacion
    fields = '__all__'
    template_name = 'act-cap/create.html'
    success_url = reverse_lazy('actividadcapacitacion_create')


# Editar
class ActividadCapacitacionUpdateView(SgeUpdateView):
    permission_required = 'capacitacion.change_actividadcapacitacion'
    model = ActividadCapacitacion
    fields = '__all__'
    template_name = 'act-cap/create.html'
    success_url = reverse_lazy('actividadcapacitacion_list')


# Detalle
class ActividadCapacitacionDetailView(SgeDetailView):
    permission_required = 'capacitacion.read_actividadcapacitacion'
    model = ActividadCapacitacion
    template_name = 'act-cap/detail.html'


# Delete
class ActividadCapacitacionDeleteView(SgeDeleteView):
    permission_required = 'capacitacion.delete_actividadcapacitacion'
    model = ActividadCapacitacion
    success_url = reverse_lazy('actividadcapacitacion_list')

# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////

# Temática Capacitación
# Listar
class TematicaListView(SgeListView):
    permission_required = 'capacitacion.read_tematica'
    raise_exception = True
    model = Tematica
    template_name = 'tem-cap/list.html'


# Crear
class TematicaCreateView(SgeCreateView):
    permission_required = 'capacitacion.add_tematica'
    model = Tematica
    fields = '__all__'
    template_name = 'tem-cap/create.html'
    success_url = reverse_lazy('tematica_create')


# Editar
class TematicaUpdateView(SgeUpdateView):
    permission_required = 'capacitacion.change_tematica'
    model = Tematica
    fields = '__all__'
    template_name = 'tem-cap/create.html'
    success_url = reverse_lazy('tematica_list')


# Detalle
class TematicaDetailView(SgeDetailView):
    permission_required = 'capacitacion.read_tematica'
    model = Tematica
    template_name = 'tem-cap/detail.html'


# Delete
class TematicaDeleteView(SgeDeleteView):
    permission_required = 'capacitacion.delete_tematica'
    model = Tematica
    success_url = reverse_lazy('tematica_list')

# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////
# todo Hacer el resto, más la lógica que pueda llevar!
