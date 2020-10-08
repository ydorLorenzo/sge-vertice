from django.urls import path, include
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("plantilla/", views.gestionar_plantilla, name='gestionarPlantilla'),
    path('adicionar_plantilla/', views.adicionar_plantilla, name='adicionarPlantilla'),
    path('editar_plantilla/<int:pk>/', views.editar_plantilla, name='editarPlantilla'),
    path('editar_plantilla_plazas/<int:pk>/', views.editar_plantilla_plazas,
         name='editarPlantillaPlazas'),
    path('eliminar_plantilla/<int:pk>/', views.eliminar_plantilla, name='eliminarPlantilla'),
    path('plantilla/Dpto_por_unidad/<int:pk>/', views.dpto_por_unidad, name='DepartamentoPorUnidad'),
    path('plantilla/Dpto_por_unidad/<int:pk>/<area>/', views.dpto_por_unidad, name='DepartamentoPorUnidad'),
    path('plantillas/', include([
        path('', views.PlantillaListView.as_view(), name='plantilla_list'),
        path('departamento/<int:departamento_id>/', views.PlantillaListView.as_view(),
             name='plantilla_departamento_list'),
        path('agregar/', views.PlantillaCreateView.as_view(), name='plantilla_create'),
        path('<int:pk>/actualizar/', views.PlantillaUpdateView.as_view(), name='plantilla_update'),
        path('<int:pk>/', views.PlantillaDetailView.as_view(), name='plantilla_detail'),
        path('<int:pk>/eliminar/', views.PlantillaDeleteView.as_view(), name='plantilla_delete')
    ])),
    path('plantilla-servicios/', include([
        path('servicios/', views.ServicioListView.as_view(), name='obra-servicio_list'),
        path('servicios/<int:servicio_id>/plantilla/', include([
            path('', views.PlantillaServicioListView.as_view(), name='plantillaservicio_list'),
            path('agregar/', views.PlantillaServicioCreateView.as_view(), name='plantillaservicio_create'),
            path('<int:pk>/', views.PlantillaServicioListView.as_view(), name='plantillaservicio_detail'),
            path('<int:pk>/actualizar/', views.PlantillaServicioUpdateView.as_view(), name='plantillaservicio_update'),
            path('<int:pk>/eliminar/', views.PlantillaServicioDeleteView.as_view(), name='plantillaservicio_delete')
        ])),
    ])),
    path('reportes/plantillas/', include([
        path('plantilla-general/', views.preview_plantilla_general, name='plantilla-general'),
        path('plantilla-general/exportar/', views.export_plantilla_general, name='plantilla-general_export'),
        path('plantilla-contratos-indeterminados/', views.preview_plantilla_ci, name='plantilla-ci'),
        path('plantilla-contratos-indeterminados/exportar/', views.export_plantilla_ci, name='plantilla-ci_export'),
        path('plantilla-recien-graduados/', views.preview_plantilla_rg,
             name='plantilla-rg'),
        path('plantilla-recien-graduados/exportar/', views.export_plantilla_rg,
             name='plantilla-rg_export'),
        path('plantilla-contratos-determinados/', views.preview_plantilla_cd, name='plantilla-cd'),
        path('plantilla-contratos-determinados/exportar/', views.export_plantilla_cd, name='plantilla-cd_export'),
        path('plantilla-reforma/', views.preview_plantilla_rf, name='plantilla-rf'),
        path('plantilla-reforma/exportar/', views.export_plantilla_rf, name='plantilla-rf_export'),
        path('calzado/', views.calzado_medios_de_proteccion, name='calzado_export')
    ]))
]
