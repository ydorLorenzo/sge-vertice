from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from auditlog import registry

from rechum.validators import general_name_validator, positive_number_validator
from rechum.models import BaseUrls


class SeccionSindical(BaseUrls, models.Model):
    nombre = models.CharField(max_length=35, unique=True, validators=[general_name_validator])

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'sección sindical'
        verbose_name_plural = 'secciones sindicales'
        default_permissions = ['read', 'add', 'delete', 'change']


class Cargo(BaseUrls, models.Model):
    codigo = models.PositiveIntegerField(
        'código', unique=True, validators=[MinValueValidator(100000), MaxValueValidator(999999)]
    )
    nombre = models.CharField(max_length=60, unique=True, validators=[general_name_validator])

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']


class UnidadOrg(BaseUrls, models.Model):
    nombre = models.CharField(max_length=60, unique=True, validators=[general_name_validator])

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['pk']
        verbose_name = 'unidad organizacional'
        verbose_name_plural = 'unidades organizacionales'
        default_permissions = ['read', 'add', 'delete', 'change']


class Departamento(BaseUrls, models.Model):
    codigo = models.CharField(
        'código', max_length=5, unique=True, validators=[
        RegexValidator(
            regex="^[0-9]{5}$",
            message="Campo obligatorio. Cadena numérica de 5 dígitos")
    ])
    nombre = models.CharField(max_length=60, validators=[general_name_validator])
    unidad = models.ForeignKey(UnidadOrg, on_delete=models.DO_NOTHING, verbose_name='unidad organizacional', related_name='departamentos')
    seccion = models.ForeignKey(SeccionSindical, on_delete=models.DO_NOTHING, verbose_name='sección sindical')
    dirige = models.ForeignKey('self', null=True, blank=True, related_name='departamentos', on_delete=models.DO_NOTHING)
    cargos = models.ManyToManyField(Cargo, through='plantilla.Plantilla', through_fields=('departamento', 'cargo'))

    def __str__(self):
        if self.dirige_id is not None:
            return "%s - %s" % (self.dirige.nombre, self.nombre)
        return self.nombre

    class Meta:
        ordering = [models.F('id').asc(nulls_last=True)]
        default_permissions = ['read', 'add', 'delete', 'change']


class EscalaSalarial(BaseUrls, models.Model):
    grupo = models.CharField(max_length=8, unique=True)
    coeficientes = models.DecimalField(max_digits=3, decimal_places=2, validators=[positive_number_validator])
    salario_escala = models.DecimalField(max_digits=5, decimal_places=2, validators=[positive_number_validator])
    tarifa_horaria = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(1)])

    def __str__(self):
        return self.grupo

    class Meta:
        verbose_name_plural = 'escalas salariales'


class EscalaSalarialReforma(BaseUrls, models.Model):
    grupo = models.CharField(max_length=8, unique=True)
    coeficiente = models.DecimalField(max_digits=16, decimal_places=15, validators=[positive_number_validator])
    salario_escala = models.DecimalField(max_digits=6, decimal_places=2, validators=[positive_number_validator])

    def __str__(self):
        return self.grupo

    class Meta:
        verbose_name = 'escala salarial reforma'
        verbose_name_plural = 'escalas salariales reforma'


class CIES(BaseUrls, models.Model):
    escala = models.ForeignKey(EscalaSalarial, on_delete=models.CASCADE, verbose_name='escala salarial')
    tecnico = models.BooleanField('técnico')
    pago_adicional = models.BooleanField()
    porciento_30 = models.BooleanField('pago del 30%')
    cies = models.DecimalField('CIES', max_digits=5, decimal_places=2, default=0, validators=[positive_number_validator])

    def __str__(self):
        return 'Escala: {}, CIES {}'.format(self.escala, self.cies)

    class Meta:
        verbose_name = 'CIES'
        verbose_name_plural = 'CIES'
        default_permissions = ['read', 'add', 'delete', 'change']


class Antiguedad(BaseUrls, models.Model):
    escala = models.ForeignKey(EscalaSalarial, on_delete=models.CASCADE, verbose_name='escala salarial')
    tecnico = models.BooleanField('técnico')
    pago_adicional = models.BooleanField()
    porciento_5 = models.BooleanField('pago del 5%')
    valor = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[positive_number_validator])

    def __str__(self):
        return 'Escala: {}, Valor {}'.format(self.escala, self.valor)

    class Meta:
        verbose_name = 'antigüedad'
        verbose_name_plural = 'antigüedades'
        default_permissions = ['read', 'add', 'delete', 'change']


class Calificacion(BaseUrls, models.Model):
    codigo = models.CharField(
        'código', max_length=2, unique=True,
        validators=[RegexValidator(
            regex='^[0-9]{2}$',
            message='Debe tener exactamente dos caracteres numéricos.'
        )]
    )
    nombre = models.CharField(max_length=60, unique=True, validators=[general_name_validator])

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['codigo']
        verbose_name = 'calificación'
        verbose_name_plural = 'calificaciones'
        default_permissions = ['read', 'add', 'delete', 'change']


class Especialidad(BaseUrls, models.Model):
    calificacion = models.ForeignKey(Calificacion, on_delete=models.CASCADE, default='', verbose_name='calificación')
    codigo = models.CharField(
        'código', max_length=8, unique=True,
        validators=[RegexValidator(
            regex='^[0-9]{8}$',
            message='Debe ser una cadena numérica de 8 dígitos.'
        )]
    )
    nombre = models.CharField(max_length=60, unique=True, validators=[general_name_validator])

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['codigo']
        verbose_name_plural = 'especialidades'
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']

registry.auditlog.register(Cargo)
