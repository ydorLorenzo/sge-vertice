from django.contrib import admin

from .models import GrupoCalendario, Calendario, TipoEvento


admin.site.register([GrupoCalendario, Calendario, TipoEvento])
