from django import forms

from .models import *


class AusenciaForm(forms.ModelForm):
    class Meta:
        model = Ausencia
        fields = ['codigo_trab', 'fecha', 'horas', 'causal']

    def __init__(self, *args, **kwargs):
        super(AusenciaForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class TarjetaCNCForm(forms.ModelForm):
    class Meta:
        model = TarjetaCNC
        fields = ['codigo_trab', 'mes', 'anno', 'cant_dias', 'salario']

    def __init__(self, *args, **kwargs):
        super(TarjetaCNCForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})
