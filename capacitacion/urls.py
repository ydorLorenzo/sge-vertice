from . import views
from rechum.urls import *


urlpatterns = [
    path('capacitacion/', include([
        path('', views.home, name='capacitacion_home'),
        path('actividad/', include([
            path('', views.ActCapListView.as_view(), name="actividadcapacitacion_list"),
            path('<int:pk>/', views.ActCapDetailView.as_view(), name="actividadcapacitacion_detail"),
            path('<int:pk>/actualizar/', views.ActCapUpdateView.as_view(), name="actividadcapacitacion_update"),
            path('agregar/', views.ActCapCreateView.as_view(), name="actividadcapacitacion_create"),
            path('<int:pk>/eliminar/', views.ActCapDeleteView.as_view(), name="actividadcapacitacion_delete")
        ]))
    ]))
]
