from django.db import models
from ges_trab.models import Trabajador


class Subsidio(models.Model):
    codigo_trab = models.ForeignKey(Trabajador, on_delete=models.CASCADE, default='')
    desde = models.DateField(verbose_name='Fecha de inicio', blank=False, null=False)
    hasta = models.DateField(verbose_name='Fecha de fin', blank=False, null=False)
    centro = models.CharField(max_length=200, verbose_name='Centro Asistencial')
    medico = models.CharField(max_length=200, verbose_name='Nombre del médico')
    fecha = models.DateField(verbose_name='Fecha de registro', blank=False, null=False)
    diagnostico = models.CharField(max_length=80, verbose_name='Diagnóstico')
    PORCIENTO_OPT = (('50', '50'), ('60', '60'), ('70', '70'), ('80', '80'), ('100', '100'))
    por_ciento = models.CharField(max_length=3, choices=PORCIENTO_OPT, verbose_name='Porciento a pagar',
                                  default=PORCIENTO_OPT[0])
    dias = models.PositiveIntegerField(verbose_name='Cantidad de días a pagar')
    TIPO_OPT = (('Inic.', 'Inicial'), ('Cont.', 'Continuado'))
    tipo = models.CharField(max_length=5, choices=TIPO_OPT, verbose_name='Tipo de certificado',
                            default=TIPO_OPT[0])
    no_reg = models.PositiveIntegerField(verbose_name='Número del registro del certificado', default=1)
    ENT_OPT = (('Si', 'Si'), ('No', 'No'))
    ent_72 = models.CharField(max_length=2, choices=ENT_OPT, verbose_name='Entregado antes las 72 horas',
                              default=ENT_OPT[0])

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
