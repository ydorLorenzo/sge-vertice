from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('trabajo_extraordinario/', login_required(views.gestionar_trabajo_extra), name='gestionarTrabajoExtra'),
    path('adicionar_trabajo_extraordinario/', login_required(views.adicionar_trabajo_extra),
         name='adicionarTrabajoExtra'),
    path('editar_trabajo_extraordinario/<int:pk>/', login_required(views.editar_trabajo_extra),
         name='editarTrabajoExtra'),
    path('eliminar_trabajo_extraordinario/<int:pk>/', login_required(views.EliminarTrabajoExtra.as_view()),
         name='eliminarTrabajoExtra'),
    path('detalle_trabajo_extraordinario/<int:pk>/', login_required(views.DetalleTrabajoExtra.as_view()),
         name='detalleTrabajoExtra'),

    path('alimentacion/', login_required(views.gestionar_alimentacion), name='gestionarAlimentacion'),
    path('adicionar_alimentacion/', login_required(views.adicionar_alimentacion),
         name='adicionarAlimentacion'),
    path('editar_alimentacion/<int:pk>/', login_required(views.editar_alimentacion),
         name='editarAlimentacion'),
    path('eliminar_alimentacion/<int:pk>/', login_required(views.EliminarAlimentacion.as_view()),
         name='eliminarAlimentacion'),
    path('detalle_alimentacion/<int:pk>/', login_required(views.DetalleAlimentacion.as_view()),
         name='detalleAlimentacion'),

    path('vacaciones/', login_required(views.gestionar_vacaciones), name='gestionarVacaciones'),
    path('adicionar_vacaciones/', login_required(views.adicionar_vacaciones),
         name='adicionarVacaciones'),
    path('editar_vacaciones/<int:pk>/', login_required(views.editar_vacaciones),
         name='editarVacaciones'),
    path('eliminar_vacaciones/<int:pk>/', login_required(views.EliminarVacaciones.as_view()),
         name='eliminarVacaciones'),
    path('detalle_vacaciones/<int:pk>/', login_required(views.DetalleVacaciones.as_view()),
         name='detalleVacaciones'),

    path('vista_reporte_vacaciones/', login_required(views.reporte), name='visualizarReporteVacaciones'),
    path('exportar_vacaciones/', login_required(views.exportar), name='exportarReporteVacaciones'),
    path('exportar_modelo_vacaciones/<int:pk>/', login_required(views.exportar_modelo_vacaciones), name='ExportarModeloVacaciones'),
]
