from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('ausentismo/', login_required(views.gestionar_ausentismo), name='gestionarAusentismo'),
    path('listar_ausentismo/<int:pk>/', login_required(views.listar_ausentismo), name='listarAusentismo'),
    path('adicionar_ausentismo/', login_required(views.adicionar_ausentismo), name='adicionarAusentismo'),
    path('editar_ausentismo/<int:idtrab>/<int:pk>/', login_required(views.editar_ausentismo), name='editarAusentismo'),
    path('eliminar_ausentismo/<int:idtrab>/<int:pk>/', login_required(views.eliminar_ausentismo),
         name='eliminarAusentismo'),

    path('vista_reporte_ausentismo/', login_required(views.reporte), name='visualizarReporteAusentismo'),
    path('exportar_ausentismo/', login_required(views.exportar), name='exportarReporteAusentismo'),

    path('registro_tarjeta_SNC/', login_required(views.gestionar_tarjeta_snc), name='gestionarRegistroTarjetaSNC'),
    path('listar_registro_tarjetaSNC/<int:pk>/', login_required(views.listar_tarjeta_snc),
         name='listarRegistroTarjetaSNC'),
    path('adicionar_registro_tarjetaSNC/', login_required(views.adicionar_tarjeta_snc),
         name='adicionarRegistroTarjetaSNC'),
    path('editar_registro_tarjetaSNC/<int:idtrab>/<int:pk>/', login_required(views.editar_tarjeta_snc),
         name='editarRegistroTarjetaSNC'),
    path('eliminar_registro_tarjetaSNC/<int:idtrab>/<int:pk>/', login_required(views.eliminar_tarjeta_snc),
         name='eliminarRegistroTarjetaSNC'),
]
