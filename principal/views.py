from django.contrib.auth.models import _user_has_module_perms
from django.shortcuts import render


# Create your views here.


def home_principal(request):
   # Verificando si tiene permiso para el modulo de capital humano
    permiso_app_adm = _user_has_module_perms(request.user, 'adm')
    if permiso_app_adm:
        permiso_app_adm = 'home'
    else:
        permiso_app_adm = 'home_principal'

   # Verificando si tiene permiso para el modulo de entrada de datos
    permiso_app_datos = _user_has_module_perms(request.user, 'entrada_datos')
    if permiso_app_datos:
        permiso_app_datos = 'home_ent_dat'
    else:
        permiso_app_datos = 'home_principal'

   # Verificando si tiene permiso para el modulo de PR3
    permiso_app_pr3 = _user_has_module_perms(request.user, 'pr3')
    if permiso_app_pr3:
        permiso_app_pr3 = 'home_pr3'
    else:
        permiso_app_pr3 = 'home_principal'

   # Verificando si tiene permiso para el modulo de Prenomina15
    permiso_app_pren15 = _user_has_module_perms(request.user, 'prenomina15')
    if permiso_app_pren15:
        permiso_app_pren15 = 'home_pren15'
    else:
        permiso_app_pren15 = 'home_principal'

    context = {'request': request,
               'permiso_app_adm':permiso_app_adm,
               'permiso_app_pren15':permiso_app_pren15,
               'permiso_app_pr3':permiso_app_pr3,
               'permiso_app_datos': permiso_app_datos}
    return render(request, 'home_principal.html', context)
