from decorator_include import decorator_include
from django.contrib import admin
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required
from django.urls import path, include, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', decorator_include(login_required, 'principal.urls')),
    path('', login, name='login_up'),
    path('rh/', include([
        path('', decorator_include(login_required, 'adm.urls')),
        path('', decorator_include(login_required, 'ges_trab.urls')),
        path('', decorator_include(login_required, 'plantilla.urls')),
        path('', decorator_include(login_required, 'capacitacion.urls')),
        path('parte-tiempo/', decorator_include(login_required, 'parte_tiempo.urls')),
        path('subsidios/', decorator_include(login_required, 'subsidio.urls')),
        path('datos-prenomina/', decorator_include(login_required, 'datos_prenom.urls')),
        path('ausentismo/', decorator_include(login_required, 'ausentismo.urls')),
        path('capacitacion/', decorator_include(login_required, 'capacitacion.urls')),
    ])),
    path('entrada-datos/', decorator_include(login_required, 'entrada_datos.urls')),
    path('facturacion/', decorator_include(login_required, 'facturacion.urls')),
    path('pr3/', decorator_include(login_required, 'pr3.urls')),
    path('pren/', decorator_include(login_required, 'prenomina15.urls')),
    re_path('^select2/', include('django_select2.urls'))
    # path('__debug__/', include(debug_toolbar.urls))
]
