import datetime

from django.db import models

from adm.models import UnidadOrg, Departamento
from ges_trab.models import Trabajador


class Ausencia(models.Model):
    codigo_trab = models.ForeignKey(Trabajador, on_delete=models.CASCADE, default='', verbose_name='Trabajador')
    fecha = models.DateField(verbose_name='Fecha de registro')
    horas = models.DecimalField(decimal_places=2, max_digits=3, null=False, blank=False, verbose_name='Horas')
    opciones = (('V', 'Vacaciones'), ('Cm', 'Certificado Médico'), ('LSS', 'Licencia sin Sueldo'),
                ('MI', 'Misión Internacionalista'), ('I', 'Interrupción'), ('B', 'Baja'), ('A', 'Alta'),
                ('M', 'Movilización'), ('E', 'Enfermo'), ('Fr', 'Receso Laboral Retribuido'),
                ('F', 'Prestación Social'))
    causal = models.CharField(max_length=3, choices=opciones, verbose_name='Causal', default=opciones[0])

    def __str__(self):
        return '{} => {} => {}'.format(self.codigo_trab, self.fecha, self.causal)


class TarjetaCNC(models.Model):
    codigo_trab = models.ForeignKey(Trabajador, on_delete=models.CASCADE, default='', verbose_name='Trabajador')
    opciones = (('Enero', 'Enero'), ('Febrero', 'Febrero'), ('Marzo', 'Marzo'), ('Abril', 'Abril'),
                ('Mayo', 'Mayo'), ('Junio', 'Junio'), ('Julio', 'Julio'), ('Agosto', 'Agosto'),
                ('Septiembre', 'Septiembre'), ('Octubre', 'Octubre'), ('Noviembre', 'Noviembre'),
                ('Diciembre', 'Diciembre'))
    mes = models.CharField(max_length=12, choices=opciones, verbose_name='Mes', default=opciones[0])
    anno = models.PositiveIntegerField(verbose_name='Año', blank=False, null=False,
                                       default=datetime.datetime.now().year)
    cant_dias = models.PositiveIntegerField(null=False, blank=False, verbose_name='Cant. días')
    salario = models.DecimalField(decimal_places=2, max_digits=7, blank=False, verbose_name='Salario', default=0.00,
                                  null=False)

    def __str__(self):
        return '{} => {} => {}'.format(self.codigo_trab, self.mes + '/' + self.anno.__str__(),
                                       self.salario)
