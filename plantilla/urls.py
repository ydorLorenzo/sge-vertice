from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('plantilla/', login_required(views.gestionar_plantilla), name='gestionarPlantilla'),
    path('adicionar_plantilla/', login_required(views.adicionar_plantilla), name='adicionarPlantilla'),
    path('editar_plantilla/<int:pk>/', login_required(views.editar_plantilla), name='editarPlantilla'),
    path('editar_plantilla_plazas/<int:pk>/', login_required(views.editar_plantilla_plazas),
         name='editarPlantillaPlazas'),
    path('eliminar_plantilla/<int:pk>/', login_required(views.eliminar_plantilla), name='eliminarPlantilla'),
    path('Dpto_por_unidad/<int:pk>/', login_required(views.dpto_por_unidad), name='DepartamentoPorUnidad'),
    path('vista_reporte_plantilla/', login_required(views.reporte), name='visualizarReportePlantilla'),
    path('exportar_plantilla/', login_required(views.exportar), name='exportarReportePlantilla'),
    path('vista_reporte_plantilla_recien_graduados/', login_required(views.reporte_graduados),
         name='visualizarReportePlantillaGraduados'),
    path('exportar_plantilla_recien_graduados/', login_required(views.exportar_graduados),
         name='exportarReportePlantillaGraduados'),
    path('vista_reporte_plantilla_contratos/', login_required(views.reporte_contratos),
         name='visualizarReportePlantillaContratos'),
    path('exportar_plantilla_contratos/', login_required(views.exportar_contratos),
         name='exportarReportePlantillaContratos'),
]
