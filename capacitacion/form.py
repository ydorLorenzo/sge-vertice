from django import forms

from capacitacion.models import *


# Capacitacion forms
class AbstractForm(forms.ModelForm):
    class Meta:
        abstract = True

    def _widget_class_modifier(self):
        for field in iter(self.fields):
            field.widget.attrs.update({'class': 'form-control'})

class TipoActividadCapacitacionForm(AbstractForm):
    class Meta:
        model = TipoActividadCapacitacion
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TipoActividadCapacitacionForm, self).__init__(*args, **kwargs)
        self._widget_class_modifier()