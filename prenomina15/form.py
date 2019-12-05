from django import forms
from .models import Obra, Plano, Objeto, Revision
from django.core.cache import cache



class ObraForm(forms.ModelForm):
    class Meta:
        model = Obra
        fields = ['orden_trab', 'tipo', 'horas_a2', 'gesc', 'nombre']

    def __init__(self, *args, **kwargs):
        super(ObraForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class ObjetoForm(forms.ModelForm):


    class Meta:
        model = Objeto
        fields = ['codigo', 'nombre', 'obra']

    def __init__(self, *args, **kwargs):
        super(ObjetoForm, self).__init__(*args, **kwargs)
        self.fields['codigo'].widget.attrs.update({'class': 'form-control'})
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['obra'].widget.attrs.update({'class': 'form-control'})




class PlanoForm(forms.ModelForm):
    class Meta:
        model = Plano
        fields = ['num', 'objeto', 'nombre', 'formato', 'obra', 'especialidad', 'trabajador', 'fecha_fin', 'cant',
                  'actividad', 'fecha_ini', 'porciento', 'corte', 'tipo_doc']

    def __init__(self, *args, **kwargs):
        super(PlanoForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class RevisionForm(forms.ModelForm):
    class Meta:
        model = Revision
        fields = ['fecha_revision', 'entregado', 'observaciones', 'fecha_estado', 'fecha_vpc', 'estado']

    def __init__(self, *args, **kwargs):
        super(RevisionForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})
