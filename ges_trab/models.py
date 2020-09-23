import datetime

from django.core.validators import MaxValueValidator, validate_image_file_extension
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from auditlog import registry, models as auditlog_models

from adm import models as adm
from plantilla.models import Plantilla
from rechum.validators import *
from rechum.models import BaseUrls


class Actividad(BaseUrls, models.Model):
    descripcion = models.CharField('descripción', max_length=60, blank=True, null=True, validators=[general_name_validator])

    def __str__(self):
        return self.descripcion

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']
        verbose_name_plural = "actividades"


class Trabajador(BaseUrls, models.Model):
    # Datos personales del trabajador
    primer_nombre = models.CharField(max_length=20, validators=[person_name_validator])
    segundo_nombre = models.CharField(max_length=20, blank=True, null=True, validators=[person_name_validator])
    apellidos = models.CharField(max_length=60, validators=[person_name_validator])
    ci = models.CharField('carnet de identidad', max_length=11, unique=True)
    foto = models.ImageField(upload_to='fotos', blank=True, validators=[validate_image_file_extension])
    SEXO_OPT = (('M', 'Masculino'), ('F', 'Femenino'))
    sexo = models.CharField(max_length=1, choices=SEXO_OPT, default=SEXO_OPT[0])
    ETNIA_OPT = (('B', 'Blanca'), ('M', 'Mestiza'), ('N', 'Negra'))
    etnia = models.CharField(max_length=1, choices=ETNIA_OPT, default=ETNIA_OPT[0])
    motivo_alta = models.CharField(max_length=60, default="Ocupar plaza vacante", blank=True, null=True)
    lugar_nacimiento = models.CharField('lugar de nacimiento', max_length=30, blank=True)
    estatura = models.FloatField(max_length=3, blank=True, null=True)
    peso = models.FloatField(max_length=3, blank=True, null=True)
    nombre_madre = models.CharField('nombre de la madre', max_length=40, blank=True)
    nombre_padre = models.CharField('nombre del padre', max_length=40, blank=True)
    ESTADO_OPT = (
        ('Soltero', 'Soltero(a)'), ('Casado', 'Casado(a)'), ('Divorciado', 'Divorciado(a)'), ('Viudo', 'Viudo(a)'))
    estado_civil = models.CharField(max_length=10, choices=ESTADO_OPT, default=ESTADO_OPT[0])
    hijos = models.PositiveIntegerField('cantidad de hijos', default=0, blank=True)
    LICENCIA_OPT = (('0', 'Primera'), ('1', 'Segunda'), ('2', 'Tercera'), ('3', 'Cuarta'), ('4', 'Quinta'))
    licencia = models.CharField('licencia de conducción', max_length=20, blank=True, choices=LICENCIA_OPT, default='No procede')
    enfermedades = models.CharField('enfermedades que padece', max_length=100, default='Ninguna', blank=True)
    direccion = models.CharField('dirección', max_length=500)
    telefono = models.CharField('teléfono', max_length=8, blank=True)
    fecha_nac = models.DateField("fecha de nacimiento", editable=False, null=True, blank=True, validators=[
        MinAgeValidator(15), MaxAgeValidator(85)
    ])
    org_plantilla = models.PositiveIntegerField('organización en la plantilla')
    unidad_org = models.ForeignKey(adm.UnidadOrg, on_delete=models.DO_NOTHING, verbose_name='unidad organizacional')
    departamento = models.ForeignKey(adm.Departamento, on_delete=models.DO_NOTHING, verbose_name='departamento', related_name='trabajadores')
    cargo = models.ForeignKey(adm.Cargo, on_delete=models.DO_NOTHING, verbose_name='cargo')
    codigo_interno = models.CharField('código interno', max_length=3, unique=True, validators=[RegexValidator(
        regex='^[0-9]{3}$',
        message=_('Código interno inválido. Código de 3 números.')
    )])
    usuario = models.CharField('usuario', max_length=20, blank=True, null=True, default='Ninguno', validators=[RegexValidator(
        regex=' ', inverse_match=True, message=_('Usuario inválido. El valor no puede contener espacios.'))
    ])
    residencia = models.CharField('municipio de residencia', max_length=20)
    # Datos laborales y salariales
    CATEGORIA_OPT = (('A', 'Administrativo'), ('C', 'Cuadro '), ('O', 'Operario'), ('S', 'Servicio'),
                     ('T', 'Técnico '))
    categoria = models.CharField('categoría ocupacional', choices=CATEGORIA_OPT, max_length=15)
    PLANTILLA_OPT = (('A', 'Administrativo'), ('P', 'Productivo'))
    t_plantilla = models.CharField('tipo de plantilla', choices=PLANTILLA_OPT, max_length=15, blank=True)
    CONTRATO_OPT = (
        ('1', 'Nombramiento'), ('2', 'Indeterminado'), ('3', 'Determinado por tiempo definido'), ('4', 'Adiestramiento'),
        ('5', 'Disponible'),
        ('6', 'A prueba'), ('7', 'Determinado por sustitución de trabajador'))
    t_contrato = models.CharField('tipo de contrato', choices=CONTRATO_OPT, max_length=20)
    FUERZA_I_OPT = (('1', 'Otras Empresas'), ('2', 'Reclusos'), ('3', 'Microbrigrada'), ('4', 'Otros'))
    fuerza_i = models.CharField('fuerza irregular', choices=FUERZA_I_OPT, max_length=20, blank=True)
    T_PAGO_OPT = (('S', 'A tiempo'), ('V', 'Por rendimiento'))
    t_pago = models.CharField('tipo de pago', choices=T_PAGO_OPT, max_length=20)
    j_laboral = models.BooleanField('jornada laboral de 208 horas', default=False)
    escala_salarial = models.ForeignKey(adm.EscalaSalarial, on_delete=models.DO_NOTHING)
    salario_escala = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    incre_res = models.DecimalField('pago por perfeccionamiento', max_digits=5, decimal_places=2)
    sal_bas = models.DecimalField('salario básico', max_digits=5, decimal_places=2)
    POR_CIES_OPT = (('0', '0%'), ('1', '30%'), ('2', '50%'))
    por_cies = models.CharField('% CIES', max_length=3, choices=POR_CIES_OPT, default=POR_CIES_OPT[0])
    cies = models.DecimalField('CIES', max_digits=5, decimal_places=2)
    sal_plus = models.DecimalField('salario plus', max_digits=5, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])
    sal_cond_anor = models.DecimalField('salario condiciones anormales', max_digits=5, decimal_places=2, default=0.0)
    POR_ANTI_OPT = (('0', '0%'), ('1', '5%'), ('2', '10%'))
    por_anti = models.CharField("% antigüedad", choices=POR_ANTI_OPT, max_length=3, default=POR_ANTI_OPT[0])
    antiguedad = models.DecimalField('antigüedad', max_digits=5, decimal_places=2, default=0.0)
    fecha_contrato = models.DateField("fecha de contrato", default=datetime.date.today)
    fecha_alta = models.DateField("fecha de alta al cargo", default=datetime.date.today)
    fecha_disponible = models.DateField("fecha de inicio disponibilidad", null=True, blank=True)
    fecha_ingreso = models.DateField("fecha de ingreso al organismo", default=datetime.date.today)
    albergado = models.BooleanField(default=False)
    CAT_CIENT_OPT = (('1', 'Ninguna'), ('2', 'Máster'), ('3', 'Doctor'))
    cat_cient = models.CharField('categoría científica', max_length=10, choices=CAT_CIENT_OPT)
    sal_cat_cient = models.DecimalField(
        'salario por cat. científica', max_digits=5, decimal_places=2, blank=True, null=True, default=0.0)
    salario_total = models.DecimalField('salario total', max_digits=7, blank=True, null=True, decimal_places=2)
    salario_jornada_laboral = models.DecimalField('salario por jornada laboral', max_digits=5, blank=True,
                                                  null=True, default=0.0, decimal_places=2)
    # Datos docentes
    actividad = models.ForeignKey(Actividad, on_delete=models.DO_NOTHING, blank=True, null=True)
    calificacion = models.ForeignKey(
        adm.Calificacion, on_delete=models.DO_NOTHING, verbose_name="calificación", blank=True, null=True)
    especialidad = models.ForeignKey(adm.Especialidad, on_delete=models.DO_NOTHING, blank=True, null=True)
    anno_graduado = models.PositiveIntegerField("año de graduado", blank=True, null=True)
    centro_graduacion = models.CharField('centro de graduación', max_length=40, default='Ninguno')
    pais_graduacion = models.CharField(max_length=20, verbose_name="País de graduación", default='Ninguno')
    ESCOLARIDAD_OPT = (
        ('6to', '6to Grado'), ('9no ', '9no Grado'), ('12mo ', '12mo Grado'), ('TM', 'Técnico Medio'),
        ('OC', 'Obrero Calificado'), ('Univ', 'Universitario'), ('FOC', 'Facultad Obrero Campesino'))
    escolaridad = models.CharField(max_length=20, choices=ESCOLARIDAD_OPT)
    idioma = models.CharField(max_length=20, blank=True, null=True)
    ORG_DEF = (
        ('MTT', 'MTT'), ('FEI', 'FEI'), ('BPD-LR ', 'BPD-LR'), ('BPD-PTG ', 'BPD-PTG'), ('U/R', 'U/R'),
        ('Imp', 'Imprescindible'))
    orga_defensa = models.CharField('organización en la defensa', max_length=20, choices=ORG_DEF)
    unidad_militar = models.CharField(max_length=20, blank=True)
    estado_mayor = models.CharField(max_length=20, blank=True)
    a_mision = models.CharField("año de misión", blank=True, max_length=15)
    ORG_OPT = (('1', 'UJC'), ('2', 'PCC'))
    militancia = models.CharField(max_length=5, choices=ORG_OPT, blank=True)
    org_masas = models.CharField('organizaciones de masas', max_length=20, validators=[general_name_validator])
    org_prof = models.CharField('organizaciones profesionales', max_length=20, blank=True, validators=[general_name_validator])
    org_cult = models.CharField('organizaciones culturales', max_length=20, blank=True, validators=[general_name_validator])

    # Talla
    zapato = models.CharField(max_length=4)
    saya = models.CharField(max_length=5, blank=True)
    blusa = models.CharField(max_length=4, blank=True)
    pullover = models.CharField(max_length=4)
    pitusa = models.CharField(max_length=5, blank=True)
    camisa = models.CharField(max_length=5, blank=True)
    derecho = models.BooleanField(default=True)

    # Baja
    fecha_baja = models.DateField(null=True, blank=True)
    MOTIVOS_BAJA = (
        ('01', 'Rescisión del contrato a voluntad del trabajador'),
        ('02', 'Motivos salariales'),
        ('03', 'Deficiente organización del trabajo'),
        ('04', 'Lejanía del centro de trabajo'),
        ('05', 'Inconveniencia del horario de trabajo'),
        ('06', 'No trabajar dentro de la especialidad'),
        ('07', 'Condiciones anormales de trabajo'),
        ('08', 'Escasa posibilidad de superación'),
        ('09', 'Problemas de vivienda y o ausencia de servicios sociales'),
        ('10', 'Inconformidad con los métodos de dirección'),
        ('11', 'Matrimonio atención a menores y familiares'),
        ('12', 'Bajas de trabajadores por sanción laboral'),
        ('13', 'Bajas por no reincorporarse después de cumplido el período de vacaciones o licencia no retribuida'),
        ('14', 'Bajas por salida del país'),
        ('15', 'Bajas por Jubilación'),
        ('16', 'Bajas por Fallecimiento'),
        ('17', 'Otras bajas por fluctuación')
    )
    motivo_baja = models.CharField(max_length=2, choices=MOTIVOS_BAJA, null=True, blank=True)
    history = auditlog_models.AuditlogHistoryField()

    def geturl(self):
        return reverse('EditarTrabajador', kwargs={'trabajador_id': self.id})

    @property
    def nombre_completo(self):
        if self.segundo_nombre:
            return '%s %s %s' % (self.primer_nombre, self.segundo_nombre, self.apellidos)
        return '%s %s' % (self.primer_nombre, self.apellidos)

    def __str__(self):
        return self.nombre_completo

    class Meta:
        verbose_name_plural = 'trabajadores'
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report', 'full-control']


