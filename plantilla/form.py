from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django_select2.forms import ModelSelect2Widget

from .models import Plantilla
from adm.models import UnidadOrg, Departamento, Cargo
from prenomina15.models import PlantillaServicio


class PlantillaForm(forms.ModelForm):
    unidad = forms.ModelChoiceField(
        label=u'Unidad organizacional',
        queryset=UnidadOrg.objects.all(),
        widget=ModelSelect2Widget(
            model=UnidadOrg,
            search_fields=['nombre__icontains']
        )
    )
    departamento = forms.ModelChoiceField(
        label=u'Departamento',
        queryset=Departamento.objects.all(),
        widget=ModelSelect2Widget(
            model=Departamento,
            search_fields=['nombre__icontains'],
            dependent_fields={'unidad': 'unidad'}
        )
    )

    class Meta:
        model = Plantilla
        fields = ['cargo', 'cant_plazas', 'escala_salarial']
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': 'Los campos %(field_labels)s de %(model_name)s no son únicos.'
            }
        }


class PlantillaServicioForm(forms.ModelForm):
    cargo = forms.ModelChoiceField(
        label=u'Cargo',
        queryset=Cargo.objects.all(),
        widget=ModelSelect2Widget(
            model=Cargo,
            search_fields=['nombre__icontains']
        )
    )

    class Meta:
        model = PlantillaServicio
        fields = ['servicio', 'cargo', 'especialidad', 'escala_salarial', 'cant_plazas']
