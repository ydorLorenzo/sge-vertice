from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from rechum.urls import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.login_up, name='login_up'),
    path('home/', login_required(views.home), name='home'),
    path('logout/', login_required(auth_views.logout), name='logout'),
    path('unidad_organizacional/', login_required(views.gestionar_unidad_org), name='gestionarUnidadOrg'),
    path('calificacion/', login_required(views.gestionar_calificacion), name='gestionarCalificacion'),
    path('departamento/', login_required(views.gestionar_departamento), name='gestionarDepartamento'),
    path('cargo/', login_required(views.gestionar_cargo), name='gestionarCargo'),
    path('especialidad/', login_required(views.gestionar_especialidad), name='gestionarEspecialidad'),
    path('seccion_sindical/', login_required(views.gestionar_seccion_sindical), name='gestionarSeccionSindical'),
    path('adicionar_unidad_organizacional/', login_required(views.adicionar_uo), name='adicionarUO'),
    path('editar_unidad_organizacional/<int:pk>/', login_required(views.editar_uo), name='editarUO'),
    path('detalle_unidad_organizacional/<int:pk>/', login_required(views.DetalleUo.as_view()), name='detalleUO'),
    path('eliminar_unidad_organizacional/<int:pk>/', login_required(views.eliminar_uo), name='eliminarUO'),
    path('adicionar_seccion_sindical/', login_required(views.adicionar_ss), name='adicionarSS'),
    path('editar_seccion_sindical/<int:pk>/', login_required(views.editar_ss), name='editarSS'),
    path('detalle_seccion_sindical/<int:pk>/', login_required(views.DetalleSs.as_view()), name='detalleSS'),
    path('eliminar_seccion_sindical/<int:pk>/', login_required(views.eliminar_ss), name='eliminarSS'),
    path('adicionar_departamento/', login_required(views.adicionar_departamento), name='adicionarDepartamento'),
    path('editar_departamento/<int:pk>/', login_required(views.editar_departamento), name='editarDepartamento'),
    path('detalle_departamento/<int:pk>/', login_required(views.DetalleDepartamento.as_view()),
         name='detalleDepartamento'),
    path('eliminar_departamento/<int:pk>/', login_required(views.eliminar_departamento), name='eliminarDepartamento'),
    path('adicionar_cargo/', login_required(views.adicionar_cargo), name='adicionarCargo'),
    path('editar_cargo/<int:pk>/', login_required(views.editar_cargo), name='editarCargo'),
    path('detalle_cargo/<int:pk>/', login_required(views.DetalleCargo.as_view()), name='detalleCargo'),
    path('eliminar_cargo/<int:pk>/', login_required(views.eliminar_cargo), name='eliminarCargo'),
    path('adicionar_calificacion/', login_required(views.adicionar_calificacion), name='adicionarCalificacion'),
    path('editar_calificacion/<int:pk>/', login_required(views.editar_calificacion), name='editarCalificacion'),
    path('detalle_calificacion/<int:pk>/', login_required(views.DetalleCalificacion.as_view()),
         name='detalleCalificacion'),
    path('eliminar_calificacion/<int:pk>/', login_required(views.eliminar_calificacion),
         name='eliminarCalificacion'),
    path('adicionar_especialidad/', login_required(views.adicionar_especialidad), name='adicionarEspecialidad'),
    path('editar_especialidad/<int:pk>/', login_required(views.editar_especialidad), name='editarEspecialidad'),
    path('detalle_especialidad/<int:pk>/', login_required(views.DetalleEspecialidad.as_view()),
         name='detalleEspecialidad'),
    path('eliminar_especialidad/<int:pk>/', login_required(views.eliminar_especialidad), name='eliminarEspecialidad'),
]
