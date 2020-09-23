from django.db import models
from django.urls import reverse_lazy


class BaseNameModel(models.Model):
    nombre = models.CharField(max_length=60)

    def __str__(self):
        return self.nombre

    class Meta:
        abstract = True


class BaseNameUniqueModel(models.Model):
    nombre = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        abstract = True


class BaseNameCodeModel(BaseNameModel):
    codigo = models.CharField(max_length=8, unique=True, verbose_name='código')

    class Meta:
        abstract = True


class BaseUrls(models.Model):
    def get_detail_url(self):
        return reverse_lazy(self._meta.model_name + '_detail', kwargs={"pk": self.id})

    def get_update_url(self):
        return reverse_lazy(self._meta.model_name + '_update', kwargs={"pk": self.id})

    def get_delete_url(self):
        return reverse_lazy(self._meta.model_name + '_delete', kwargs={"pk": self.id})

    def get_list_url(self):
        return reverse_lazy(self._meta.model_name + '_list')

    def get_create_url(self):
        return reverse_lazy(self._meta.model_name + '_create')

    def get_absolute_url(self):
        return reverse_lazy(self._meta.model_name + '_list')

    class Meta:
        abstract = True

