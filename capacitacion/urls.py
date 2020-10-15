from . import views
from rechum.urls import *


urlpatterns = [
    path('capacitacion/', include([
        path('', views.home, name='capacitacion_home'),
        path('actividad/', include([
            path('', views.ActividadCapacitacionListView.as_view(), name="actividadcapacitacion_list"),
            path('<int:pk>/', views.ActividadCapacitacionDetailView.as_view(), name="actividadcapacitacion_detail"),
            path('<int:pk>/actualizar/', views.ActividadCapacitacionUpdateView.as_view(), name="actividadcapacitacion_update"),
            path('agregar/', views.ActividadCapacitacionCreateView.as_view(), name="actividadcapacitacion_create"),
            path('<int:pk>/eliminar/', views.ActividadCapacitacionDeleteView.as_view(), name="actividadcapacitacion_delete")
        ])),
        path('modo_formacion/', include([
            path('', views.ModoFormacionListView.as_view(), name='modoformacion_list'),
            path('agregar/', views.ModoFormacionCreateView.as_view(), name='modoformacion_create'),
            path('<int:pk>/', views.ModoFormacionDetailView.as_view(), name='modoformacion_detail'),
            path('<int:pk>/actualizar/', views.ModoFormacionUpdateView.as_view(), name='modoformacion_update'),
            path('<int:pk>/eliminar/', views.ModoFormacionDeleteView.as_view(), name='modoformacion_delete')
        ])),
        path('tipo_actividad/', include([
            path('', views.TipoActividadCapacitacionListView.as_view(), name='tipoactividadcapacitacion_list'),
            path('agregar/', views.TipoActividadCapacitacionCreateView.as_view(), name='tipoactividadcapacitacion_create'),
            path('<int:pk>/', views.TipoActividadCapacitacionDetailView.as_view(), name='tipoactividadcapacitacion_detail'),
            path('<int:pk>/actualizar/', views.TipoActividadCapacitacionUpdateView.as_view(), name='tipoactividadcapacitacion_update'),
            path('<int:pk>/eliminar/', views.TipoActividadCapacitacionDeleteView.as_view(), name='tipoactividadcapacitacion_delete')
        ]))
    ]))
]
