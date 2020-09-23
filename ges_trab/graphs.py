from django.db.models import Count, Q
from highcharts.views import HighChartsPieView
from datetime import date

from adm.models import UnidadOrg, Departamento
from ges_trab.models import Alta, BajaOther

to_abreviatura = {
    'Oficina Central': 'Oficina Central',
    'Unidad de Gestión y Dirección de Diseño': 'UGDD',
    'Unidad de Servicios Técnicos de Ingeniería': 'USTI',
    'Unidad de Gestión de Dirección de la Construcc 1': 'UGDC 1',
    'Unidad de Gestión de Dirección de la Construcc 3': 'UGDC 3',
    'Unidad de Gestión de Dirección de la Construcc 5': 'UGDC 5',
    'Unidad Empresarial de Base Servicios Generales': "UEB Servicios Generales"
}


class BarDrilldownDept(HighChartsPieView):
    title = 'Trabajadores'
    chart_type = 'bar'
    tooltip = {"headerFormat": '<span style="font-size: 10px">{point.key}</span><br/>'}
    tooltip_point_format = '<span style="color:{point.color}">●</span> Trabajadores: <b>{point.y}</b><br/>'
    queryset = Departamento.objects.annotate(
        count=Count('trabajadores', filter=Q(trabajadores__fecha_baja__isnull=True))).order_by('unidad_id', 'codigo')
    drill_up_queryset = {un.id: to_abreviatura[un.nombre] for un in UnidadOrg.objects.all().order_by('id')}
    exporting = {
        'enabled': False
    }

    def get_data(self):
        data = super().get_data()
        data['lang'] = {'drillUpText': '◁ Volver a {series.name}'}
        data['yAxis'] = {'title': {'text': 'Cantidad de trabajadores'}}
        data['xAxis'] = {'categories': [], 'className': 'x-axis-report'}
        return data

    @property
    def series(self):
        unidades = []
        self._drilldown = {'drillUpButton': {'position': {'y': -15}}, 'series': []}
        prev_unidad = -1
        un_drill_index = 0
        dep_drill_index = 0
        data_index = 0
        for dep in self.queryset:
            if dep.unidad_id != prev_unidad:
                prev_unidad = dep.unidad_id
                self._drilldown['series'].append({
                    'id': f'u{dep.unidad_id}',
                    'name': self.drill_up_queryset[prev_unidad],
                    'data': []
                })
                un_drill_index = len(self._drilldown['series']) - 1
                unidades.append(
                    {'y': dep.count, 'drilldown': f'u{prev_unidad}', 'name': self.drill_up_queryset[prev_unidad]})
            else:
                unidades[-1]['y'] += dep.count
            if dep.dirige_id is None:
                self._drilldown['series'].append({
                    'id': f'd{dep.id}',
                    'name': dep.nombre,
                    'data': []
                })
                dep_drill_index = len(self._drilldown['series']) - 1
                self._drilldown['series'][un_drill_index]['data'].append(
                    {'name': dep.nombre, 'y': dep.count, 'drilldown': f'd{dep.id}'})
                self._drilldown['series'][dep_drill_index]['data'].append({'name': dep.nombre, 'y': dep.count})
                data_index = len(self._drilldown['series'][un_drill_index]['data']) - 1
            else:
                self._drilldown['series'][un_drill_index]['data'][data_index]['y'] += dep.count
                self._drilldown['series'][dep_drill_index]['data'].append({'name': dep.nombre, 'y': dep.count})

        series = [
            {
                'name': 'Empresa',
                'colorByPoint': 'true',
                'data': []
            }
        ]
        for unidad in unidades:
            series[0]['data'].append({
                'name': unidad['name'],
                'y': unidad['y'],
                'drilldown': str(unidad['drilldown'])
            })
        return series


