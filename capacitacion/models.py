from auditlog import registry, models as auditlog_models
from django.db import models
from ges_trab.models import Trabajador
from plantilla.models import Plantilla
from rechum.models import BaseUrls
from rechum.validators import *


class ModoFormacion(BaseUrls, models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.CharField('código', max_length=5, primary_key=True)
    history = auditlog_models.AuditlogHistoryField()

    def __str__(self):
        return self.nombre

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']
        verbose_name = 'modo de formación'
        verbose_name_plural = 'modos de formación'

class TipoActividadCapacitacion(BaseUrls, models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.CharField('código', max_length=3, primary_key=True)
    modo_formacion = models.ForeignKey(ModoFormacion, on_delete=models.CASCADE, null=True)
    history = auditlog_models.AuditlogHistoryField()

    def __str__(self):
        return self.nombre

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']
        verbose_name = 'tipo de actividad'
        verbose_name_plural = 'tipos de actividades'

class Tematica(BaseUrls, models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.CharField('código', max_length=2, primary_key=True)
    history = auditlog_models.AuditlogHistoryField()

    def __str__(self):
        return self.nombre

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']
        verbose_name = 'temática'
        verbose_name_plural = 'temáticas'


class ActividadCapacitacion(BaseUrls, models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.CharField('código', max_length=10)
    tipo_actividad = models.ForeignKey(TipoActividadCapacitacion, on_delete=models.CASCADE, null=True)
    tematica = models.ForeignKey(Tematica, on_delete=models.CASCADE, null=True)
    institucion = models.CharField('institución', max_length=150, null=True)
    lugar = models.CharField(max_length=100, null=True)
    profesor = models.CharField(max_length=150, null=True)
    fecha_inicio = models.DateTimeField(null=True)
    fecha_term = models.DateTimeField(null=True)
    horas = models.PositiveIntegerField(null=True)
    valor_mn = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    valor_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    history = auditlog_models.AuditlogHistoryField()

    def __str__(self):
        return ' {} - {} '.format(self.codigo, self.nombre)

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']
        verbose_name = 'actividad capacitación'
        verbose_name_plural = 'actividades capacitación'

class ActividadCapacitacionTrabajadores(BaseUrls, models.Model):
    actividad = models.ForeignKey(ActividadCapacitacion, on_delete=models.CASCADE)
    trabajador = models.ForeignKey(Trabajador, on_delete=models.SET_NULL, null=True)
    evaluacion = models.CharField('evaluación', max_length=30, null=True)
    tomo = models.CharField(max_length=20, null=True)
    folio = models.CharField(max_length=20, null=True)
    history = auditlog_models.AuditlogHistoryField()

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']
        verbose_name = 'actividad capacitación trabajadores'
        verbose_name_plural = 'actividades capacitación trabajadores'


class Ponencia(BaseUrls, models.Model):
    actividad_trabajador = models.ForeignKey(ActividadCapacitacionTrabajadores, on_delete=models.CASCADE)
    titulo = models.CharField('título', max_length=150)
    premio = models.CharField('código', max_length=30)
    instancia = models.CharField(max_length=30)
    history = auditlog_models.AuditlogHistoryField()

    def __str__(self):
        return self.titulo

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']
        verbose_name = 'ponencia'
        verbose_name_plural = 'ponencias'