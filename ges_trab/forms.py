from django import forms
from .models import *


class TrabajadorForm(forms.ModelForm):
    class Meta:
        model = Trabajador
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TrabajadorForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class NucleoFamiliarForm(forms.ModelForm):
    class Meta:
        model = NucleoFamiliar
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(NucleoFamiliarForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['fecha_nac'].widget.attrs.update({
            'class': 'fecha-inline form-control'
        })


class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(MovimientoForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})
