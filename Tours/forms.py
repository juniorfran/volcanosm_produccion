from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Resena, Reserva
from bootstrap_datepicker_plus.widgets import DatePickerInput

class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ['comentario']
        widgets = {
            #'estrellas': forms.Select(choices=[(i, str(i)) for i in range(1, 6)], attrs={'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        exclude = ['fecha_reserva']

    widgets = {
        'fecha_reserva': DatePickerInput(
            format='%Y-%m-%d',
            options={
                "daysOfWeekDisabled": [0, 1, 2, 3, 4],  # Deshabilitar días de la semana excepto sábado y domingo
            }
        ),
    }

    def clean_fecha_reserva(self):
        fecha_reserva = self.cleaned_data.get('fecha_reserva')
        # Asegurarse de que la fecha de reserva sea un sábado o domingo
        if fecha_reserva.weekday() not in [5, 6]:  # 5=Sábado, 6=Domingo
            raise forms.ValidationError("Solo se permiten reservas para los sábados y domingos.")
        return fecha_reserva