import datetime

from django import forms
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django_select2.forms import Select2Widget, ModelSelect2Widget

from .models import *
from adm.models import UnidadOrg, Departamento, Calificacion
from rechum.utils import decorate_bound_field

decorate_bound_field()


class TrabajadorForm(forms.ModelForm):
#    unidad_org = forms.ModelChoiceField(
#        queryset=UnidadOrg.objects.all(),
#        label=u"Unidad organizacional",
#        widget=ModelSelect2Widget(
#            model=UnidadOrg,
#            search_fields=['nombre__icontains']
#        )
#    )
#    departamento = forms.ModelChoiceField(
#        queryset=Departamento.objects.all(),
#        label=u"Departamento",
#        widget=ModelSelect2Widget(
#            model=Departamento,
#            search_fields=['nombre__icontains'],
#            dependent_fields={'unidad': 'unidad_org'}
#        )
#    )
#    calificacion = forms.ModelChoiceField(
#        queryset=Calificacion.objects.all(),
#        label=u"Calificación",
#        widget=ModelSelect2Widget(
#            model=Calificacion,
#            search_fields=['nombre__icontains']
#        )
#    )
#    plantilla = forms.ModelChoiceField(
#        queryset=Plantilla.objects.all(),
#        label=u"Plantilla",
#        widget=ModelSelect2Widget(
#            model=Plantilla,
#            search_fields=['cargo__nombre__icontains'],
#            dependent_fields={'departamento': 'departamento'}
#        )
#    )

    def __init__(self, *args, **kwargs):
        super(TrabajadorForm, self).__init__(*args, **kwargs)
        for field in ['sal_plus', 'sal_cond_anor', 'peso', 'estatura', 'salario_escala']:
            self.fields[field].widget.attrs.update({'min': 0})
        for field in ['fecha_contrato']:
            self.fields[field].widget.attrs.update({'class': 'inline-date form-control'})

    class Meta:
        model = Trabajador
        fields = '__all__'
        widgets = {
            'escolaridad': Select2Widget,
            'especialidad': Select2Widget,
            'actividad': Select2Widget,
            'orga_defensa': Select2Widget
        }


class NucleoFamiliarForm(forms.ModelForm):
    class Meta:
        model = NucleoFamiliar
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(NucleoFamiliarForm, self).__init__(*args, **kwargs)
        self.fields['fecha_nac'].widget.attrs.update({
            'class': 'fecha-inline form-control'
        })

NucleoFamiliarFormSet = inlineformset_factory(
    Alta, NucleoFamiliar, form=NucleoFamiliarForm, extra=1, can_delete=True,
    fields=['parentesco', 'fecha_nac', 'enfermedades', 'salario_dev', 'vinc_lab']
)


def get_available_codes():
    num_list = [x[0] for x in list(Trabajador.objects.filter(
        Q(fecha_baja__isnull=True) | Q(fecha_baja__gte=datetime.datetime(datetime.datetime.today().year, 1, 1))
    ).values_list('codigo_interno'))]
    gum_set_distinct = []
    for x in range(0, 1000):
        tmp = format(x, '3').replace(' ', '0')
        if tmp not in num_list:
            gum_set_distinct.append((tmp, tmp))
    return gum_set_distinct


class TrabajadorAltaForm(forms.ModelForm):
    t_contrato = forms.ChoiceField(label='tipo de contrato', choices=(
        ('6', 'A prueba'),
        ('2', 'Indeterminado'),
        ('3', 'Determinado por tiempo definido'),
        ('7', 'Determinado por sustitución de trabajador'),
        ('4', 'Adiestramiento')
    ), initial='6')
#    unidad_org = forms.ModelChoiceField(
#        queryset=adm.UnidadOrg.objects.all(),
#        label=u"Unidad organizacional",
#        widget=ModelSelect2Widget(
#            model=adm.UnidadOrg,
#            search_fields=['nombre__icontains']
#        )
#    )
#    departamento = forms.ModelChoiceField(
#        queryset=adm.Departamento.objects.all(),
#        label=u"Unidad organizacional",
#        widget=ModelSelect2Widget(
#            model=adm.Departamento,
#            search_fields=['nombre__icontains'],
#            dependent_fields={'unidad': 'unidad_org'}
#        )
#    )
#    cargo = forms.ModelChoiceField(
#        queryset=adm.Cargo.objects.all(),
#        label=u"Cargo",
#        widget=ModelSelect2Widget(
#            model=adm.Cargo,
#            search_fields=['nombre__icontains'],
#            dependent_fields={'departamento': 'plantilla__departamento'}
#        )
#    )
#    calificacion = forms.ModelChoiceField(
#        queryset=adm.Calificacion.objects.all(),
#        label=u"Calificación",
#        widget=ModelSelect2Widget(
#            model=adm.Calificacion,
#            search_fields=['nombre__icontains']
#        )
#    )
#    especialidad = forms.ModelChoiceField(
#        queryset=adm.Especialidad.objects.all(),
#        label=u"Especialidad",
#        widget=ModelSelect2Widget(
#            model=adm.Especialidad,
#            search_fields=['nombre__icontains'],
#            dependent_fields={'calificacion': 'calificacion'}
#        )
#    )
    codigo_interno = forms.ChoiceField(choices=get_available_codes())

    def __init__(self, *args, **kwargs):
        super(TrabajadorAltaForm, self).__init__(*args, **kwargs)
        for field in ['sal_plus', 'sal_cond_anor', 'peso', 'estatura']:
            self.fields[field].widget.attrs.update({'min': 0})

    class Meta:
        model = Alta
        fields = '__all__'
        widgets = {
            'escolaridad': Select2Widget,
            'actividad': Select2Widget,
            'orga_defensa': Select2Widget
        }


class TrabajadorAltaBajaForm(forms.ModelForm):
    unidad_org = forms.ModelChoiceField(
        queryset=adm.UnidadOrg.objects.all(),
        widget=ModelSelect2Widget(
            model=adm.UnidadOrg,
            search_fields=['nombre__icontains']
        )
    )
    departamento = forms.ModelChoiceField(
        queryset=adm.Departamento.objects.all(),
        widget=ModelSelect2Widget(
            model=adm.Departamento,
            search_fields=['nombre__icontains'],
            dependent_fields={'unidad': 'unidad_org'}
        )
    )
    cargo = forms.ModelChoiceField(
        queryset=adm.Cargo.objects.all(),
        widget=ModelSelect2Widget(
            model=adm.Cargo,
            search_fields=['nombre__icontains']
        )
    )

    class Meta:
        model = Trabajador
        fields = [
            'primer_nombre',
            'segundo_nombre',
            'apellidos',
            'fecha_contrato',
            'codigo_interno',
            'categoria',
            'org_plantilla',
            't_plantilla',
            't_contrato',
            'fuerza_i',
            't_pago',
            'escala_salarial',
            'cies',
            'antiguedad',
            'motivo_alta'
        ]



class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        exclude = ()
