from .models import Plano
import django_filters


class PlanoFilter(django_filters.FilterSet):
    dateestado = django_filters.DateFromToRangeFilter(field_name='fecha_pago', lookup_expr='gt')
    datevpc = django_filters.DateFromToRangeFilter(field_name='fecha_vpc', lookup_expr='gt')

    class Meta:
        model = Plano
        fields = ['estado', 'vpc', 'fecha_pago', 'fecha_vpc', 'obra', 'tipo_doc', 'etapa']
