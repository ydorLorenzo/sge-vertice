from django.db import models


# Create your models here.





class Inversionista(models.Model):
    codigo_inv = models.CharField(max_length=12, blank=False, null=False, unique=True)
    nombre_inv = models.CharField(max_length=60, blank=False, null=False)
    direccion_inv = models.CharField(max_length=160, blank=False, null=False)
    municipio_sucursal_inv = models.CharField(max_length=20, blank=False, null=False)
    sucursal_mn_inv = models.CharField(max_length=60, blank=False, null=False)
    cuenta_mn_inv = models.CharField(max_length=16, blank=False, null=False, unique=True)
    sucursal_usd_inv = models.CharField(max_length=16, blank=False, null=False)
    cuenta_usd_inv = models.CharField(max_length=16, blank=False, null=False, unique=True)
    nit = models.CharField(max_length=11, blank=False, null=False, unique=True)

    def __str__(self):
        return '{} {}'.format(self.codigo_inv, self.nombre_inv)


class Area (models.Model):
    codigo = models.PositiveIntegerField(null=False, blank=False)
    nombre = models.CharField(max_length=20, null=False, unique=True, blank=False)


class Servicio (models.Model):
    codigo = models.CharField(null=False, blank=False, unique=True, max_length=2)
    nombre = models.CharField(max_length=20, null=False, unique=True, blank=False)


class OT(models.Model):
    codigo_ot = models.CharField(max_length=10, unique=True)
    descripcion_ot = models.CharField(max_length=100, null=False, blank=False)
    no_contrato = models.CharField(max_length=5, null=False, blank=False, unique=True)
    valor_contrato = models.DecimalField(max_digits=9, decimal_places=2, editable=False, default=0.00)
    tipo_servicio = models. ForeignKey(Servicio, on_delete=models.DO_NOTHING, default='')
    area = models.ForeignKey(Area, on_delete=models.DO_NOTHING, default='')
    inversionista = models.ForeignKey(Inversionista, on_delete=models.DO_NOTHING, default='')
    OPT_Unidad = (('03', 'USTI'), ('07', 'UGDD'))
    unidad = models.CharField(max_length=4, choices=OPT_Unidad, default='', null=False, blank=False)

    def __str__(self):
        return '{} {}'.format(self.codigo_ot, self.descripcion_ot)


class TipoActividad(models.Model):
    nombre_tipo_act = models.CharField(max_length=60, blank=False, null=False, unique=True)
    valor = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return '{}'.format(self.nombre_tipo_act)


class Actividad(models.Model):
    tipo_act = models.ForeignKey(TipoActividad, on_delete=models.DO_NOTHING, default='', null=False, blank=False)
    codigo_act = models.PositiveIntegerField(null=False, blank=False)
    descripcion_act = models.CharField(max_length=100, null=False, blank=True)
    valor_prod_act = models.DecimalField(max_digits=9, decimal_places=2, editable=False, default=0.00)
    activa = models.BooleanField(editable=False, default=True)
    orden_trab = models.ForeignKey(OT, on_delete=models.DO_NOTHING, default='', null=False, blank=False)
    numero = models.PositiveIntegerField(null=False, blank=False, verbose_name='N&uacute;mero', default=1)
    valor_act = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    prod_tecleada = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    venta = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return '{} {}'.format(self.codigo_act, self.descripcion_act)


class UnidadFacturacion(models.Model):
    codigo_uf = models.CharField(max_length=12, blank=False, null=False)
    nombre_uf = models.CharField(max_length=60, blank=False, null=False)
    direccion_uf = models.CharField(max_length=160, blank=False, null=False)
    municipio_sucursal = models.CharField(max_length=10, blank=False, null=False)
    sucursal_mn = models.CharField(max_length=60, blank=False, null=False)
    cuenta_mn = models.CharField(max_length=16, blank=False, null=False)
    sucursal_usd = models.CharField(max_length=16, blank=False, null=False)
    cuenta_usd = models.CharField(max_length=16, blank=False, null=False)
    nit = models.CharField(max_length=11, blank=False, null=False)

    def __str__(self):
        return '{}'.format(self.nombre_uf)


class Suplemento (models.Model):
    orden_trab = models.ForeignKey(OT, on_delete=models.DO_NOTHING)
    monto = models.DecimalField(max_digits=7, decimal_places=2)
    fecha = models.DateField()
    usuario = models.CharField(max_length=100)
    solicitud = models.CharField(max_length=60)
