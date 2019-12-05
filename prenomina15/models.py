from django.db import models
from adm.models import EscalaSalarial
from ges_trab.models import Trabajador
from entrada_datos.models import OT, Actividad
from django.contrib.auth.models import User


class SalarioMax(models.Model):
    grupo_esc = models.ForeignKey(EscalaSalarial, on_delete=models.CASCADE, null=False, blank=False, default='')
    sal = models.DecimalField(null=False, blank=False, max_digits=6, decimal_places=2)
    TIPO_OPT = (('OT', 'Obra Turismo'), ('VT', 'Vivienda para Turismo'))
    tipo = models.CharField(max_length=2, choices=TIPO_OPT, default='')

    def __str__(self):
        return ' {} - {} - {}'.format(self.tipo, self.grupo_esc, self.sal)


class Formato(models.Model):
    formato = models.CharField(max_length=6, null=False, blank=False)
    factor = models.DecimalField(max_digits=2, decimal_places=1, null=False, blank=False)

    def __str__(self):
        return '{}'.format(self.formato)


class Especialidad(models.Model):
    nombre = models.CharField(max_length=150, null=False, blank=False)
    factor = models.DecimalField(max_digits=2, decimal_places=1, null=False, blank=False)
    siglas = models.CharField(max_length=2, null=False, blank=False)
    md = models.IntegerField(editable=False, blank=True, null=True)
    lm = models.IntegerField(editable=False, blank=True, null=True)
    pr = models.IntegerField(editable=False, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Obra(models.Model):
    orden_trab = models.ForeignKey(OT, on_delete=models.PROTECT, default='')
    nombre = models.CharField(max_length=20, blank=False, null=False)
    TIPO_OPT = (('OT', 'Obra Turismo'), ('VT', 'Vivienda para Turismo'), ('R6', 'Resolucion 6'))
    tipo = models.CharField(max_length=2, choices=TIPO_OPT, default='')
    horas_a2 = models.PositiveIntegerField(null=False, blank=False)
    gesc = models.ForeignKey(EscalaSalarial, on_delete=models.PROTECT, null=False, blank=False, default='')
    usuarios = models.ManyToManyField(User)
    owner = models.CharField(max_length=20, editable=False, blank=False, null=False, default='admin')


    def __str__(self):
        return self.nombre


class Objeto(models.Model):
    codigo = models.CharField(max_length=2, blank=False, null=False)
    nombre = models.CharField(max_length=60, blank=False, null=False)
    obra = models.ForeignKey(Obra, on_delete=models.PROTECT, null=False, blank=False, default='')

    def __str__(self):
        return ' {} - {} '.format(self.codigo, self.nombre)


class Plano(models.Model):
    num = models.CharField(max_length=5, null=False, blank=False)
    objeto = models.ForeignKey(Objeto, on_delete=models.PROTECT, null=False, blank=False, default='')

    nombre = models.CharField(max_length=210, null=False, blank=False)
    formato = models.ForeignKey(Formato, on_delete=models.PROTECT, null=False, blank=False, default='')
    obra = models.ForeignKey(Obra, on_delete=models.PROTECT, null=False, blank=False, default='')
    cant = models.PositiveIntegerField(default=1, blank=False, null=False)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.PROTECT, null=False, blank=False, default='')
    fecha_vpc = models.DateField(editable=False, null=True, blank=True)
    VPC_OPT = (('No', 'No'), ('Si', 'Si'))
    vpc = models.CharField(max_length=2, default='No', editable=False, choices=VPC_OPT)
    trabajador = models.ForeignKey(Trabajador, on_delete=models.PROTECT, null=False, blank=False, default='',
                                   related_name='Trabajador_del_Plano')
    fecha_ini = models.DateField(null=False, blank=False)
    fecha_fin = models.DateField(null=False, blank=False)
    actividad = models.ForeignKey(Actividad, on_delete=models.PROTECT, default='')
    tarifa = models.DecimalField(max_digits=8, decimal_places=6, editable=False, null=False, blank=False, default=0.00)
    horas_creadas = models.DecimalField(max_digits=5, decimal_places=2, editable=False, default=0.00)
    valor = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    ESTADO_OPT = (('V', 'V'), ('GE', 'GE'), ('VPC', 'VPC'))
    estado = models.CharField(max_length=3, editable=False, default='', choices=ESTADO_OPT)
    fecha_pago = models.DateField(null=True, blank=True, editable=False)
    valor_retenido = models.DecimalField(max_digits=6, decimal_places=2, editable=False, default=0.00)
    valor_total = models.DecimalField(max_digits=6, decimal_places=2, editable=False, default=0.00)
    PORCIENTO_OPT = (('1.0', '100%'), ('0.7', '70%'), ('0.3', '30%'))
    porciento = models.CharField(choices=PORCIENTO_OPT, default='', max_length=3)
    last_rev = models.IntegerField(editable=False, null=True, blank=True)
    orden_servicio = models.CharField(max_length=100, editable=False, blank=True, null=True)
    corte = models.CharField(max_length=22, blank=True, null=True, default='')
    horas_creadas_real = models.DecimalField(max_digits=5, decimal_places=2, editable=False, default=0.00)
    valor_real = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    valor_retenido_real = models.DecimalField(max_digits=6, decimal_places=2, editable=False, default=0.00)
    valor_total_real = models.DecimalField(max_digits=6, decimal_places=2, editable=False, default=0.00)
    os_vpc = models.CharField(max_length=7, blank=True, null=True, editable=False, default='')
    rev_vpc = models.IntegerField(editable=False, blank=True, null=True)
    rev_pago = models.IntegerField(editable=False, blank=True, null=True)
    DOC_OPT = (('PL', 'PL'), ('MD', 'MD'), ('LM', 'LM'), ('PR', 'PR'))
    tipo_doc = models.CharField(max_length=2, blank=False, default='PL', editable=True, choices=DOC_OPT)


