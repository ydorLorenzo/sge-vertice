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
    permission_required = 'adm.read_actividadcapacitacion'
    raise_exception = True
    model = ActividadCapacitacion
    template_name = 'act-cap/list.html'


# Crear
class ActCapCreateView(SgeCreateView):
    permission_required = 'adm.add_actividadcapacitacion'
    model = ActividadCapacitacion
    fields = ['nombre']
    template_name = 'act-cap/create.html'
    success_url = reverse_lazy('actividadcapacitacion_create')


# Editar
class ActCapUpdateView(SgeUpdateView):
    model = ActividadCapacitacion
    fields = ['nombre']
    template_name = 'act-cap/create.html'
    permission_required = 'adm.change_actividadcapacitacion'
    success_url = reverse_lazy('actividadcapacitacion_list')


# Detalle
class ActCapDetailView(SgeDetailView):
    model = ActividadCapacitacion
    template_name = 'act-cap/detail.html'
    permission_required = 'adm.read_actividadcapacitacion'


# Delete
class ActCapDeleteView(SgeDeleteView):
    model = ActividadCapacitacion
    permission_required = 'adm.delete_actividadcapacitacion'
    success_url = reverse_lazy('actividadcapacitacion_list')


# todo Hacer el resto, más la lógica que pueda llevar!
