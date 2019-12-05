from django.db import models
from entrada_datos.models import OT, Actividad
from ges_trab.models import Trabajador

# Create your models here.


class Datos (models.Model):
    orden_trab = models.ForeignKey(OT, on_delete=models.DO_NOTHING, null=False, blank=False, default='')
    actividad = models.ForeignKey(Actividad, on_delete=models.DO_NOTHING, null=False, blank=False, default='')
    trabajador = models.ForeignKey(Trabajador, on_delete=models.DO_NOTHING, null=False, blank=False, default='')
    cant_horas = models.PositiveIntegerField(null=False, blank=False)
    horas_ext = models.PositiveIntegerField(null=False, blank=False, default=0)
    tarifa_hor = models.DecimalField(max_digits=7, decimal_places=6, editable=False)
    prod_reportada = models.PositiveIntegerField(null=False, blank=False, editable=False)


class DatosAnual (models.Model):
    orden_trab = models.ForeignKey(OT, on_delete=models.DO_NOTHING, null=False, blank=False)
    actividad = models.ForeignKey(Actividad, on_delete=models.DO_NOTHING, null=False, blank=False)
    trabajador = models.ForeignKey(Trabajador, on_delete=models.DO_NOTHING, null=False, blank=False)
    cant_horas = models.PositiveIntegerField(null=False, blank=False)
    horas_ext = models.PositiveIntegerField(null=False, default=0)
    tarifa_hor = models.DecimalField(max_digits=7, decimal_places=6, editable=False, null=False, blank=False)
    prod_reportada = models.PositiveIntegerField(editable=False)
    fecha = models.DateField(editable=False)
    prod_tecleada = models.PositiveIntegerField(null=False, blank=False, default=0)


class CoeficientePromedioSalario(models.Model):
    coeficiente = models.PositiveIntegerField(null=False, blank=False)


class Area:
    nombre = ''
    id = ''
    ot = []
    total = 0

    def __init__(self, nombre, ot, id_a, total):
        self.nombre = nombre
        self.ot = ot
        self.id = id_a
        self.total = total


class OrdenTrabajo:
    codigo = ''
    nombre = ''
    actividades = []
    total = 0
    area = 0

    def __init__(self, codigo, nombre, actividades, total, area):
        self.codigo = codigo
        self.nombre = nombre
        self.actividades = actividades
        self.total = total
        self.area = area


class Actividades:
    orden_trab = ''
    codigo = ''
    nombre = ''
    trabajadores = []
    valor = 0
    id = ''

    def __init__(self, orden_trab, codigo, nombre, trabajadores, valor, id):
        self.orden_trab = orden_trab
        self.nombre = nombre
        self.codigo = codigo
        self.trabajadores = trabajadores
        self.valor = valor
        self.id = id


class Trabajador:
    codigo = ''
    nombre = ''
    real = 0
    extra = 0
    id = 0
    id_act =0

    def __init__(self, codigo, nombre, real, extra, id, id_act):
        self.nombre = nombre
        self.codigo = codigo
        self.real = real
        self.extra = extra
        self.id = id
        self.id_act = id_act
