from django.db import models

from ges_trab.models import Trabajador
from rechum.models import BaseUrls


class TrabajoExtraordinario(models.Model):
    codigo_trab = models.ForeignKey(Trabajador, on_delete=models.CASCADE, default='', verbose_name="trabajador")
    desde = models.DateField('fecha de inicio')
    hasta = models.DateField('fecha de fin')
    cant_horas = models.PositiveIntegerField('cantidad de horas')

    def __str__(self):
        return '{} => ({} / {})'.format(self.codigo_trab, self.desde, self.hasta)

    class Meta:
        verbose_name_plural = "trabajos extraordinarios"


class Vacaciones(BaseUrls, models.Model):
    codigo_trab = models.ForeignKey(Trabajador, on_delete=models.CASCADE, default='', verbose_name='trabajador')
    fecha = models.DateField(verbose_name='fecha de solicitud')
    cant_dias = models.PositiveIntegerField('cantidad de días')
    desde = models.DateField('fecha inicio')
    hasta = models.DateField('fecha fin')
    incorporacion = models.DateField('fecha de inincorporación')
    horas = models.PositiveIntegerField(verbose_name='cantidad de horas a descontar')
    horas1 = models.PositiveIntegerField(verbose_name='cantidad de horas a descontar mes próximo', default=0)
    jefe_area = models.CharField('jefe de área', max_length=60)
    director = models.CharField('aprobado por', max_length=60)

    def __str__(self):
        return '{} => {}'.format(self.codigo_trab, self.fecha)

    class Meta:
        verbose_name_plural = 'vacaciones'


class Alimentacion(BaseUrls, models.Model):
    codigo_trab = models.ForeignKey(Trabajador, on_delete=models.CASCADE, default='', verbose_name='trabajador')
    desde = models.DateField('fecha de inicio')
    hasta = models.DateField('fecha de fin')
    cant_dias = models.PositiveIntegerField('días trabajados')
    cant_dias_dieta = models.PositiveIntegerField('días dieta', blank=True, null=True, default=0)

    def __str__(self):
        return '{} => {} => {}'.format(self.codigo_trab, self.desde, self.cant_dias)

    class Meta:
        verbose_name = "alimentación"
        verbose_name_plural = "alimentaciones"
