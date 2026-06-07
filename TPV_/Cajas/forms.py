from django import forms

from .models import Cajas


class CajasForm(forms.ModelForm):
    """Crear caja: solo datos de identificacion."""

    class Meta:
        model = Cajas
        fields = ['numero_caja', 'nombre_caja']
        widgets = {
            'numero_caja': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_caja': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'numero_caja': 'Número de caja',
            'nombre_caja': 'Nombre de la caja',
        }


class CajasUpdateForm(forms.ModelForm):
    """Editar datos basicos de la caja."""

    class Meta:
        model = Cajas
        fields = ['numero_caja', 'nombre_caja']
        widgets = {
            'numero_caja': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_caja': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'numero_caja': 'Número de caja',
            'nombre_caja': 'Nombre de la caja',
        }


class OpenCajaForm(forms.Form):
    """Apertura de caja: efectivo inicial con que se abre."""

    efectivo_inicial = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        label='Efectivo inicial',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
    )
    comentarios_notas = forms.CharField(
        required=False,
        label='Comentarios / Notas',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )


class CloseCajaForm(forms.Form):
    """Cierre / arqueo de caja: efectivo realmente contado."""

    efectivo_cierre = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        label='Efectivo contado (arqueo)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
    )
    comentarios_notas = forms.CharField(
        required=False,
        label='Comentarios / Notas',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )


class ReporteAperturasForm(forms.Form):
    """Filtro por rango de fechas para el reporte de aperturas/cierres."""

    caja = forms.ModelChoiceField(
        queryset=Cajas.objects.all(),
        required=False,
        label='Caja (opcional)',
        empty_label='Todas las cajas',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    fecha_inicio = forms.DateField(
        label='Fecha inicio',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    fecha_fin = forms.DateField(
        label='Fecha fin',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get('fecha_inicio')
        fin = cleaned.get('fecha_fin')
        if inicio and fin and inicio > fin:
            raise forms.ValidationError('La fecha de inicio no puede ser mayor que la fecha fin.')
        return cleaned
