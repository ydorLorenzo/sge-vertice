from django.db import models
from django.contrib.auth.models import User

from ges_trab.models import Trabajador


class GrupoCalendario(models.Model):
    CAL_GRPS = (
        ('01', 'Incidencias Trabajador'),
    )
    nombre = models.CharField(max_length=2, choices=CAL_GRPS, blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Grupo de calendarios'
        verbose_name_plural = 'Grupos de calendarios'


####################################################################################
class Calendario(models.Model):
    nombre = models.CharField(max_length=155, blank=True, null=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    fecha_creado = models.DateTimeField(auto_now_add=True)
    grupo = models.ForeignKey(GrupoCalendario, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


####################################################################################
class TipoEvento(models.Model):
    siglas = models.CharField(max_length=10)
    nombre = models.CharField(max_length=155)
    color = models.CharField(max_length=7)
    excluyente = models.BooleanField(default=True)
    calendario = models.ForeignKey(Calendario, on_delete=models.CASCADE)

    def __str__(self):
        return "%s: %s" % (self.siglas, self.nombre)

    class Meta:
        verbose_name = 'Tipo de evento'
        verbose_name_plural = 'Tipos de evento'


####################################################################################
class Evento(models.Model):
    STATUS = (
        ('programado', 'Programado'),
        ('cancelado', 'Cancelado')
    )
    EVENT_TYPE = (
        ('AJ', 'Ausencia Justificada'),
        ('AI', 'Ausencia Injustificada'),
        ('V', 'Vacaciones'),
        ('EF', 'Enfermedad'),
        ('LSS', 'Licencia sin Sueldo'),
        ('Dec.339', 'Decreto 339'),
        ('Otr', 'Otros'),
        ('MI', 'Misión Internacionalista'),
        ('VP', 'Vacaciones Pagadas'),
        ('Fer.Res.15', 'Feriado Resolución 15'),
        ('AC', 'Acción Capacitación'),
        ('Mov', 'Movilizado'),
        ("IL", "interrupción laboral"),
        ("MD", "medida disciplinaria"),
        ("RL", "receso laboral"),
        ('Fr', 'Feriado'),
        ('HT', 'Horas Trabajadas')
    )
    nombre = models.CharField(max_length=155, blank=True, null=True)
    agregado_por = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    afecta_a = models.ForeignKey(Trabajador, on_delete=models.CASCADE, null=True, blank=True)
    comentario = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=12, choices=STATUS, default=STATUS[0])
    programado = models.DateTimeField(auto_now_add=True, editable=False)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(blank=True, null=True)
    todo_dia = models.BooleanField(default=True)
    background = models.BooleanField(default=False)
    tipo_evento = models.ForeignKey(TipoEvento, on_delete=models.DO_NOTHING)

    @property
    def calendario(self):
        return self.tipo_evento.calendario

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Incidencia'
        verbose_name_plural = 'Incidencias'
