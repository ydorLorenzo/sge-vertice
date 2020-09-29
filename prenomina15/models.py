from auditlog import registry, models as auditlog_models
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse_lazy

from adm.models import EscalaSalarial, Cargo
from entrada_datos.models import OT, Actividad
from ges_trab.models import Trabajador
from rechum.models import BaseUrls


class SalarioMax(BaseUrls, models.Model):
    grupo_esc = models.ForeignKey(EscalaSalarial, on_delete=models.CASCADE, default='', verbose_name="grupo escala")
    sal = models.DecimalField('salario', max_digits=6, decimal_places=2)
    TIPO_OPT = (('OT', 'Obra Turismo'), ('VT', 'Vivienda para Turismo'))
    tipo = models.CharField('tipo de servicio', max_length=2, choices=TIPO_OPT, default='')

    def __str__(self):
        return ' {} - {} - {}'.format(self.tipo, self.grupo_esc, self.sal)


class Formato(BaseUrls, models.Model):
    formato = models.CharField(max_length=6)
    factor = models.DecimalField(max_digits=2, decimal_places=1)

    def __str__(self):
        return '{}'.format(self.formato)


class EspecialidadOrganizativa(BaseUrls, models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.CharField('código', max_length=2, unique=True)

    def __str__(self):
        return self.nombre


class Especialidad(BaseUrls, models.Model):
    nombre = models.CharField(max_length=150)
    factor = models.DecimalField(max_digits=2, decimal_places=1)
    siglas = models.CharField(max_length=2)
    md = models.DecimalField('memoria descriptiva', max_digits=4, decimal_places=2, default=0.00, editable=False)
    lc = models.DecimalField('listado de cantidades', max_digits=4, decimal_places=2, default=0.00, editable=False)
    pr = models.DecimalField('presupuesto', max_digits=4, decimal_places=2, default=0.00, editable=False)
    especialidad_organizativa = models.ForeignKey(EspecialidadOrganizativa, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = 'especialidades'


class Obra(BaseUrls, models.Model):
    orden_trab = models.ForeignKey(OT, on_delete=models.PROTECT, default='', verbose_name="orden de trabajo")
    nombre = models.CharField(max_length=20)
    TIPO_OPT = (('OT', 'Obra Turismo'), ('VT', 'Vivienda para Turismo'), ('R6', 'Resolucion 6'))
    tipo = models.CharField('tipo de servicio', max_length=2, choices=TIPO_OPT, default='')
    horas_a2 = models.PositiveIntegerField('horas A2')
    gesc = models.ForeignKey(EscalaSalarial, on_delete=models.PROTECT, default='', verbose_name="grupo escala")
    usuarios = models.ManyToManyField(User)
    owner = models.CharField(max_length=20, editable=False, default='admin', verbose_name="dueño")
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'servicio'
        verbose_name_plural = 'servicios'


class PlantillaServicio(BaseUrls, models.Model):
    servicio = models.ForeignKey(Obra, on_delete=models.DO_NOTHING)
    especialidad = models.ForeignKey(EspecialidadOrganizativa, on_delete=models.DO_NOTHING, null=True, blank=True)
    cargo = models.ForeignKey(Cargo, on_delete=models.DO_NOTHING)
    escala_salarial = models.ForeignKey(EscalaSalarial, on_delete=models.DO_NOTHING)
    cant_plazas = models.IntegerField('cantidad de plazas', default=1)
    disponibles = models.IntegerField(editable=False)

    def __str__(self):
        return self.cargo.nombre + ' Grupo ' + self.escala_salarial.grupo + ' - ' + self.servicio.nombre

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.id:
            self.disponibles = self.cant_plazas
        super(PlantillaServicio, self).save(
            force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def get_detail_url(self):
        return reverse_lazy('plantillaservicio_detail', kwargs={"servicio_id": self.servicio_id, "pk": self.id})

    def get_update_url(self):
        return reverse_lazy('plantillaservicio_update', kwargs={"servicio_id": self.servicio_id, "pk": self.id})

    def get_delete_url(self):
        return reverse_lazy('plantillaservicio_delete', kwargs={"servicio_id": self.servicio_id, "pk": self.id})

    def get_list_url(self, servicio_id=None):
        return reverse_lazy('plantillaservicio_list', kwargs={"servicio_id": servicio_id})

    def get_create_url(self, servicio_id=None):
        return reverse_lazy('plantillaservicio_create', kwargs={"servicio_id": servicio_id})

    class Meta:
        verbose_name = 'platilla para servicio'
        verbose_name_plural = "plantillas para servicio"
        unique_together = ['servicio', 'cargo', 'escala_salarial']


class PorCientoCIES:
    PORCIENTO_0 = '1'
    PORCIENTO_30 = '2'
    PORCIENTO_50 = '3'
    choices = ((PORCIENTO_0, '0%'), (PORCIENTO_30, '30%'), (PORCIENTO_50, '50%'))


class TrabajadorServicio(BaseUrls, models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.DO_NOTHING)
    cargo = models.ForeignKey(Cargo, on_delete=models.DO_NOTHING)
    servicio = models.ForeignKey(Obra, on_delete=models.CASCADE)
    ord_plant = models.PositiveIntegerField('orden en la plantilla', default=0)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    por_cies = models.CharField(
        'por ciento CIES', max_length=1, choices=PorCientoCIES.choices, default=PorCientoCIES.PORCIENTO_0)

    def __str__(self):
        return self.trabajador.nombre_completo + " " + self.servicio.nombre

    class Meta:
        verbose_name = 'trabajador del servicio'
        verbose_name_plural = 'trabajadores del servicio'


class Objeto(BaseUrls, models.Model):
    codigo = models.CharField('código', max_length=2)
    nombre = models.CharField(max_length=60)
    obra = models.ForeignKey(Obra, on_delete=models.PROTECT, default='', verbose_name="servicio")

    def __str__(self):
        return ' {} - {} '.format(self.codigo, self.nombre)


class Plano(BaseUrls, models.Model):
    num = models.CharField('número', max_length=5)
    objeto = models.ForeignKey(Objeto, on_delete=models.PROTECT, default='')

    nombre = models.CharField(max_length=210)
    formato = models.ForeignKey(Formato, on_delete=models.PROTECT, default='')
    obra = models.ForeignKey(Obra, on_delete=models.PROTECT, default='', verbose_name="servicio")
    cant = models.PositiveIntegerField('cantidad', default=1)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.PROTECT, default='')
    fecha_vpc = models.DateField('fecha VPC', editable=False, null=True, blank=True)
    VPC_OPT = (('No', 'No'), ('Si', 'Si'))
    vpc = models.CharField('VPC', max_length=2, default='No', editable=False, choices=VPC_OPT)
    trabajador = models.ForeignKey(Trabajador, on_delete=models.PROTECT, default='', related_name="planos")
    fecha_ini = models.DateField('fecha de inicio')
    fecha_fin = models.DateField('fecha de fin')
    actividad = models.ForeignKey(Actividad, on_delete=models.PROTECT, default='')
    tarifa = models.DecimalField(max_digits=8, decimal_places=6, editable=False, default=0.00)
    horas_creadas = models.DecimalField(max_digits=5, decimal_places=2, editable=False, default=0.00)
    valor = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    ESTADO_OPT = (('SR', 'SR'), ('V', 'V'), ('GE', 'GE'), ('VPC', 'VPC'))
    estado = models.CharField('estado del plano', max_length=3, editable=False, default='SR', choices=ESTADO_OPT)
    fecha_pago = models.DateField('fecha de pago', null=True, blank=True, editable=False)
    valor_retenido = models.DecimalField(max_digits=6, decimal_places=2, editable=False, default=0.00)
    valor_total = models.DecimalField(max_digits=6, decimal_places=2, editable=False, default=0.00)
    PORCIENTO_OPT = (('1.0', '100%'), ('0.7', '70%'), ('0.3', '30%'))
    porciento = models.CharField('por ciento de detalle', choices=PORCIENTO_OPT, default='', max_length=3)
    last_rev = models.IntegerField('última revision', editable=False, null=True, blank=True)
    orden_servicio = models.CharField(max_length=100, editable=False, blank=True, null=True)
    corte = models.CharField(max_length=22, blank=True, null=True, default='')
    horas_creadas_real = models.DecimalField(max_digits=5, decimal_places=2, editable=False, default=0.00)
    valor_real = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    valor_retenido_real = models.DecimalField(max_digits=6, decimal_places=2, editable=False, default=0.00)
    valor_total_real = models.DecimalField(max_digits=6, decimal_places=2, editable=False, default=0.00)
    os_vpc = models.CharField(max_length=7, blank=True, null=True, editable=False, default='')
    rev_vpc = models.IntegerField(editable=False, blank=True, null=True)
    rev_pago = models.IntegerField(editable=False, blank=True, null=True)
    DOC_OPT = (('PL', 'PL'), ('MD', 'MD'), ('LC', 'LC'), ('PR', 'PR'))
    tipo_doc = models.CharField('tipo de documento', max_length=2, blank=False, default='PL', editable=True,
                                choices=DOC_OPT)
    ETAPA_OPT = (('IB', 'IB'), ('ID', 'ID'), ('PTE D', 'PTE Decoración'))
    etapa = models.CharField(max_length=15, default='IB', editable=True, choices=ETAPA_OPT)
    incumplimiento_plano = models.IntegerField('incumplimiento en plano', editable=True, default=0)
    incumplimiento_cpl = models.IntegerField('incumplimiento en CPL', editable=True, default=0)
    incumplimiento_calidad = models.IntegerField('incumplimiento en calidad', editable=True, default=0)
    incumplimiento_plano_valor = models.DecimalField('valor de incumplimiento en plano', max_digits=6, decimal_places=2,
                                                     editable=False, default=0.00)
    incumplimiento_cpl_valor = models.DecimalField('valor de incumplimiento en CPL', max_digits=6, decimal_places=2,
                                                   editable=False, default=0.00)
    incumplimiento_calidad_valor = models.DecimalField('valor de incumplimiento en calidad', max_digits=6,
                                                       decimal_places=2, editable=False, default=0.00)
    valor_pen = models.DecimalField('valor de penalización', max_digits=6, decimal_places=2, default=0.00)
    history = auditlog_models.AuditlogHistoryField()


class Catalogo(BaseUrls, models.Model):
    plano = models.ForeignKey(Plano, on_delete=models.CASCADE, default=0)
    cant = models.PositiveIntegerField('cantidad', default=1)
    formato = models.ForeignKey(Formato, on_delete=models.PROTECT, default='')
    PORCIENTO_OPT = (('1.0', '100%'), ('0.7', '70%'), ('0.3', '30%'))
    porciento = models.CharField('por ciento de detalle', choices=PORCIENTO_OPT, default='', max_length=3)
    horas_creadas = models.DecimalField(max_digits=5, decimal_places=2, editable=False, default=0.00)
    horas_creadas_real = models.DecimalField(max_digits=5, decimal_places=2, editable=False, default=0.00)
    valor_retenido = models.DecimalField(max_digits=6, decimal_places=2, editable=False, default=0.00)
    valor_retenido_real = models.DecimalField(max_digits=6, decimal_places=2, editable=False, default=0.00)
    valor = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    valor_real = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    valor_total = models.DecimalField(max_digits=6, decimal_places=2, editable=False, default=0.00)
    valor_total_real = models.DecimalField(max_digits=6, decimal_places=2, editable=False, default=0.00)
    incumplimiento_plano_valor = models.DecimalField('valor de incumplimiento en plano', max_digits=6, decimal_places=2,
                                                     editable=False, default=0.00)
    incumplimiento_cpl_valor = models.DecimalField('valor de incumplimiento en CPL', max_digits=6, decimal_places=2,
                                                   editable=False, default=0.00)
    incumplimiento_calidad_valor = models.DecimalField('valor de incumplimiento en calidad', max_digits=6,
                                                       decimal_places=2, editable=False, default=0.00)
    valor_pen = models.DecimalField('valor de penalización', max_digits=6, decimal_places=2, default=0.00)
    history = auditlog_models.AuditlogHistoryField()


class Revision(BaseUrls, models.Model):
    plano = models.ForeignKey(Plano, on_delete=models.CASCADE, default=0)
    no_rev = models.IntegerField('número de revisión', editable=False)
    fecha_revision = models.DateField('fecha de revisión')
    entregado = models.CharField(max_length=30, blank=True, null=True)
    observaciones = models.CharField(max_length=100, blank=True, null=True)
    fecha_estado = models.DateField()
    fecha_vpc = models.DateField('fecha VPC', blank=True, null=True)
    ESTADO_OPT = (('GE', 'GE'), ('V', 'V'), ('VPC', 'VPC'))
    estado = models.CharField(max_length=3, choices=ESTADO_OPT, default='GE')
    history = auditlog_models.AuditlogHistoryField()


class Etapas:
    nombre = ''
    objetos = []
    cant = ''
    total_planos_plan = ''
    total_planos_real = ''
    total_planos_vpc_90 = ''
    total_planos_vpc_100 = ''
    total_planos_vpc_ret = ''
    total_planos_vpc_ret_ant = ''

    def __init__(self, nombre, objetos, cant, total_planos_plan, total_planos_real, total_planos_vpc_90,
                 total_planos_vpc_100, total_planos_vpc_ret, total_planos_vpc_ret_ant):
        self.nombre = nombre
        self.objetos = objetos
        self.cant = cant
        self.total_planos_plan = total_planos_plan
        self.total_planos_real = total_planos_real
        self.total_planos_vpc_90 = total_planos_vpc_90
        self.total_planos_vpc_100 = total_planos_vpc_100
        self.total_planos_vpc_ret = total_planos_vpc_ret
        self.total_planos_vpc_ret_ant = total_planos_vpc_ret_ant


class Objetos:
    codigo = ''
    nombre = ''
    etapa = ''
    total_planos_plan = ''
    total_planos_real = ''
    total_planos_vpc_90 = ''
    total_planos_vpc_100 = ''
    total_planos_vpc_ret = ''
    total_planos_vpc_ret_ant = ''

    def __init__(self, codigo, nombre, etapa, total_planos_plan, total_planos_real, total_planos_vpc_90,
                 total_planos_vpc_100, total_planos_vpc_ret, total_planos_vpc_ret_ant):
        self.codigo = codigo
        self.nombre = nombre
        self.etapa = etapa
        self.total_planos_plan = total_planos_plan
        self.total_planos_real = total_planos_real
        self.total_planos_vpc_90 = total_planos_vpc_90
        self.total_planos_vpc_100 = total_planos_vpc_100
        self.total_planos_vpc_ret = total_planos_vpc_ret
        self.total_planos_vpc_ret_ant = total_planos_vpc_ret_ant


class Esp:
    nombre = ''
    personas = []
    cant = ''

    def __init__(self, nombre, personas, cant):
        self.nombre = nombre
        self.personas = personas
        self.cant = cant


class Persona:
    no = ''
    nombre = ''
    cargo = ''
    ge = ''
    sal_max = ''
    tarifa = ''
    planos = []
    total_horas = ''
    total_valor = ''
    total_retenido = ''
    total_pagar = ''
    cant = ''
    especialidad = ''
    retenido_ant = ''
    pagar = ''

    def __init__(self, no, nombre, cargo, ge, sal_max, tarifa, planos, total_horas, total_valor, total_retenido,
                 total_pagar, cant, especialidad, retenido_ant, pagar):
        self.no = no
        self.nombre = nombre
        self.cargo = cargo
        self.ge = ge
        self.sal_max = sal_max
        self.tarifa = tarifa
        self.planos = planos
        self.total_horas = total_horas
        self.total_valor = total_valor
        self.total_retenido = total_retenido
        self.total_pagar = total_pagar
        self.cant = cant
        self.especialidad = especialidad
        self.retenido_ant = retenido_ant
        self.pagar = pagar


class Cat:
    formato = ''
    porciento = ''
    horas_creadas = 0
    horas_creadas_real = 0
    valor_retenido = 0
    valor_retenido_real = 0
    valor = 0
    valor_real = 0
    valor_total = 0
    valor_total_real = 0
    incumplimiento_plano = 0
    incumplimiento_cpl = 0
    incumplimiento_calidad = 0
    incumplimiento_plano_valor = 0.00
    incumplimiento_cpl_valor = 0.00
    incumplimiento_calidad_valor = 0.00
    valor_pen = 0.00

    def __init__(self, formato, porciento, horas_creadas, horas_creadas_real, valor_retenido,
                 valor_retenido_real, valor, valor_real, valor_total, valor_total_real,
                 incumplimiento_plano=None, incumplimiento_cpl=None, incumplimiento_calidad=None,
                 incumplimiento_plano_valor=None, incumplimiento_cpl_valor=None, incumplimiento_calidad_valor=None,
                 valor_pen=None):
        self.formato = formato
        self.porciento = porciento
        self.horas_creadas = horas_creadas
        self.horas_creadas_real = horas_creadas_real
        self.valor_retenido = valor_retenido
        self.valor_retenido_real = valor_retenido_real
        self.valor = valor
        self.valor_real = valor_real
        self.valor_total = valor_total
        self.valor_total_real = valor_total_real
        self.incumplimiento_plano = incumplimiento_plano
        self.incumplimiento_cpl = incumplimiento_cpl
        self.incumplimiento_calidad = incumplimiento_calidad
        self.incumplimiento_plano_valor = incumplimiento_plano_valor
        self.incumplimiento_cpl_valor = incumplimiento_cpl_valor
        self.incumplimiento_calidad_valor = incumplimiento_calidad_valor
        self.valor_pen = valor_pen


class Plan:
    nombre = ''
    codigo = ''
    objeto = ''
    obra = ''
    etapa = ''
    formato = ''
    porciento = ''
    horas_creadas = ''
    valor = ''
    valor_total = ''
    retenido = ''
    rev = ''
    vpc = ''
    trabajador_id = ''
    ult_rev = ''
    especialidad = ''
    caso = ''
    pagar = ''
    reten_ant = ''
    cant = 1
    nombre_obj = ''
    corte = ''
    horas_creadas_real = 0
    valor_real = 0
    valor_retenido_real = 0
    valor_total_real = 0
    list_cant = []
    tarifa = 0
    sigla = ''
    tipo_doc = ''
    incumplimiento_plano = 0
    incumplimiento_cpl = 0
    incumplimiento_calidad = 0
    incumplimiento_plano_valor = 0.00
    incumplimiento_cpl_valor = 0.00
    incumplimiento_calidad_valor = 0.00
    valor_pen = 0.00
    catalogo = []

    def __init__(self, nombre, codigo, objeto, etapa, formato, porciento, horas_creadas, valor, valor_total,
                 retenido, rev, vpc, trabajador_id, ult_rev, especialidad, caso, pagar, reten_ant, cant, nombre_obj,
                 corte, horas_creadas_real, valor_real, valor_retenido_real, valor_total_real, list_cant, tarifa,
                 sigla, tipo_doc=None, incumplimiento_plano=None, incumplimiento_cpl=None, incumplimiento_calidad=None,
                 incumplimiento_plano_valor=None, incumplimiento_cpl_valor=None, incumplimiento_calidad_valor=None,
                 valor_pen=None, catalogo=None, obra=None):
        self.nombre = nombre
        self.codigo = codigo
        self.objeto = objeto
        self.etapa = etapa
        self.formato = formato
        self.porciento = porciento
        self.horas_creadas = horas_creadas
        self.valor = valor
        self.valor_total = valor_total
        self.retenido = retenido
        self.rev = rev
        self.vpc = vpc
        self.trabajador_id = trabajador_id
        self.ult_rev = ult_rev
        self.especialidad = especialidad
        self.caso = caso
        self.pagar = pagar
        self.reten_ant = reten_ant
        self.cant = cant
        self.nombre_obj = nombre_obj
        self.corte = corte
        self.horas_creadas_real = horas_creadas_real
        self.valor_real = valor_real
        self.valor_retenido_real = valor_retenido_real
        self.valor_total_real = valor_total_real
        self.list_cant = list_cant
        self.tarifa = tarifa
        self.sigla = sigla
        self.tipo_doc = tipo_doc
        self.incumplimiento_plano = incumplimiento_plano
        self.incumplimiento_cpl = incumplimiento_cpl
        self.incumplimiento_calidad = incumplimiento_calidad
        self.incumplimiento_plano_valor = incumplimiento_plano_valor
        self.incumplimiento_cpl_valor = incumplimiento_cpl_valor
        self.incumplimiento_calidad_valor = incumplimiento_calidad_valor
        self.valor_pen = valor_pen
        self.catalogo = catalogo
        self.obra = obra


class Corte:
    nombre = ''
    descripcion = ''
    especialidades = []
    total = 0
    pendiente = 0
    vpc_mes = 0

    def __init__(self, nombre, descripcion, especialidades, total, pendiente, vpc_mes):
        self.nombre = nombre
        self.descripcion = descripcion
        self.especialidades = especialidades
        self.total = total
        self.pendiente = pendiente
        self.vpc_mes = vpc_mes


class Penalizaciones:
    trabajador_id = 0
    trabajador = ''
    corte = ''
    inc_plano = 0
    inc_cpl = 0
    inc_calidad = 0

    def __init__(self, trabajador_id, trabajador, corte, inc_plano, inc_cpl, inc_calidad):
        self.trabajador_id = trabajador_id
        self.trabajador = trabajador
        self.corte = corte
        self.inc_plano = inc_plano
        self.inc_cpl = inc_cpl
        self.inc_calidad = inc_calidad


class Cortes_Penalizaciones:
    corte = ''

    def __init__(self, corte):
        self.corte = corte


class Especial:
    nombre_esp = ''
    sigla = ''
    planos_vpc = []
    total = 0
    vpc = 0
    pendiente = 0

    def __init__(self, nombre_esp, planos_vpc, total, vpc, pendiente, sigla):
        self.nombre_esp = nombre_esp
        self.planos_vpc = planos_vpc
        self.total = total
        self.vpc = vpc
        self.pendiente = pendiente
        self.sigla = sigla


class Area:
    nombre = ''
    codigo = ''
    personas = []
    cant = ''
    horas_creadas_total = ''
    setrt = ''
    inc_res_30 = ''
    cies = ''
    ant = ''
    maest = ''
    total_dev_30 = ''
    cant_planos = ''
    total_horas = ''
    sal_res15 = ''
    sal_res15_plano = ''
    ret = ''
    ret_ant = ''
    impacto = ''
    sal_total_dev = ''
    total_vac = 0
    total_otros = 0
    total_dif_sal = 0
    incumplimiento_plano_valor = 0.00
    incumplimiento_cpl_valor = 0.00
    incumplimiento_calidad_valor = 0.00
    valor_pen = 0.00

    def __init__(self, nombre, personas, cant, codigo, horas_creadas_total, setrt, inc_res_30, cies, ant, maest,
                 total_dev_30, cant_planos, total_horas, sal_res15, sal_res15_plano, ret, ret_ant, impacto,
                 sal_tot_dev, incumplimiento_plano_valor=None, incumplimiento_cpl_valor=None,
                 incumplimiento_calidad_valor=None,
                 valor_pen=None):
        self.nombre = nombre
        self.personas = personas
        self.cant = cant
        self.codigo = codigo
        self.horas_creadas_total = horas_creadas_total
        self.setrt = setrt
        self.inc_res_30 = inc_res_30
        self.cies = cies
        self.ant = ant
        self.maest = maest
        self.total_dev_30 = total_dev_30
        self.cant_planos = cant_planos
        self.total_horas = total_horas
        self.sal_res15 = sal_res15
        self.sal_res15_plano = sal_res15_plano
        self.ret = ret
        self.ret_ant = ret_ant
        self.impacto = impacto
        self.sal_total_dev = sal_tot_dev
        self.incumplimiento_plano_valor = incumplimiento_plano_valor
        self.incumplimiento_cpl_valor = incumplimiento_cpl_valor
        self.incumplimiento_calidad_valor = incumplimiento_calidad_valor
        self.valor_pen = valor_pen


class Trab:
    no_loop = ''
    no = ''
    trab_id = ''
    nombre = ''
    cargo = ''
    ge = ''
    sal_max = ''
    tarifa = ''
    planos = []
    obras = []
    total_horas = ''
    total_valor = ''
    total_retenido = ''
    total_pagar = ''
    cant = ''
    dpto = ''
    retenido_ant = ''
    pagar = ''
    ci = ''
    categoria = ''
    sal_escala = ''
    cies = ''
    incre_res = ''
    antig = ''
    maestria = ''
    tarifa_se = ''
    tarifa_pa = ''
    tarifa_cies = ''
    tarifa_maest = ''
    tarifa_ant = ''
    salario_total = ''
    se_real = ''
    pa_real = ''
    cies_real = ''
    maest_real = ''
    ant_real = ''
    total_dev = ''
    impacto = ''
    sal_dev_total = ''
    eval = 0
    tarifa_30 = 0
    dif_30_15 = 0
    vac = 0
    otros = 0
    dif_sal = 0
    incumplimiento_plano = 0
    incumplimiento_cpl = 0
    incumplimiento_calidad = 0
    incumplimiento_plano_valor = 0.00
    incumplimiento_cpl_valor = 0.00
    incumplimiento_calidad_valor = 0.00
    total_valor_pen = 0.00
    sal_res15 = 0.00

    def __init__(self, no, nombre, ge, sal_max, tarifa, planos, total_horas, total_valor, total_retenido,
                 total_pagar, cant, dpto, retenido_ant, pagar, trab_id, ci, categoria, sal_escala, cies, incre_res,
                 antig, maestria, tarifa_se, tarifa_pa, tarifa_cies, tarifa_maest, tarifa_ant, salario_total,
                 se_real, pa_real, cies_real, maest_real, ant_real, total_dev, impacto, sal_dev_total, cargo,
                 incumplimiento_plano=None, incumplimiento_cpl=None, incumplimiento_calidad=None,
                 incumplimiento_plano_valor=None, incumplimiento_cpl_valor=None,
                 incumplimiento_calidad_valor=None, total_valor_pen=None, obras=None, sal_res15=None, no_loop=None):
        self.no_loop = no_loop
        self.no = no
        self.nombre = nombre
        self.ge = ge
        self.sal_max = sal_max
        self.tarifa = tarifa
        self.planos = planos
        self.total_horas = total_horas
        self.total_valor = total_valor
        self.total_valor_pen = total_valor_pen
        self.total_retenido = total_retenido
        self.total_pagar = total_pagar
        self.cant = cant
        self.dpto = dpto
        self.retenido_ant = retenido_ant
        self.pagar = pagar
        self.trab_id = trab_id
        self.ci = ci
        self.categoria = categoria
        self.sal_escala = sal_escala
        self.cies = cies
        self.incre_res = incre_res
        self.antig = antig
        self.maestria = maestria
        self.tarifa_se = tarifa_se
        self.tarifa_pa = tarifa_pa
        self.tarifa_ant = tarifa_ant
        self.tarifa_cies = tarifa_cies
        self.tarifa_maest = tarifa_maest
        self.salario_total = salario_total
        self.se_real = se_real
        self.pa_real = pa_real
        self.cies_real = cies_real
        self.ant_real = ant_real
        self.maest_real = maest_real
        self.total_dev = total_dev
        self.impacto = impacto
        self.sal_dev_total = sal_dev_total
        self.cargo = cargo
        self.incumplimiento_plano = incumplimiento_plano
        self.incumplimiento_cpl = incumplimiento_cpl
        self.incumplimiento_calidad = incumplimiento_calidad
        self.incumplimiento_plano_valor = incumplimiento_plano_valor
        self.incumplimiento_cpl_valor = incumplimiento_cpl_valor
        self.incumplimiento_calidad_valor = incumplimiento_calidad_valor
        self.total_valor_pen = total_valor_pen
        self.sal_res15 = sal_res15
        self.obras = obras


class Obr:
    id_obra = 0
    obra = ''
    planos = []
    valor_total = ''
    horas_creadas = ''
    no = ''
    strt = ''
    inc_r30 = ''
    cies = ''
    ant = ''
    maest = ''
    devengado = ''
    impacto = ''
    total = ''
    sal_res15 = ''
    retenido = ''
    retenido_ant = ''

    def __init__(self, id_obra, obra, planos, horas_creadas, no, strt, inc_r30, cies, ant,
                 maest, devengado, impacto, total, sal_res15, retenido, retenido_ant, valor_total):
        self.id_obra = id_obra
        self.obra = obra
        self.planos = planos
        self.horas_creadas = horas_creadas
        self.no = no
        self.strt = strt
        self.inc_r30 = inc_r30
        self.cies = cies
        self.ant = ant
        self.maest = maest
        self.devengado = devengado
        self.impacto = impacto
        self.total = total
        self.sal_res15 = sal_res15
        self.retenido = retenido
        self.retenido_ant = retenido_ant
        self.valor_total = valor_total


registry.auditlog.register(Plano)
registry.auditlog.register(Revision)
registry.auditlog.register(Catalogo)
