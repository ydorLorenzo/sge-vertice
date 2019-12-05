from django import forms
from .models import *


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ['descripcion_act', 'orden_trab', 'codigo_act', 'numero', 'valor_act', 'prod_tecleada']

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
        fields = ['descripcion_ot', 'no_contrato', 'inversionista', 'unidad', 'codigo_ot']

    def __init__(self, *args, **kwargs):
        super(OTForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class TipoActividadForm(forms.ModelForm):
    class Meta:
        model = TipoActividad
        fields = ['nombre_tipo_act', 'valor']

    def __init__(self, *args, **kwargs):
        super(TipoActividadForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['codigo', 'nombre']

    def __init__(self, *args, **kwargs):
        super(AreaForm, self).__init__(*args, **kwargs)
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
