import json, datetime

from django.shortcuts import render, HttpResponse
from django.urls import reverse_lazy
from django.db.models import F

from .models import Evento, Calendario
from ges_trab.models import Alta
from .forms import EventoCreateForm
from rechum.views import SgeCreateView


def events(request):
    all_events = Evento.objects.all()
    get_event_types = Evento.objects.only('tipo_evento')
    calendars = Calendario.objects.all()
    trabajadores = Alta.objects.all().order_by('departamento__codigo', 'org_plantilla')

    if request.GET:
        # Events in events table
        if request.GET.get('tipo_evento', 'all') == 'all':
            all_events = Evento.objects.all()
        else:
            all_events = Evento.objects.filter(tipo_evento__siglas__icontains=request.GET.get('tipo_evento'))
        all_events = all_events.annotate(
            calendar=F('tipo_evento__calendario'),
            calendar_id=F('tipo_evento__calendario_id'),
            title=F('nombre'),
            start=F('fecha_inicio'),
            end=F('fecha_fin'),
            color=F('tipo_evento__color')
        ).values_list('id', 'calendar', 'calendar_id', 'title', 'start', 'end', 'color')
        return HttpResponse(json.dumps(all_events))

    context = {
        "calendars": calendars,
        "events": all_events,
        "get_event_types": get_event_types,
        "trabajadores": trabajadores
    }
    return render(request, 'calendario-general.html', context)


class EventoCreate(SgeCreateView):
    model = Evento
    form_class = EventoCreateForm
    permission_required = 'parte_tiempo.add_evento'
    template_name = 'evento/create.html'
    success_url = reverse_lazy('evento_list')

    def get_context_data(self, **kwargs):
        context = super(EventoCreate, self).get_context_data()
        context['fecha_inicio'] = self.request.GET.get('date', datetime.datetime.today().strftime('%d/%m/%Y'))
        return context

    def form_valid(self, form):
        trabajador_id = self.request.GET.get('trabajador', None)
        fecha = self.request.GET.get('date', datetime.datetime.today().strftime('%Y-%m-%d'))
        form.instance.afecta_a = Alta.objects.get(id=trabajador_id)
        form.instance.fecha_inicio = fecha
        form.instance.agregado_por = self.request.user
        return super(EventoCreate, self).form_valid(form)
