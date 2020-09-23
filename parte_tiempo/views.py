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
    dummy_events = [
        {
            'title': 'All day event',
            'start': '2020-09-01'
        },
        {
            'title': 'Long Event',
            'start': '2020-09-07',
            'end': '2020-09-10'
        },
        {
            'title': 'Repeating Event',
            'start': '2020-09-09T16:00:00'
        },
        {
            'title': 'Repeating Event',
            'start': '2020-09-16T16:00:00'
        },
        {
            'title': 'Conference',
            'start': '2020-09-11',
            'end': '2020-09-13'
        },
        {
            'title': 'Meeting',
            'start': '2020-09-12T10:30:00',
            'end': '2020-09-12T12:30:00'
        },
        {
            'title': 'Lunch',
            'start': '2020-09-12T12:00:00'
        },
        {
            'title': 'Meeting',
            'start': '2020-09-12T14:30:00'
        },
        {
            'title': 'Happy Hour',
            'start': '2020-09-12T17:30:00'
        },
        {
            'title': 'Dinner',
            'start': '2020-09-12T20:00:00'
        },
        {
            'title': 'Birthday Party',
            'start': '2020-09-13T07:00:00'
        },
        {
            'title': 'Click for Google',
            'start': '2020-09-28'
        }
    ]

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
        "dummy_events": dummy_events,
        "get_event_types": get_event_types,
        "trabajadores": trabajadores
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
    print(all_events)
    return all_events


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
        form.instance.afecta_a = Alta.objects.get(id=trabajador_id)
        form.instance.agregado_por = self.request.user
        return super(EventoCreate, self).form_valid(form)
