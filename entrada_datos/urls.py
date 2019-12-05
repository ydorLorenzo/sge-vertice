from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('home_ent_dat/', login_required(views.home_ent_dat), name='home_ent_dat'),
    path('actividad/', login_required(views.gestionar_actividad), name='gestionarActividad'),
    path('tipo_actividad/', login_required(views.gestionar_tipo_actividad), name='gestionarTipoActividad'),
    path('area/', login_required(views.gestionar_area), name='gestionarArea'),
    path('servicio/', login_required(views.gestionar_servicio), name='gestionarServicio'),
    path('orden_trabajo/', login_required(views.gestionar_ot), name='gestionarOT'),
    path('adicionar_actividad/', login_required(views.adicionar_actividad), name='adicionarActividad'),
    path('adicionar_area/', login_required(views.adicionar_area), name='adicionarArea'),
    path('adicionar_servicio/', login_required(views.adicionar_servicio), name='adicionarServicio'),
    path('adicionar_tipo_actividad/', login_required(views.adicionar_tipo_actividad), name='adicionarTipoActividad'),
    path('adicionar_suplemento/', login_required(views.adicionar_suplemento), name='adicionarSuplemento'),
    path('editar_actividad/<int:pk>/', login_required(views.editar_actividad), name='editarActividad'),
    path('eliminar_area/<int:pk>/', login_required(views.eliminar_area), name='eliminarArea'),
    path('eliminar_servicio/<int:pk>/', login_required(views.eliminar_servicio), name='eliminarServicio'),
    path('eliminar_actividad/<int:pk>/', login_required(views.eliminar_actividad), name='eliminarActividad'),
    path('eliminar_tipo_actividad/<int:pk>/', login_required(views.eliminar_tipo_actividad),
         name='eliminarTipoActividad'),
    path('inversionista/', login_required(views.gestionar_inversionista), name='gestionarInversionista'),
    path('adicionar_inversionista/', login_required(views.adicionar_inversionista), name='adicionarInversionista'),
    path('editar_inversionista/<int:pk>/', login_required(views.editar_inversionista), name='editarInversionista'),
    path('eliminar_inversionista/<int:pk>/', login_required(views.eliminar_inversionista),
         name='eliminarInversionista'),
    path('detalle_inversionista/<int:pk>/', login_required(views.DetalleInversionista.as_view()),
         name='detalleInversionista'),
    path('orden_trabajo/', login_required(views.gestionar_ot), name='gestionarOT'),
    path('adicionar_ot/', login_required(views.adicionar_ot), name='adicionarOT'),
    path('editar_ot/<int:pk>/', login_required(views.editar_ot), name='editarOT'),
    path('eliminar_ot/<int:pk>/', login_required(views.eliminar_ot),
         name='eliminarOT'),
    path('detalle_ot/<int:pk>/', login_required(views.detalle_ot), name='detalleOT'),
    path('listado_suplementos/<int:pk>/', login_required(views.listado_suplementos), name='listadoSup'),
]
