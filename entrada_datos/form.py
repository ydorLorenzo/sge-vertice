from django import forms
from django_select2.forms import Select2Widget

from .models import *
from adm.models import UnidadOrg


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ['descripcion_act', 'orden_trab', 'codigo_act', 'numero', 'valor_act', 'prod_tecleada']
        widgets = {
            'orden_trab': Select2Widget,
            'tipo_act': Select2Widget
        }

    def __init__(self, *args, **kwargs):
        super(ActividadForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class InversionistaForm(forms.ModelForm):
    class Meta:
        model = Inversionista
        fields = ['codigo_inv', 'nombre_inv', 'direccion_inv', 'municipio_sucursal_inv', 'sucursal_mn_inv',
                  'sucursal_usd_inv', 'cuenta_mn_inv', 'cuenta_usd_inv', 'nit']


    def __init__(self, *args, **kwargs):
        super(InversionistaForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class OTForm(forms.ModelForm):
    class Meta:
        model = OT
        fields = '__all__'
        widgets = {
            'inversionista': Select2Widget,
            'tipo_servicio': Select2Widget,
            'area': Select2Widget,
            'unidad': Select2Widget
        }

    def __init__(self, *args, **kwargs):
        super(OTForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class TipoActividadForm(forms.ModelForm):
    class Meta:
        model = TipoActividad
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TipoActividadForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class AreaForm(forms.ModelForm):
    unidad = forms.ModelChoiceField(UnidadOrg.objects, label=u'Unidad Organizacional:', widget=Select2Widget)
    class Meta:
        model = Area
        fields = '__all__'
        widgets = {'area': Select2Widget}

    def __init__(self, *args, **kwargs):
        super(AreaForm, self).__init__(*args, **kwargs)
        self.fields['area'].queryset = Departamento.objects.filter(dirige_id__isnull=True)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['codigo', 'nombre']

    def __init__(self, *args, **kwargs):
        super(ServicioForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class SuplementoForm(forms.ModelForm):
    class Meta:
        model = Suplemento
        fields = ['monto', 'fecha', 'solicitud']

    def __init__(self, *args, **kwargs):
        super(SuplementoForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})