class Revision(models.Model):
    plano = models.ForeignKey(Plano, on_delete=models.CASCADE, default=0)
    no_rev = models.IntegerField(editable=False)
    fecha_revision = models.DateField()
    entregado = models.CharField(max_length=30, blank=True, null=True)
    observaciones = models.CharField(max_length=100, blank=True, null=True)
    fecha_estado = models.DateField(blank=False, null=False)
    fecha_vpc = models.DateField(blank=True, null=True)
    ESTADO_OPT = (('GE', 'GE'), ('V', 'V'), ('VPC', 'VPC'))
    estado = models.CharField(max_length=3, choices=ESTADO_OPT, default='GE', blank=False, null=False)


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


class Plan:
    nombre = ''
    codigo = ''
    objeto = ''
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

    def __init__(self, nombre, codigo, objeto, etapa, formato, porciento, horas_creadas, valor, valor_total,
                 retenido, rev, vpc, trabajador_id, ult_rev, especialidad, caso, pagar, reten_ant, cant, nombre_obj,
                 corte, horas_creadas_real, valor_real, valor_retenido_real, valor_total_real, list_cant, tarifa,
                 sigla):
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

    def __init__(self, nombre, personas, cant, codigo, horas_creadas_total, setrt, inc_res_30, cies, ant, maest,
                 total_dev_30, cant_planos, total_horas, sal_res15, sal_res15_plano, ret, ret_ant, impacto,
                 sal_tot_dev):
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


class Trab:
    no = ''
    trab_id = ''
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

    def __init__(self, no, nombre, ge, sal_max, tarifa, planos, total_horas, total_valor, total_retenido,
                 total_pagar, cant, dpto, retenido_ant, pagar, trab_id, ci, categoria, sal_escala, cies, incre_res,
                 antig, maestria, tarifa_se, tarifa_pa, tarifa_cies, tarifa_maest, tarifa_ant, salario_total,
                 se_real, pa_real, cies_real, maest_real, ant_real, total_dev, impacto, sal_dev_total, cargo):
        self.no = no
        self.nombre = nombre
        self.ge = ge
        self.sal_max = sal_max
        self.tarifa = tarifa
        self.planos = planos
        self.total_horas = total_horas
        self.total_valor = total_valor
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
