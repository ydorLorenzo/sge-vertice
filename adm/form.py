from django import forms
from django_select2.forms import Select2Widget

from .models import *


class UnidadOrgForm(forms.ModelForm):
    class Meta:
        model = UnidadOrg
        fields = ['nombre']

    def __init__(self, *args, **kwargs):
        super(UnidadOrgForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})


class SeccionSindicalForm(forms.ModelForm):
    class Meta:
        model = SeccionSindical
        fields = ['nombre']

    def __init__(self, *args, **kwargs):
        super(SeccionSindicalForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ['codigo', 'nombre', 'unidad', 'seccion', 'dirige']
        widgets = {
            'dirige': Select2Widget,
            'seccion': Select2Widget,
            'unidad': Select2Widget
        }

    def __init__(self, *args, **kwargs):
        super(DepartamentoForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['codigo', 'nombre']

    def __init__(self, *args, **kwargs):
        super(CargoForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['codigo', 'nombre']

    def __init__(self, *args, **kwargs):
        super(CalificacionForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean_codigo(self):
        codigo = self.cleaned_data['codigo']
        if not codigo.isdigit():
            raise forms.ValidationError('El nombre no puede contener números')
        return codigo


class EspecialidadForm(forms.ModelForm):
    class Meta:
        model = Especialidad
        fields = ['calificacion', 'codigo', 'nombre']
        widgets = {'calificacion': Select2Widget}

    def __init__(self, *args, **kwargs):
        super(EspecialidadForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean_codigo(self):
        codigo = self.cleaned_data['codigo']
        if not codigo.isdigit():
            raise forms.ValidationError('El nombre no puede contener números')
        return codigo
