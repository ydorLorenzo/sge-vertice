from django.db import models
from ges_trab.models import Trabajador
from entrada_datos.models import Inversionista,Actividad


# Create your models here.
class Cliente (models.Model):
    nombre = models.CharField(max_length=30, verbose_name='Cliente')
    cargo =  models.CharField(max_length=10, verbose_name='Cargo')
    empresainversionista= models.ForeignKey(Inversionista, on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return self.nombre

class Facturas(models.Model):
    tipo= models.CharField(max_length=3, verbose_name='Moneda')
    numero= models.CharField(max_length=6, verbose_name='Número de factura')
    nombre= models.CharField(max_length=200, verbose_name='Número de factura')
    fecha_conf= models.DateField(verbose_name="Fecha de confección")
    entregado = models.ForeignKey(Trabajador, on_delete=models.DO_NOTHING)
    cliente = models.ForeignKey(Cliente, on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return self.numero

class Servicios (models.Model):
    descripcion= models.TextField(max_length=3, verbose_name='Moneda')
    importe= models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Importe', default=0.00)
    factura= models.ForeignKey(Facturas, on_delete=models.DO_NOTHING)
    actividad= models.ForeignKey(Actividad, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.descripcion

