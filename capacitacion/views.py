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
class ActCapListView(SgeListView):
    permission_required = 'capacitacion.read_actividadcapacitacion'
    raise_exception = True
    model = ActividadCapacitacion
    template_name = 'act-cap/list.html'


# Crear
class ActCapCreateView(SgeCreateView):
    permission_required = 'capacitacion.add_actividadcapacitacion'
    model = ActividadCapacitacion
    fields = '__all__'
    template_name = 'act-cap/create.html'
    success_url = reverse_lazy('actividadcapacitacion_create')


# Editar
class ActCapUpdateView(SgeUpdateView):
    permission_required = 'capacitacion.change_actividadcapacitacion'
    model = ActividadCapacitacion
    fields = '__all__'
    template_name = 'act-cap/create.html'
    success_url = reverse_lazy('actividadcapacitacion_list')


# Detalle
class ActCapDetailView(SgeDetailView):
    permission_required = 'capacitacion.read_actividadcapacitacion'
    model = ActividadCapacitacion
    template_name = 'act-cap/detail.html'


# Delete
class ActCapDeleteView(SgeDeleteView):
    permission_required = 'capacitacion.delete_actividadcapacitacion'
    model = ActividadCapacitacion
    success_url = reverse_lazy('actividadcapacitacion_list')


# todo Hacer el resto, más la lógica que pueda llevar!
