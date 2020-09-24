from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django_select2.forms import ModelSelect2Widget

from .models import Plantilla
from adm.models import UnidadOrg, Cargo
from prenomina15.models import PlantillaServicio


class PlantillaForm(forms.ModelForm):
    unidad = forms.ChoiceField(choices=UnidadOrg.objects.values_list('id', 'nombre'))

    class Meta:
        model = Plantilla
        fields = ('cargo', 'cant_plazas', 'escala_salarial', 'departamento')
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
