from django import forms

from .models import Evento


class EventoCreateForm(forms.ModelForm):

    class Meta:
        model = Evento
        fields = ('nombre', 'comentario', 'fecha_inicio', 'fecha_fin', 'todo_dia', 'tipo_evento')
