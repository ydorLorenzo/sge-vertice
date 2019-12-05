from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('home_pr3/', login_required(views.home_pr3), name='home_pr3'),
    path('actualizar_coeficiente/', login_required(views.editar_coeficiente), name='actualizarCoeficiente'),
    path('datos/', login_required(views.registrar_datos), name='entradaDatos'),
    path('listar_valor_prod/', login_required(views.listar_valor_prod), name='listaValorProd'),
    path('ajustar_prod/', login_required(views.ajustar_valor_prod), name='ajustar_prod'),
    path('act_por_ot/<int:pk>/', login_required(views.act_por_ot), name='ActPorOT'),
    path('list_datos/', login_required(views.listado_datos), name='ListDatos'),
    path('vista_reporte_ot_actividades/', login_required(views.reporte_ot_actividades),
         name='visualizarReporteOTActividades'),
    path('exportar_reporte_ot_actividades/', login_required(views.exportar_ot_actividades),
         name='exportarReporteOTActividades'),
    path('vista_reporte_area_ot/', login_required(views.reporte_area_ot), name='visualizarReporteAreaOT'),
    path('exportar_reporte_area_ot/', login_required(views.exportar_area_ot), name='exportarReporteAreaOT'),
    path('vista_reporte_act_contrato/', login_required(views.reporte_actividades_contrato), name='ReporteActCont'),
    path('exportar_reporte_act_contrato/<cont>/', login_required(views.exportar_actividades_contrato),
         name='exportarReporteActCont'),
    path('vista_reporte_pr3/', login_required(views.reporte_pr3), name='visualizarReportePR3'),
    path('exportar_reporte_pr3/', login_required(views.exportar_reporte_pr3), name='exportarReportePR3'),
    path('vista_reporte_prod_dir/', login_required(views.reporte_prod_direccion), name='visualizarReporteProdDir'),
]
