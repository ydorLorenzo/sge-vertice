from django import forms

from .models import *


class TrabajadorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TrabajadorForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['sal_plus'].widget.attrs['min'] = 0.0
        self.fields['sal_cond_anor'].widget.attrs['min'] = 0.0
        self.fields['salario_escala'].widget.attrs['min'] = 0.0

    def clean_sal_plus(self):
        sal_plus = self.cleaned_data['sal_plus']
        if sal_plus < 0.0:
            raise forms.ValidationError("El salario plus no puede ser menor que 0")
        return sal_plus

    def clean_sal_cond_anor(self):
        sal_cond_anor = self.cleaned_data['sal_cond_anor']
        if sal_cond_anor < 0.0:
            raise forms.ValidationError("El salario condicional anor. no puede ser menor que 0")
        return sal_cond_anor

    def clean_salario_escala(self):
        salario_escala = self.cleaned_data['salario_escala']
        if salario_escala < 0.0:
            raise forms.ValidationError("El salario escala no puede ser menor que 0")
        return salario_escala

    class Meta:
        model = Trabajador
        fields = '__all__'


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
