from django.contrib import admin

# Register your models here.
from ausentismo.models import Ausencia, TarjetaCNC

admin.site.register(Ausencia)
admin.site.register(TarjetaCNC)