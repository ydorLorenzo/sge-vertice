from django.urls import path, include

from . import views

urlpatterns = [
    path('incidencias/', include([
        path('', views.events, name='evento_list'),
        path('<int:unidad_id>/', views.events, name='unidad-evento_list'),
        path('<int:unidad_id>/<int:trab_id>/', views.events, name='trab-evento_list')
    ])),
    path('evento/agregar/', views.EventoCreate.as_view(), name='evento_create')
]
