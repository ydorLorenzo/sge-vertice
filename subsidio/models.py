from django.db import models

from ges_trab.models import Trabajador
from rechum.models import BaseUrls


class Subsidio(BaseUrls, models.Model):
    codigo_trab = models.ForeignKey(Trabajador, on_delete=models.CASCADE, default='', verbose_name="trabajador")
    desde = models.DateField('fecha de inicio')
    hasta = models.DateField('fecha de fin')
    centro = models.CharField('centro asistencial', max_length=200)
    medico = models.CharField('nombre del médico', max_length=200)
    fecha = models.DateField('fecha de registro')
    diagnostico = models.CharField('diagnóstico', max_length=80)
    PORCIENTO_OPT = (('50', '50'), ('60', '60'), ('70', '70'), ('80', '80'), ('100', '100'))
    por_ciento = models.CharField('por ciento a pagar', max_length=3, choices=PORCIENTO_OPT, default=PORCIENTO_OPT[0])
    dias = models.PositiveIntegerField('cantidad de días a pagar')
    TIPO_OPT = (('Inic.', 'Inicial'), ('Cont.', 'Continuado'))
    tipo = models.CharField('tipo de certificado', max_length=5, choices=TIPO_OPT, default=TIPO_OPT[0])
    no_reg = models.PositiveIntegerField('número de registro del certificado', default=1)
    ENT_OPT = (('Si', 'Si'), ('No', 'No'))
    ent_72 = models.CharField('entregado antes de las 72 horas', max_length=2, choices=ENT_OPT, default=ENT_OPT[0])

    def __str__(self):
        return '{} => {}'.format(self.codigo_trab, self.fecha)


class Department:
    codigo = ''
    nombre = ''
    personas = []
    suma_area = ''
    cant_registros = ''

    def __init__(self, codigo, nombre, personas, suma_area, cant_registros):
        self.codigo = codigo
        self.nombre = nombre
        self.personas = personas
        self.suma_area = suma_area
        self.cant_registros = cant_registros


class Person:
    codigo = ''
    nombre = ''
    subsidios = []
    suma_cod = ''
    cant_registros = ''

    def __init__(self, codigo, nombre, subsidios, suma_cod, cant_registros):
        self.codigo = codigo
        self.nombre = nombre
        self.subsidios = subsidios
        self.suma_cod = suma_cod
        self.cant_registros = cant_registros
