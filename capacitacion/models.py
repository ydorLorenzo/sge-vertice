from auditlog import registry, models as auditlog_models
from django.core.validators import validate_image_file_extension
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from adm import models as adm
from ges_trab.models import Trabajador
from plantilla.models import Plantilla
from rechum.models import BaseUrls
from rechum.validators import *


class ModoFormacion(BaseUrls, models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.CharField('código', max_length=5, unique=True)
    history = auditlog_models.AuditlogHistoryField()

    def __str__(self):
        return self.nombre

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']

class TipoActividadCapacitacion(BaseUrls, models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.CharField('código', max_length=2, unique=True)
    modo_formacion = models.ForeignKey(ModoFormacion, on_delete=models.CASCADE, null=True)
    history = auditlog_models.AuditlogHistoryField()

    def __str__(self):
        return self.nombre

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']


class Tematica(BaseUrls, models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.CharField('código', max_length=2, unique=True)
    history = auditlog_models.AuditlogHistoryField()

    def __str__(self):
        return self.nombre

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']


class ActividadCapacitacion(BaseUrls, models.Model):
    nombre = models.CharField(max_length=150, null=False)
    codigo = models.CharField('código', max_length=10, unique=True)
    tipo_actividad = models.ForeignKey(TipoActividadCapacitacion, on_delete=models.CASCADE, null=False)
    tematica = models.ForeignKey(Tematica, on_delete=models.CASCADE, null=False)
    institucion = models.CharField('institución', max_length=150, null=False)
    lugar = models.CharField(max_length=20, null=False)
    profesor = models.CharField(max_length=150, null=False)
    fecha_ini = models.DateField('fecha de inicio')
    fecha_fin = models.DateField('fecha de fin')
    cant_horas = models.PositiveIntegerField('cantidad de horas', default=0)
    importe_MN = models.DecimalField(max_digits=6, decimal_places=2, editable=False, default=0.00)
    importe_USD = models.DecimalField(max_digits=6, decimal_places=2, editable=False, default=0.00)
    history = auditlog_models.AuditlogHistoryField()

    def __str__(self):
        return ' {} - {} '.format(self.codigo, self.nombre)

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']


class ActividadCapacitacionTrabajadores(BaseUrls, models.Model):
    actividad = models.ForeignKey(ActividadCapacitacion, on_delete=models.CASCADE, null=False)
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, null=False)
    evaluacion = models.CharField('evaluación', max_length=30, null=True)
    tomo = models.CharField(max_length=20, null=True)
    folio = models.CharField(max_length=20, null=True)
    history = auditlog_models.AuditlogHistoryField()

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']

class Ponencia(BaseUrls, models.Model):
    actividad_trabajador = models.ForeignKey(ActividadCapacitacionTrabajadores, on_delete=models.CASCADE, null=False)
    titulo = models.CharField('título', max_length=150)
    premio = models.CharField('código', max_length=30)
    instancia = models.CharField(max_length=30)
    history = auditlog_models.AuditlogHistoryField()

    def __str__(self):
        return self.titulo

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']