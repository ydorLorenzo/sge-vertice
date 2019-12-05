from django.db import models
from adm.models import UnidadOrg, Departamento, Cargo


# Create your models here.


class Plantilla(models.Model):
    unidad = models.ForeignKey(UnidadOrg, on_delete=models.DO_NOTHING, default='')
    departamento = models.ForeignKey(Departamento, on_delete=models.DO_NOTHING, default='')
    cargo = models.ForeignKey(Cargo, on_delete=models.DO_NOTHING, default='')
    cant_plazas = models.PositiveIntegerField()
    disponibles = models.PositiveIntegerField(null=True, blank=True, editable=False)

    def __str__(self):
        return '{} => {}'.format(self.departamento, self.cargo)


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
