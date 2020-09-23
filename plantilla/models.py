from django.db import models

from rechum.models import BaseUrls
from adm.models import UnidadOrg, Departamento, Cargo, EscalaSalarial


class Plantilla(BaseUrls, models.Model):
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, related_name='plantilla')
    escala_salarial = models.ForeignKey(EscalaSalarial, on_delete=models.SET_NULL, null=True)
    cant_plazas = models.PositiveIntegerField()
    disponibles = models.PositiveIntegerField(null=True, blank=True, editable=False)

    @property
    def unidad(self):
        return self.departamento.unidad

    def __str__(self):
        return '{} => {}'.format(self.cargo, self.escala_salarial.grupo)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.id:
            self.disponibles = self.cant_plazas
        return super(Plantilla, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']
        unique_together = ['departamento', 'cargo', 'escala_salarial']


class Unidad:
    codigo = ''
    nombre = ''
    departamentos = []
    cant_registros = ''
    numero = 0

    def __init__(self, codigo, nombre, departamentos, cant_registros, numero):
        self.codigo = codigo
        self.nombre = nombre
        self.departamentos = departamentos
        self.cant_registros = cant_registros
        self.numero = numero


class Dpto:
    codigo = ''
    nombre = ''
    trabajadores = []
    cant_registros = ''

    def __init__(self, codigo, nombre, trabajadores, cant_registros):
        self.codigo = codigo
        self.nombre = nombre
        self.trabajadores = trabajadores
        self.cant_registros = cant_registros


class Registro:
    data = None

    def __init__(self, data):
        self.data = data
