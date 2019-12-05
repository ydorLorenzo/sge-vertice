from django.contrib import admin
from datos_prenom.models import TrabajoExtraordinario, Vacaciones, Alimentacion

# Register your models here.
admin.site.register(TrabajoExtraordinario)
admin.site.register(Vacaciones)
admin.site.register(Alimentacion)
