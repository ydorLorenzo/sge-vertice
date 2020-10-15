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
from .models import *
from ges_trab.models import Trabajador, Alta
from adm.models import Departamento, UnidadOrg, Cargo, EscalaSalarial
from django.shortcuts import render
from django.urls import reverse_lazy

from .models import *
from principal.decorators import module_permission_required
from rechum.views import SgeListView, SgeCreateView, SgeUpdateView, SgeDetailView, SgeDeleteView

@module_permission_required('capacitacion')
def home(request):
    return render(request, 'home_cap.html')


class TipoActCapListView(SgeListView):
    permission_required = 'capacitacion.read_tipo_act'
    model = TipoActividadCapacitacion
    template_name = 'tipo_actividad_capacitacion/list.html'
    raise_exception = True


class TipoActCapCreateView(SgeCreateView):
    permission_required = 'capacitacion.add_tipo_act'
    model = TipoActividadCapacitacion
    form_class = TipoActividadCapacitacionForm
    template_name = 'tipo_actividad_capacitacion/create.html'
    success_url = reverse_lazy('tipoactividadcapacitacion_create')


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
