from django import forms
from .models import CoeficientePromedioSalario, Datos
from entrada_datos.models import Actividad


class CoeficientePromedioSalarioForm(forms.ModelForm):
    class Meta:
        model = CoeficientePromedioSalario
        fields = ['coeficiente']

    def __init__(self, *args, **kwargs):
        super(CoeficientePromedioSalarioForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class DatosForm(forms.ModelForm):
    class Meta:
        model = Datos
        fields = ['orden_trab', 'actividad', 'trabajador', 'cant_horas', 'horas_ext']

    def __init__(self, *args, **kwargs):
        super(DatosForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class AjusteForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ['prod_tecleada']

    def __init__(self, *args, **kwargs):
        super(AjusteForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})
