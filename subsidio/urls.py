from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('subsidios/', login_required(views.gestionar_subsidio), name='gestionarSubsidio'),
    path('adicionar_subsidio/', login_required(views.adicionar_subsidio), name='adicionarSubsidio'),
    path('editar_subsidio/<int:pk>/', login_required(views.editar_subsidio), name='editarSubsidio'),
    path('eliminar_sudsidio/<int:pk>/', login_required(views.EliminarSubsidio.as_view()),
         name='eliminarSubsidio'),
    path('detalle_subsidio/<int:pk>/', login_required(views.DetalleSubsidio.as_view()), name='detalleSubsidio'),
    path('vista_reporte/', login_required(views.reporte), name='visualizarReporte'),
    path('exportar/', login_required(views.exportar), name='exportarReporte'),
]