class Alta(Trabajador):
    objects = Trabajador.objects.filter(fecha_baja__isnull=True)

    class Meta:
        proxy = True


class BajaOther(Trabajador):
    objects = Trabajador.objects.filter(fecha_baja__isnull=False)

    class Meta:
        proxy = True


class Movimiento(BaseUrls, models.Model):
    fecha = models.DateField(max_length=20, verbose_name="Fecha del movimiento", blank=True, null=True)
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE)
    TIPO_OPT = (('1', 'Promoción'), ('2', 'Cambio de área'), ('3', 'Ambos'))
    tipo = models.CharField(max_length=100, verbose_name="Tipo de movimiento", blank=True, null=True,
                            default='No definido')
    cargo_ant = models.CharField(max_length=60, verbose_name="Cargo anterior", blank=True, null=True)
    cargo_act = models.CharField(max_length=60, verbose_name="Cargo actual", blank=True, null=True)
    area_ant = models.CharField(max_length=60, verbose_name="Departamento anterior", blank=True, null=True)
    area_act = models.CharField(max_length=60, verbose_name="Departamento actual", blank=True, null=True)
    cies_ant = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='CIES')
    cies_act = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='CIES')
    incre_res_ant = models.DecimalField(max_digits=5, decimal_places=2,
                                        verbose_name='Pago por perfeccionamiento anterior')
    incre_res_act = models.DecimalField(max_digits=5, decimal_places=2,
                                        verbose_name='Pago por perfeccionamiento actual')
    categoria_ant = models.CharField(max_length=15, verbose_name='Categoría ocupacional anterior')
    categoria_act = models.CharField(max_length=15, verbose_name='Categoría ocupacional actual')
    antiguedad_ant = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    antiguedad_act = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    salario_escala_ant = models.DecimalField(verbose_name='Salario escala anterior', max_digits=5, decimal_places=2,
                                             default=0.00)
    salario_escala_act = models.DecimalField(verbose_name='Salario escala actual', max_digits=5, decimal_places=2,
                                             default=0.00)
    escala_salarial_ant = models.CharField(max_length=5)
    escala_salarial_act = models.CharField(max_length=5)
    salario_total_ant = models.DecimalField(max_digits=7, verbose_name='Salario Total anterior', blank=True, null=True,
                                            decimal_places=2)
    salario_total_act = models.DecimalField(max_digits=7, verbose_name='Salario Total actual', blank=True, null=True,
                                            decimal_places=2)
    sal_plus_ant = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Salario plus anterior',
                                       default=0.00)
    sal_plus_act = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Salario plus actual', default=0.00)
    sal_cat_cient_ant = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Salario x cat. científica",
                                            blank=True, null=True, default=0.00)
    sal_cat_cient_act = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Salario x cat. científica",
                                            blank=True, null=True, default=0.00)

    def __str__(self):
        return 'Trabajador: {0} Movimiento: {1}'.format(self.trabajador, self.tipo)

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']


