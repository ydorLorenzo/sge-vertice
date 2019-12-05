from django.contrib.auth.decorators import *
from django.shortcuts import render, redirect
from django.views import generic


def context_add_perm(request, context, app, perm_a = None):

    if app == 'prenomina15':  # Verificando los permisos para el menu de PRENOMINA15
        menu_gestionar_obra = request.user.has_perm('prenomina15.read_obra')
        menu_gestionar_objeto = request.user.has_perm('prenomina15.read_objeto')
        menu_gestionar_plano = request.user.has_perm('prenomina15.read_plano')
        menu_export_dato = request.user.has_perm('prenomina15.export_dato')
        menu_generate_acta = request.user.has_perm('prenomina15.generate_acta')
        menu_find_acta = request.user.has_perm('prenomina15.read_acta')
        menu_generate_certifico = request.user.has_perm('prenomina15.generate_certifico')
        menu_export_prenomina = request.user.has_perm('prenomina15.export_prenomina')
        menu_generate_anexo = request.user.has_perm('prenomina15.generate_anexo')
        context['menu_gestionar_obra'] = menu_gestionar_obra
        context['menu_gestionar_objeto'] = menu_gestionar_objeto
        context['menu_gestionar_plano'] = menu_gestionar_plano
        context['menu_generate_acta'] = menu_generate_acta
        context['menu_find_acta'] = menu_find_acta
        context['menu_export_dato'] = menu_export_dato
        context['menu_generate_certifico'] = menu_generate_certifico
        context['menu_export_prenomina'] = menu_export_prenomina
        context['menu_generate_anexo'] = menu_generate_anexo

    if perm_a is not None:
        read = request.user.has_perm(app +'.read_'+ perm_a)
        add = request.user.has_perm(app +'.add_'+ perm_a)
        delete = request.user.has_perm(app +'.delete_'+ perm_a)
        change = request.user.has_perm(app +'.change_'+ perm_a)
        context['read'] = read
        context['add'] = add
        context['delete'] = delete
        context['change'] = change


    if app == 'prenomina15' and perm_a == 'plano':
        add_rev = request.user.has_perm(app + '.add_revision')
        read_rev = request.user.has_perm(app + '.read_revision')
        context['add_rev'] = add_rev
        context['read_rev'] = read_rev

    if app == 'prenomina15' and perm_a == 'acta':
        generate_acta = request.user.has_perm(app + '.generate_'+perm_a)
        export_acta = request.user.has_perm(app + '.export_' + perm_a)
        context['generate_acta'] = generate_acta
        context['export_acta'] = export_acta

    if app == 'prenomina15' and perm_a == 'certifico':
        generate_certifico = request.user.has_perm(app + '.generate_'+perm_a)
        export_certifico = request.user.has_perm(app + '.export_'+perm_a)
        context['generate_certifico'] = generate_certifico
        context['export_certifico'] = export_certifico

    if app == 'prenomina15' and perm_a == 'anexo':
        generate_anexo = request.user.has_perm(app + '.generate_'+perm_a)
        export_anexo = request.user.has_perm(app + '.export_'+perm_a)
        context['generate_anexo'] = generate_anexo
        context['export_anexo'] = export_anexo

    if app == 'prenomina15' and perm_a == 'prenomina':
        generate_prenomina = request.user.has_perm(app + '.generate_'+perm_a)
        export_prenomina = request.user.has_perm(app + '.export_'+perm_a)
        context['generate_prenomina'] = generate_prenomina
        context['export_prenomina'] = export_prenomina

    return context



def context_add_perm_menu_pren15(request, context):
    menu_gestionar_obra = request.user.has_perm('prenomina15.read_obra')
    menu_gestionar_objeto = request.user.has_perm('prenomina15.read_objeto')
    menu_gestionar_plano = request.user.has_perm('prenomina15.read_plano')
    menu_export_dato = request.user.has_perm('prenomina15.export_dato')
    menu_generate_acta = request.user.has_perm('prenomina15.generate_acta')
    menu_generate_certifico = request.user.has_perm('prenomina15.generate_certifico')
    menu_export_prenomina = request.user.has_perm('prenomina15.export_prenomina')
    menu_generate_anexo = request.user.has_perm('prenomina15.generate_anexo')
    context['menu_gestionar_obra'] = menu_gestionar_obra
    context['menu_gestionar_objeto'] = menu_gestionar_objeto
    context['menu_gestionar_plano'] = menu_gestionar_plano
    context['menu_generate_acta'] = menu_generate_acta
    context['menu_export_dato'] = menu_export_dato
    context['menu_generate_certifico'] = menu_generate_certifico
    context['menu_export_prenomina'] = menu_export_prenomina
    context['menu_generate_anexo'] = menu_generate_anexo

    return context

