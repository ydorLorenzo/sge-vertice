from django.urls import path

from . import views

urlpatterns = [
    path('incidencias/', views.events, name='evento_list'),
    path('evento/agregar/', views.EventoCreate.as_view(), name='evento_create')
]