class PieGenderChart(HighChartsPieView):
    title = 'Distribución por Géneros'
    tooltip = {"headerFormat": '<span style="font-size: 10px">{point.key}</span><br/>'}
    tooltip_point_format = '<span style="color:{point.color}">●</span> Trabajadores: <b>{point.y}</b><br/>'
    exporting = {
        'enabled': False
    }
    model = Alta

    def get_data(self):
        data = super(PieGenderChart, self).get_data()
        return data

    @property
    def series(self):
        list_gender = self.model.objects.values('sexo').annotate(count=Count('id')).values('sexo', 'count')
        dict_gender = {'M': 'Hombres', 'F': 'Mujeres'}
        series = [
            {
                'name': 'Empresa',
                'colorByPoint': 'true',
                'data': [[dict_gender[x['sexo']], x['count']] for x in list_gender]
            }
        ]
        return series


class PieEtniaChart(HighChartsPieView):
    title = 'Distribución por Etnia'
    tooltip = {"headerFormat": '<span style="font-size: 10px">{point.key}</span><br/>'}
    tooltip_point_format = '<span style="color:{point.color}">●</span> Trabajadores: <b>{point.y}</b><br/>'
    exporting = {
        'enabled': False
    }
    model = Alta

    def get_data(self):
        data = super(PieEtniaChart, self).get_data()
        return data

    @property
    def series(self):
        list_etnia = self.model.objects.values('etnia').annotate(count=Count('id')).values('etnia', 'count')
        dict_etnia = {'N': 'Negros', 'B': 'Blancos', 'M': 'Mestizos'}
        series = [
            {
                'name': 'Empresa',
                'colorByPoint': 'true',
                'data': [[dict_etnia[x['etnia']], x['count']] for x in list_etnia]
            }
        ]
        return series


class AgePyramidChart(HighChartsPieView):
    title = 'Pirámide de edades'
    chart_type = 'pyramid'
    tooltip_point_format = '<span style="color:{point.color}">●</span> Trabajadores: <b>{point.y}</b><br/>'
    exporting = {'enabled': False}
    plot_options = {
        'pyramid': {'width': '50%', 'animation': True}
    }
    model = BajaOther
    now = date.today()

    def get_data(self):
        data = super().get_data()
        return data

    @property
    def series(self):
        now = date.today()
        date_60 = now.replace(year=now.year - 60)
        try:
            date_30 = now.replace(year=now.year - 30)
            date_50 = now.replace(year=now.year - 50)
        except ValueError:
            date_30 = now.replace(year=now.year - 30, day=now.day - 1)
            date_50 = now.replace(year=now.year - 50, day=now.day - 1)
        queryset = self.model.objects.aggregate(
            _30=Count('id', filter=Q(fecha_nac__gte=date_30)),
            _31_50=Count('id', filter=(Q(fecha_nac__lt=date_30) & Q(fecha_nac__gte=date_50))),
            _51_60=Count('id', filter=(Q(fecha_nac__lt=date_50) & Q(fecha_nac__gte=date_60))),
            _60=Count('id', filter=Q(fecha_nac__lt=date_60))
        )
        _sum = sum(queryset.values())
        list_ranges = [
            ['Menores de 31 <strong>(%.1f%s)</strong>' % (queryset["_30"] / _sum * 100, '%'), queryset['_30']],
            [f'De 31 a 50 <strong>(%.1f%s)</strong>' % (queryset["_31_50"] / _sum * 100, '%'), queryset['_31_50']],
            [f'De 51 a 60 <strong>(%.1f%s)</strong>' % (queryset["_51_60"] / _sum * 100, '%'), queryset['_51_60']],
            [f'Mayores de 60 <strong>(%.1f%s)</strong>' % (queryset["_60"] / _sum * 100, '%'), queryset['_60']],
        ]
        list_ranges.sort(key=lambda x: x[1], reverse=True)
        return [
            {
                'name': 'Empresa',
                'colorByPoint': 'true',
                'data': list_ranges
            }
        ]
