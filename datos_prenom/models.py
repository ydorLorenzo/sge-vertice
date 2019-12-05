from django.db import models
from ges_trab.models import Trabajador


# Create your models here.


class TrabajoExtraordinario(models.Model):
    codigo_trab = models.ForeignKey(Trabajador, on_delete=models.CASCADE, default='')
    desde = models.DateField(verbose_name='Fecha de inicio', blank=False, null=False)
    hasta = models.DateField(verbose_name='Fecha de fin', blank=False, null=False)
    cant_horas = models.PositiveIntegerField(verbose_name='Cantidad de horas', blank=False, null=False)

    def __str__(self):
        return '{} => ({} / {})'.format(self.codigo_trab, self.desde, self.hasta)


class Vacaciones(models.Model):
    codigo_trab = models.ForeignKey(Trabajador, on_delete=models.CASCADE, default='')
    fecha = models.DateField(verbose_name='Fecha de solicitud', blank=False, null=False)
    cant_dias = models.PositiveIntegerField(verbose_name='Cantidad de días', blank=False, null=False)
    desde = models.DateField(verbose_name='Fecha Inicio', blank=False, null=False)
    hasta = models.DateField(verbose_name='Fecha Fin', blank=False, null=False)
    incorporacion = models.DateField(verbose_name='Fecha Fin', blank=False, null=False)
    horas = models.PositiveIntegerField(verbose_name='Cantidad de horas a descontar', blank=False, null=False)
    horas1 = models.PositiveIntegerField(verbose_name='Cantidad de horas a descontar mes próximo', blank=False,
                                         null=False, default=0)
    jefe_area = models.CharField(verbose_name='Jefe de Área', max_length=60, null=False, blank=False)
    director = models.CharField(verbose_name='Aprobado:', max_length=60, null=False, blank=False)

    def __str__(self):
        return '{} => {}'.format(self.codigo_trab, self.fecha)


class Alimentacion(models.Model):
    codigo_trab = models.ForeignKey(Trabajador, on_delete=models.CASCADE, default='')
    desde = models.DateField(verbose_name='Fecha de inicio', blank=False, null=False)
    hasta = models.DateField(verbose_name='Fecha de fin', blank=False, null=False)
    cant_dias = models.PositiveIntegerField(verbose_name='Días trabajados', blank=False, null=False)
    cant_dias_dieta = models.PositiveIntegerField(verbose_name='Días dieta', blank=True, null=True, default=0)

    def __str__(self):
        return '{} => {} => {}'.format(self.codigo_trab, self.desde, self.cant_dias)
