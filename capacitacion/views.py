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


class TipoActCapUpdateView(SgeUpdateView):
    permission_required = 'capacitacion.change_tipo_act'
    model = TipoActividadCapacitacion
    form_class = TipoActividadCapacitacionForm
    template_name = 'tipo_actividad_capacitacion/create.html'
    success_url = reverse_lazy('tipoactividadcapacitacion_list')


class TipoActCapDetailView(SgeDetailView):
    model = TipoActividadCapacitacion
    template_name = 'tipo_actividad_capacitacion/detail.html'
    permission_required = 'capacitacion.read_tipo_act'


class TipoActCapDeleteView(SgeDeleteView):
    model = TipoActividadCapacitacion
    permission_required = 'capacitacion.delete_tipo_act'
    success_url = reverse_lazy('tipoactividadcapacitacion_list')