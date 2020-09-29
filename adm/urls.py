from django.urls import path
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import views as auth_views

from . import views
from rechum.urls import *


urlpatterns = [
    path('home/', views.home, name='home'),
    path('administracion/', include([
        path('unidades-organizacionales/', include([
            path('', views.UnidadOrgListView.as_view(), name='unidadorg_list'),
            path('agregar/', views.UnidadOrgCreateView.as_view(), name='unidadorg_create'),
            path('<int:pk>/actualizar/', views.UnidadOrgUpdateView.as_view(), name='unidadorg_update'),
            path('<int:pk>/', views.UnidadOrgDetailView.as_view(), name='unidadorg_detail'),
            path('<int:pk>/trabajadores/', views.trab_unidad, name='trab-unidad'),
            path('<int:pk>/eliminar/', views.UnidadOrgDeleteView.as_view(), name='unidadorg_delete')
        ])),
        path('secciones-sindicales/', include([
            path('', views.SecSinListView.as_view(), name='seccionsindical_list'),
            path('agregar/', views.SecSinCreateView.as_view(), name='seccionsindical_create'),
            path('<int:pk>/actualizar/', views.SecSinUpdateView.as_view(), name='seccionsindical_update'),
            path('<int:pk>/', views.SecSinDetailView.as_view(), name='seccionsindical_detail'),
            path('<int:pk>/eliminar/', views.SecSinDeleteView.as_view(), name='seccionsindical_delete')
        ])),
        path('departamentos/', include([
            path('', views.DepListView.as_view(), name='departamento_list'),
            path('unidad/<int:unidad_id>/', views.DepListView.as_view(), name='departamento_unidad_list'),
            path('agregar/', views.DepCreateView.as_view(), name='departamento_create'),
            path('<int:pk>/actualizar/', views.DepUpdateView.as_view(), name='departamento_update'),
            path('<int:pk>/', views.DepDetailView.as_view(), name='departamento_detail'),
            path('<int:pk>/eliminar/', views.DepDeleteView.as_view(), name='departamento_delete')
        ])),
        path('escalas-salariales/', include([
            path('', views.EscSalListView.as_view(), name='escalasalarial_list'),
            path('agregar/', views.EscSalCreateView.as_view(), name='escalasalarial_create'),
            path('<int:pk>/actualizar/', views.EscSalUpdateView.as_view(), name='escalasalarial_update'),
            path('<int:pk>/', views.EscSalDetailView.as_view(), name='escalasalarial_detail'),
            path('<int:pk>/eliminar/', views.EscSalDeleteView.as_view(), name='escalasalarial_delete')
        ])),
        path('cargos/', include([
            path('', views.CargoListView.as_view(), name='cargo_list'),
            path('agregar/', views.CargoCreateView.as_view(), name='cargo_create'),
            path('<int:pk>/actualizar/', views.CargoUpdateView.as_view(), name='cargo_update'),
            path('<int:pk>/', views.CargoDetailView.as_view(), name='cargo_detail'),
            path('<int:pk>/eliminar/', views.CargoDeleteView.as_view(), name='cargo_delete')
        ])),
        path('calificaciones/', include([
            path('', views.CalListView.as_view(), name='calificacion_list'),
            path('agregar/', views.CalCreateView.as_view(), name='calificacion_create'),
            path('<int:pk>/actualizar/', views.CalUpdateView.as_view(), name='calificacion_update'),
            path('<int:pk>/', views.CalDetailView.as_view(), name='calificacion_detail'),
            path('<int:pk>/eliminar/', views.CalDeleteView.as_view(), name='calificacion_delete')
        ])),
        path('especialidades/', include([
            path('', views.EspListView.as_view(), name='especialidad_list'),
            path('agregar/', views.EspCreateView.as_view(), name='especialidad_create'),
            path('<int:pk>/actualizar/', views.EspUpdateView.as_view(), name='especialidad_update'),
            path('<int:pk>/', views.EspDetailView.as_view(), name='especialidad_detail'),
            path('<int:pk>/eliminar/', views.EspDeleteView.as_view(), name='especialidad_delete')
        ])),
    ])),
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
