from django.urls import path, include, register_converter, re_path

from principal.decorators import module_permission_required
from rechum.converters import FourDigitsYearConverter, TwoDigitsMonthConverter, DateConverter
from rechum.views import SgeTemplateView
from . import views, models

register_converter(FourDigitsYearConverter, 'yyyy')
register_converter(TwoDigitsMonthConverter, 'mm')
register_converter(DateConverter, 'date')

urlpatterns = [
    path('capacitacion/', include([
        path('tipoactividadcapacitacion_list/', include([
            path('', views.TipoActCapListView.as_view(), name='tipoactividadcapacitacion_list'),
            path('agregar/', views.TipoActCapCreateView.as_view(), name='tipoactividadcapacitacion_create'),
            path('<int:pk>/', views.TipoActCapDetailView.as_view(), name='tipoactividadcapacitacion_detail'),
            path('<int:pk>/actualizar/', views.TipoActCapUpdateView.as_view(), name='tipoactividadcapacitacion_update'),
            path('<int:pk>/eliminar/', views.TipoActCapDeleteView.as_view(), name='tipoactividadcapacitacion_delete')
        ]))
    ]))
 ]
