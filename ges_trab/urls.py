from django.urls import path, include, register_converter, re_path

from principal.decorators import module_permission_required
from rechum.converters import FourDigitsYearConverter, TwoDigitsMonthConverter, DateConverter
from rechum.views import SgeTemplateView
from . import views, models, graphs

register_converter(FourDigitsYearConverter, 'yyyy')
register_converter(TwoDigitsMonthConverter, 'mm')
register_converter(DateConverter, 'date')

urlpatterns = [
    path('trabajadores/', include([
        path('', module_permission_required('ges_trab')(SgeTemplateView.as_view(template_name='ges-trab_home.html')),
             name='ges_trab_home'),
        path('trabajador_list/', include([
            path('', views.TrabListView.as_view(), name='trabajador_list'),
            path('agregar/', views.TrabCreateView.as_view(), name='trabajador_create'),
            path('<int:pk>/', views.TrabDetailView.as_view(), name='trabajador_detail'),
            path('<int:pk>/actualizar/', views.TrabUpdateView.as_view(), name='trabajador_update'),
            path('<int:pk>/eliminar/', views.TrabDeleteView.as_view(), name='trabajador_delete')
        ])),
        path('bajas_list/', include([
            path('', views.BajaListView.as_view(), name='bajaother_list'),
            path('agregar/', views.BajaCreateView.as_view(), name='bajaother_create'),
            path('<int:pk>/', views.BajaDetailView.as_view(), name='bajaother_detail')
        ])),
        path('movimiento_nomina/<int:pk>/', views.exportar_movimiento_nomina, name='MovimientoNomina'),
        path('movimiento_nomina_alta/<int:pk>/', views.exportar_movimiento_nomina_alta, name='MovimientoNominaAlta'),
        path('movimiento_nomina_baja/<int:pk>/', views.exportar_movimiento_nomina_baja, name='MovimientoNominaBaja'),
        path('acuerdo_conf/<int:pk>/', views.exportar_acuerdo, name='AcuerdoConfidencialidad'),
        path('solic_cuenta_usuario/<int:pk>/', views.exportar_solic_cuenta_user, name='SolicCuentaUser'),
        path('contrato_pdf/<int:pk>/', views.exportar, name='ReporteContrato'),
        path('movimiento/', views.listar_movimiento, name='ListarMovimiento'),
        path('disponibles/', views.listar_disponible, name='TrabajadoresDisponibles'),
        path('trabajador/', views.gestionar_trabajador, name='GestionarTrabajador'),
        path('bajas/', views.gestionar_bajatrabajador, name='GestionarBaja'),
        path('ad_trabajador/', views.adicionar_trabajador_inline, name='AdicionarTrabajador'),
        path('baja/<int:pk>/', views.bajaeliminar, name='bajaeliminar'),
        path('editar_mov/<int:pk>/', views.editar_movimiento, name='EditarMovimiento'),
        path('editar_baj/<int:pk>/', views.editar_baja, name='EditarBaja'),
        path('eliminar_familiar/<int:nucleofamiliar_id>/', views.eliminar_familiar, name='EliminarFamiliar'),
        path('alta/<int:pk>/', views.daralta, name='altabaja'),
        path('select_salarioescala/<int:pk>/', views.salarioescala_por_escalasarial, name='SelectEscalasalarial'),
        path('select_especialidad/<int:calificacion_id>/', views.calificacion_especialidad, name='CalificacionEspecialidad'),
        path('select_cargos/<int:departamento_id>/', views.cargos_disponibles, name='CargosDisponibles'),
        path('ed_trabajador/<int:trabajador_id>/', views.adicionar_trabajador_inline, name='EditarTrabajador'),
        path('ver_codigo_interno/', views.check_codigo, name='ver_codigo_interno'),
        path('ver_codigo_interno/<int:pk>', views.check_codigo, name='ver_codigo_interno'),
        path('ver_ci/', views.check_ci, name='ver_ci'),
        path('ver_ci/<int:pk>', views.check_ci, name='ver_ci'),
        path('ver_plantilla/', views.check_plantilla, name='ver_plantilla'),
        path('ver_usuario/', views.check_usuario, name='ver_usuario'),
        path('ver_usuario/<int:pk>', views.check_usuario, name='ver_usuario'),
    ])),
    path('exportar_movimientos/', views.exportar_movimientos, name='ExportarReporteMovimientos'),
    path('exportar_suplemento_contrato/<int:pk>/', views.exportar_suplemento_contrato, name='ExportarSuplementoContrato'),
    path('exportar_altas/', views.exportar_altas, name='export_altas'),
    path('exportar_altas/<yyyy:year>/', views.all_altas_report, name='export_altas_year'),
    path('exportar_altas/<yyyy:year>/<mm:month>/', views.all_altas_report, name='export_altas_month'),
    path('exportar_bajas/', views.exportar_bajas, name='export_bajas'),
    path('exportar_bajas/<yyyy:year>/<mm:month>/', views.all_bajas_report, name='export_bajas_month'),
    path('exportar_bajas/<yyyy:year>/', views.all_bajas_report, name='export_bajas_year'),
    path('reportes/trabajadores/', include([
        path('altas/', views.informaciones_trabajador, name='informaciones_trabajador'),
        path('', views.dist_x_departamento, name='trabajador_reports'),
        path('listado-x-departamento/', include([
            path('altas/', include([
                path('', views.altas_x_departamento, name='altas-dept_report'),
                path('<date:from_date>/<date:to_date>/', views.altas_x_departamento, name='altas-dept-range_report'),
                path('<date:from_date>/<date:to_date>/pdf/', views.exportar_altas, name='altas-dept-range_export'),
                path('<yyyy:year>/', views.altas_x_departamento, name='altas-dept-year_report'),
                path('<yyyy:year>/pdf/', views.all_altas_report, name='altas-dept-year_export'),
                path('<yyyy:year>/<mm:month>/', views.altas_x_departamento, name='altas-dept-month_report'),
                path('<yyyy:year>/<mm:month>/pdf/', views.all_altas_report, name='altas-dept-month_export'),
            ])),
            path('bajas/', include([
                path('', views.bajas_x_departamento, name='bajas-dept_report'),
                path('<date:from_date>/<date:to_date>/', views.bajas_x_departamento, name='bajas-dept-range_report'),
                path('<date:from_date>/<date:to_date>/pdf/', views.exportar_bajas, name='bajas-dept-range_export'),
                path('<yyyy:year>/', views.bajas_x_departamento, name='bajas-dept-year_report'),
                path('<yyyy:year>/pdf/', views.all_bajas_report, name='bajas-dept-year_export'),
                path('<yyyy:year>/<mm:month>/', views.bajas_x_departamento, name='bajas-dept-month_report'),
                path('<yyyy:year>/<mm:month>/pdf/', views.all_bajas_report, name='bajas-dept-month_export')
            ])),
        ])),
        path('distribucion-x-departamento/', views.dist_x_departamento, name='dist-departamento_report'),
        path('distribucion-x-genero/', include([
            path('altas/', views.dist_altas_x_genero, name='altas-genero_report'),
            path('bajas/', views.dist_bajas_x_genero, name='bajas-genero_report')
        ])),
        path('distribucion-x-etnia', include([
            path('altas/', views.dist_altas_x_etnia, name='altas-etnia_report'),
            path('bajas/', views.dist_bajas_x_etnia, name='bajas-etnia_report')
        ])),
        path('piramide-de-edades/', include([
            path('altas/', views.dist_altas_x_rango_edades, name='altas-piramide-edades_report'),
            path('bajas/', views.dist_bajas_x_rango_edades, name='bajas-piramide-edades_report')
        ])),
        path('especialidad-x-departamento/', include([
            path('', views.dist_esp_x_dep, name='dist-esp-departamento_report'),
            path('pdf/', views.dist_esp_x_dep_report, name='dist-esp-departamento_export')
        ])),
        path('cargo-x-departamento/', include([
            path('', views.dist_cargos_x_dep, name='dist-cargo-departamento_report'),
            path('pdf/', views.dist_cargo_x_dep_report, name='dist-cargo-departamento_export')
        ])),
        path('resumen-defensa/', views.export_ubicacion_en_defensa, name='resumen-defensa_report'),
        path('registro-militar/', views.registro_defensa, name='registro-militar_report'),
        path('asignado-a-defensa/', views.asignado_a_defensa, name='asignado-a-defensa_report'),
        path('choferes-en-la-defensa/', views.choferes_en_defensa, name='choferes-defensa_report'),
        path('trabajadores-x-contrato/', views.trabajadores_x_contrato, name='trabajadores-contrato_report')
    ])),
    re_path('^dist-bar-drilldown/$', graphs.BarDrilldownDept.as_view(), name='dist-bar-drilldown'),
    re_path('^gender-pie/alta/$', graphs.PieGenderChart.as_view(model=models.Alta), name='gender-pie-alta'),
    re_path('^gender-pie/baja/$', graphs.PieGenderChart.as_view(model=models.BajaOther), name='gender-pie-baja'),
    re_path('^etnia-pie/alta/$', graphs.PieEtniaChart.as_view(model=models.Alta), name='etnia-pie-alta'),
    re_path('^etnia-pie/baja/$', graphs.PieEtniaChart.as_view(model=models.BajaOther), name='etnia-pie-baja'),
    re_path('^age-range-pyramid/alta/$', graphs.AgePyramidChart.as_view(model=models.Alta), name='age-pyramid-alta'),
    re_path('^age-range-pyramid/baja/$', graphs.AgePyramidChart.as_view(model=models.BajaOther),
            name='age-pyramid-baja')
]
