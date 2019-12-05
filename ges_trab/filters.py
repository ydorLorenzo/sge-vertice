from .models import Trabajador
import django_filters


class TrabajadorFilter(django_filters.FilterSet):
    datecontrato = django_filters.DateFromToRangeFilter(field_name='fecha_contrato', lookup_expr='gt')
    datealta = django_filters.DateFromToRangeFilter(field_name='fecha_alta', lookup_expr='gt')
    datenac = django_filters.DateFromToRangeFilter(field_name='fecha_nac', lookup_expr='gt')

    class Meta:
        model = Trabajador
        fields = ['etnia', 'sexo', 'estado_civil', 'unidad_org', 'departamento', 'cargo', 'categoria', 't_plantilla',
                  't_contrato', 's_pago', 'escala_salarial', 'por_cies', 'por_anti', 'fecha_contrato', 'fecha_alta',
                  'cat_cient', 'calificacion', 'centro_graduacion', 'tipo_tecnico', 'fecha_nac', 'categoria',
                  'departamento', 'por_anti', 'orga_defensa', 'anno_graduado', 'motivo_alta']
