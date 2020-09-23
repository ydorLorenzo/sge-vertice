from django import forms

from .models import Evento, TipoEvento


class EventoCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EventoCreateForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['fecha_inicio'].widget.attrs.update({'class': 'form-control inline-date'})
        self.fields['fecha_fin'].widget.attrs.update({'class': 'form-control inline-date'})

    class Meta:
        model = Evento
        fields = ('nombre', 'comentario', 'fecha_inicio', 'fecha_fin', 'todo_dia', 'tipo_evento')
