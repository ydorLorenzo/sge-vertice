from django import forms
from .models import *


class SubsidioForm(forms.ModelForm):
    class Meta:
        model = Subsidio
        fields = ['codigo_trab', 'desde', 'hasta', 'centro', 'medico', 'fecha', 'diagnostico', 'por_ciento', 'dias',
                  'tipo', 'ent_72', 'no_reg']

    def __init__(self, *args, **kwargs):
        super(SubsidioForm, self).__init__(*args, **kwargs)

        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})
