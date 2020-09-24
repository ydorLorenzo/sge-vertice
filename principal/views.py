from datetime import date

from django.db.models import F, Func, Value, PositiveIntegerField, DateField
from django.db.models.functions import Cast
from django.shortcuts import render

from ges_trab.models import Alta


def home_principal(request):
    today = date.today()
    workers_birthday = Alta.objects.filter(
        fecha_nac__month=today.month
    ).filter(
        fecha_nac__day__gte=today.day
    ).annotate(
        unidad_nombre=F('unidad_org__nombre'),
        dep_nombre=F('departamento__nombre'),
        dep_padre=F('departamento__dirige__nombre'),
        day=Func(Value('day'), 'fecha_nac', function='date_part'),
        day_integer=Cast('day', PositiveIntegerField()),
        fecha_cumple=Func(
            Value(today.year), Value(today.month), 'day_integer',
            function='make_date', output_field=DateField())
    ).values(
        'primer_nombre', 'segundo_nombre', 'apellidos', 'fecha_cumple',
        'unidad_nombre', 'dep_nombre', 'dep_padre', 'foto'
    ).order_by("fecha_cumple")
    return render(request, 'home_principal.html', {'birthdays': workers_birthday})