class Cpl(models.Model):
    fecha = models.DateField()
    valor = models.DecimalField(max_digits=3, decimal_places=2)
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return 'Trabajador: {0} Valor CPL: {1} Fecha: {2}'.format(self.trabajador, self.valor, self.fecha)

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']


class NucleoFamiliar(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE)
    PARENTESCO_OPT = (
        ('0', 'Padre'), ('1', 'Madre'), ('2', 'Hermano(a)'), ('3', 'Abuelo(a)'), ('4', 'Tio(a)'), ('5', 'Primo(a)'),
        ('6', 'Pareja'), ('7', 'Esposo(a)'), ('8', 'Hijastro(a)'), ('9', 'Madrasta'), ('10', 'Padrastro'),
        ('11', 'Otro'))
    parentesco = models.CharField(max_length=10, choices=PARENTESCO_OPT, blank=True, null=True)
    fecha_nac = models.DateField(verbose_name='Fecha de nacimiento', blank=True, null=True)
    enfermedades = models.CharField(max_length=100, verbose_name='Enfermedades que padece', default='Ninguna')
    vinc_lab = models.BooleanField(verbose_name='Vinculo laboral')
    salario_dev = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Salario que devenga', blank=True,
                                      null=True)

    def __str__(self):
        return self.trabajador.primer_nombre

    class Meta:
        default_permissions = ['read', 'add', 'delete', 'change', 'export', 'report']


