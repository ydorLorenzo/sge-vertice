from django import forms
from .models import *


class PlantillaForm(forms.ModelForm):
    class Meta:
        model = Plantilla
        fields = ['unidad', 'departamento', 'cargo', 'cant_plazas']

    def __init__(self, *args, **kwargs):
        super(PlantillaForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})
