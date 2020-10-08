import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from dateutil.relativedelta import relativedelta

from adm.models import UnidadOrg, Departamento
from ges_trab.models import Trabajador


class TipoIncidencia:
    VACACIONES = 'V'
    CERTIFICADO_MEDICO = 'Cm'
    LICENCIA_SIN_SUELDO = 'LSS'
    MISION_INTERNACIONALISTA = 'MI'
    INTERRUPCION = 'I'
    BAJA = 'B'
    ALTA = 'A',
    MOVILIZACION = 'M'
    ENFERMO = 'E'
    RECESO_LABORAL_RETRIBUIDO = 'Fr'
    PRESTACION_SOCIAL = 'F'

    choices = (
        (VACACIONES, 'Vacaciones'),
        (CERTIFICADO_MEDICO, 'Certificado Médico'),
        (LICENCIA_SIN_SUELDO, 'Licencia sin Sueldo'),
        (MISION_INTERNACIONALISTA, 'Misión Internacionalista'),
        (INTERRUPCION, 'Interrupción'),
        (BAJA, 'Baja'),
        (ALTA, 'Alta'),
        (MOVILIZACION, 'Movilización'),
        (ENFERMO, 'Enfermo'),
        (RECESO_LABORAL_RETRIBUIDO, 'Receso Laboral Retribuido'),
        (PRESTACION_SOCIAL, 'Prestación Social')
    )


class Ausencia(models.Model):
    codigo_trab = models.ForeignKey(Trabajador, on_delete=models.CASCADE, default='', verbose_name='trabajador')
    fecha = models.DateField(verbose_name='fecha de registro')
    horas = models.DecimalField(decimal_places=2, max_digits=3)
    causal = models.CharField(max_length=3, choices=TipoIncidencia.choices, default=TipoIncidencia.VACACIONES)

    @property
    def trabajador(self):
        return self.codigo_trab

    def __str__(self):
        return '{} => {} => {}'.format(self.codigo_trab, self.fecha, self.causal)


class Mes:
    ENERO = 1
    FEBRERO = 2
    MARZO = 3
    ABRIL = 4
    MAYO = 5
    JUNIO = 6
    JULIO = 7
    AGOSTO = 8
    SEPTIEMBRE = 9
    OCTUBRE = 10
    NOVIEMBRE = 11
    DICIEMBRE = 12

    choices = ((ENERO, 'Enero'), (FEBRERO, 'Febrero'), (MARZO, 'Marzo'), (ABRIL, 'Abril'), (MAYO, 'Mayo'),
               (JUNIO, 'Junio'), (JULIO, 'Julio'), (AGOSTO, 'Agosto'), (SEPTIEMBRE, 'Septiembre'), (OCTUBRE, 'Octubre'),
               (NOVIEMBRE, 'Noviembre'), (DICIEMBRE, 'Diciembre'))


class TarjetaCNC(models.Model):
    codigo_trab = models.ForeignKey(Trabajador, on_delete=models.CASCADE, default='', verbose_name='Trabajador')
    mes = models.PositiveSmallIntegerField(choices=Mes.choices, default=datetime.datetime.now().month, validators=[
        MaxValueValidator(12), MinValueValidator(1)
    ])
    anno = models.PositiveSmallIntegerField(verbose_name='año', default=datetime.datetime.now().year, validators=[
        MaxValueValidator(2150), MinValueValidator(1900)
    ])
    cant_dias = models.PositiveIntegerField(verbose_name='cant. días')
    salario = models.DecimalField(decimal_places=2, max_digits=7, verbose_name='Salario', default=0.00)

    @property
    def trabajador(self):
        return self.codigo_trab

    @property
    def fecha_primer_dia_mes(self):
        return datetime.datetime.strptime(str(self.mes) + '/' + str(self.anno), '%m/%Y')

    @property
    def fecha_ultimo_dia_mes(self):
        return self.fecha_primer_dia_mes + relativedelta(months=1, days=-1)

    def __str__(self):
        return '{} => {} => {}'.format(self.codigo_trab, str(self.mes) + '/' + str(self.anno),
                                       self.salario)
