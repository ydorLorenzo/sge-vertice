from django.db import models


# Create your models here.
class SeccionSindical(models.Model):
    nombre = models.CharField(max_length=35, unique=True)

    def __str__(self):
        return self.nombre


class UnidadOrg(models.Model):
    nombre = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.nombre


class Departamento(models.Model):
    codigo = models.CharField(max_length=5, unique=True)
    nombre = models.CharField(max_length=60)
    unidad = models.ForeignKey(UnidadOrg, on_delete=models.DO_NOTHING, default='')
    seccion = models.ForeignKey(SeccionSindical, on_delete=models.DO_NOTHING, default='')
    dirige = models.ForeignKey('self', null=True, blank=True, related_name='Departamento', on_delete=models.DO_NOTHING)

    def __str__(self):
        return '{} {}'.format(self.codigo, self.nombre)


class EscalaSalarial(models.Model):
    grupo = models.CharField(max_length=8, unique=True)
    coeficientes = models.DecimalField(max_digits=3, decimal_places=2)
    salario_escala = models.DecimalField(max_digits=5, decimal_places=2)
    tarifa_horaria = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return self.grupo


class Cargo(models.Model):
    codigo = models.PositiveIntegerField(unique=True)
    nombre = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.nombre


class CIES(models.Model):
    escala = models.ForeignKey(EscalaSalarial, on_delete=models.CASCADE)
    tecnico = models.BooleanField()
    pago_adicional = models.BooleanField()
    porciento_30 = models.BooleanField()
    cies = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return 'Escala: {}, CIES {}'.format(self.escala, self.cies)


class Antiguedad(models.Model):
    escala = models.ForeignKey(EscalaSalarial, on_delete=models.CASCADE)
    tecnico = models.BooleanField()
    pago_adicional = models.BooleanField()
    porciento_5 = models.BooleanField()
    valor = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return 'Escala: {}, Valor {}'.format(self.escala, self.valor)


class Calificacion(models.Model):
    codigo = models.CharField(max_length=2, unique=True)
    nombre = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return '{}  {}'.format(self.codigo, self.nombre)


class Especialidad(models.Model):
    calificacion = models.ForeignKey(Calificacion, on_delete=models.CASCADE, default='')
    codigo = models.CharField(max_length=8, unique=True)
    nombre = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.nombre