class Baja(models.Model):
    primer_nombre = models.CharField(max_length=20, verbose_name='Primer nombre')
    segundo_nombre = models.CharField(max_length=20, blank=True, verbose_name='Segundo nombre')
    apellidos = models.CharField(max_length=60, verbose_name='Apellidos')
    ci = models.CharField(max_length=11, verbose_name='Carnet de Identidad', unique=True)
    causa = models.CharField(max_length=60, verbose_name='Causa de la baja', default='No definida')
    foto = models.ImageField(upload_to='fotos', verbose_name='Foto', blank=True)
    SEXO_OPT = (('M', 'Masculino'), ('F', 'Femenino'))
    sexo = models.CharField(max_length=1, choices=SEXO_OPT, verbose_name='Sexo', default=SEXO_OPT[0])
    ETNIA_OPT = (('B', 'Blanca'), ('M', 'Mestiza'), ('N', 'Negra'))
    etnia = models.CharField(max_length=10, choices=ETNIA_OPT, verbose_name='Etnia', default=ETNIA_OPT[0])
    lugar_nacimiento = models.CharField(max_length=30, verbose_name='Lugar de nacimiento', blank=True)
    telefono = models.CharField(max_length=8, verbose_name='Teléfono', blank=True)
    codigo_interno = models.CharField(max_length=3, unique=True, verbose_name='Código Interno')
    usuario = models.CharField(max_length=20, verbose_name='Usuario', blank=True, null=True)
    unidad_org = models.ForeignKey(adm.UnidadOrg, on_delete=models.DO_NOTHING, verbose_name='Unidad organizacional')
    departamento = models.ForeignKey(adm.Departamento, on_delete=models.DO_NOTHING, verbose_name='Departamento')
    cargo = models.ForeignKey(adm.Cargo, on_delete=models.DO_NOTHING, verbose_name='Cargo')
    salario_escala = models.DecimalField(verbose_name='Salario escala', max_digits=5, decimal_places=2, default=0.00)
    motivo_baja = models.CharField(max_length=20, blank=True, verbose_name='Motivo de la Baja')
    cies = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='CIES')
    antiguedad = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    salario_total = models.DecimalField(max_digits=7, verbose_name='Salario Total', blank=True, null=True,
                                        decimal_places=2)
    incre_res = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Pago por perfeccionamiento')
    escala_salarial = models.ForeignKey(adm.EscalaSalarial, on_delete=models.DO_NOTHING)
    categoria = models.CharField(max_length=15, verbose_name='Categoría ocupacional')
    fecha_alta = models.DateField(verbose_name="Fecha de alta al cargo")
    fecha_baja = models.DateField(verbose_name="Fecha de baja")
    fecha_disponible = models.DateField(blank=True, verbose_name="Fecha de inicio disponibilidad", null=True)
    fecha_ingreso = models.DateField(verbose_name="Fecha de ingreso al organismo")
    especialidad = models.ForeignKey(adm.Especialidad, on_delete=models.DO_NOTHING, verbose_name="Especialidad", null=True,
                                     blank=True)
    anno_graduado = models.PositiveIntegerField(verbose_name="Año de graduado", null=True, blank=True)
    ESCOLARIDAD_OPT = (
        ('6to', '6to Grado'), ('9no', '9no Grado'), ('12mo', '12mo Grado'), ('TM', 'Técnico Medio'),
        ('OC', 'Obrero Calificado'),
        ('Univ', 'Universitario'))
    escolaridad = models.CharField(max_length=20, choices=ESCOLARIDAD_OPT, verbose_name="Escolaridad")
    sal_cat_cient = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Salario x cat. científica",
                                        blank=True, null=True, default=0.00)
    sal_plus = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Salario plus', default=0.00)
    salario_jornada_laboral = models.DecimalField(max_digits=5, verbose_name='Salario por Jornada Laboral', blank=True,
                                                  null=True, default=0.00, decimal_places=2)
    j_laboral = models.BooleanField(verbose_name='Jornada Laboral de 208 horas', default=False)

    def __str__(self):
        return '{} {} {} {}'.format(self.codigo_interno, self.primer_nombre, self.segundo_nombre, self.apellidos)


class Disponible(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE)
    fecha = models.DateField("fecha de disponibilidad")

    def __str__(self):
        return self.trabajador.primer_nombre, self.trabajador.apellidos, self.trabajador.codigo_interno


registry.auditlog.register(Trabajador)
registry.auditlog.register(Movimiento)
