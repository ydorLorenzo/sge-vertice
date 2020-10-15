from . import views
from rechum.urls import *
from django.urls import path, include, register_converter, re_path

from principal.decorators import module_permission_required
from rechum.converters import FourDigitsYearConverter, TwoDigitsMonthConverter, DateConverter
from rechum.views import SgeTemplateView
from . import views, models

urlpatterns = [
    path('capacitacion/', include([
        path('', views.home, name='capacitacion_home'),
        path('actividad/', include([
            path('', views.ActCapListView.as_view(), name="actividadcapacitacion_list"),
            path('<int:pk>/', views.ActCapDetailView.as_view(), name="actividadcapacitacion_detail"),
            path('<int:pk>/actualizar/', views.ActCapUpdateView.as_view(), name="actividadcapacitacion_update"),
            path('agregar/', views.ActCapCreateView.as_view(), name="actividadcapacitacion_create"),
            path('<int:pk>/eliminar/', views.ActCapDeleteView.as_view(), name="actividadcapacitacion_delete")
        ])),
        path('tipoactividadcapacitacion_list/', include([
            path('', views.TipoActCapListView.as_view(), name='tipoactividadcapacitacion_list'),
            path('agregar/', views.TipoActCapCreateView.as_view(), name='tipoactividadcapacitacion_create'),
            path('<int:pk>/', views.TipoActCapDetailView.as_view(), name='tipoactividadcapacitacion_detail'),
            path('<int:pk>/actualizar/', views.TipoActCapUpdateView.as_view(), name='tipoactividadcapacitacion_update'),
            path('<int:pk>/eliminar/', views.TipoActCapDeleteView.as_view(), name='tipoactividadcapacitacion_delete')
        ]))
    ]))
]
