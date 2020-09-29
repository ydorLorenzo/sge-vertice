import datetime
import json
from datetime import date, timedelta

from django.db.models import F
from django.shortcuts import render, HttpResponse
from django.urls import reverse_lazy

from adm.models import UnidadOrg
from ges_trab.models import Alta
from rechum.views import SgeCreateView
from .forms import EventoCreateForm
from .models import Evento, Calendario


def events(request):
    all_events = Evento.objects.all()
    get_event_types = Evento.objects.only('tipo_evento')
    calendars = Calendario.objects.all()
    unidades = UnidadOrg.objects.all()

    if request.GET:
        # Events in events table
        if request.GET.get('tipo_evento', 'all') == 'all':
            all_events = Evento.objects.all()
        else:
            all_events = Evento.objects.filter(tipo_evento__siglas__icontains=request.GET.get('tipo_evento'))
        return HttpResponse(json.dumps(refract_events(all_events)))

    context = {
        "calendars": calendars,
        "events": refract_events(all_events),
        "get_event_types": get_event_types,
        "unidades": unidades
    }
    return render(request, 'calendario-general.html', context)


def refract_events(events_qs):
    all_events = events_qs.annotate(
        calendar=F('tipo_evento__calendario'),
        calendar_id=F('tipo_evento__calendario_id'),
        title=F('nombre'),
        start=F('fecha_inicio'),
        end=F('fecha_fin'),
        color=F('tipo_evento__color')
    ).values('id', 'calendar', 'calendar_id', 'title', 'start', 'end', 'color')
    return all_events


class EventoCreate(SgeCreateView):
    model = Evento
    form_class = EventoCreateForm
    permission_required = 'parte_tiempo.add_evento'
    template_name = 'evento/create.html'
    success_url = reverse_lazy('evento_list')

    def get_context_data(self, **kwargs):
        context = super(EventoCreate, self).get_context_data()
        tmp = self.request.GET.get('date', datetime.datetime.today().strftime('%Y-%m-%d')).split('-')
        tmp.reverse()
        context['fecha_inicio'] = '/'.join(tmp)
        return context

    def form_valid(self, form):
        trabajador_id = self.request.GET.get('trabajador', None)
        form.instance.afecta_a = Alta.objects.get(id=trabajador_id)
        form.instance.agregado_por = self.request.user
        return super(EventoCreate, self).form_valid(form)


######################
# Utility functions
#
def daterange(start_date, end_date):
    for n in range(int((date(end_date) - date(start_date)).days)):
        yield date(start_date) + timedelta(n)
