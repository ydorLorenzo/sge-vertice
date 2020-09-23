from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import TemplateView

from . import views
from .decorators import module_permission_required


urlpatterns = [
    path('home_principal/', login_required(views.home_principal), name='home_principal'),
    path('rh/', login_required(
        module_permission_required(perm=('adm', 'ausentismo', 'datos_prenom', 'ges_trab', 'plantilla', 'subsidio'))(
            TemplateView.as_view(template_name='home_rechum.html'))), name='rechum_home'
    )
]
