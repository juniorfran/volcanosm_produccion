from django import forms
from .models import Cajas
from django.contrib.auth.models import User

class CajasForm(forms.ModelForm):
    class Meta:
        model = Cajas
        fields = ['numero_caja', 'nombre_caja', 'efectivo_inicial', 'usuario_responsable', 'informacion_auditoria', 'comentarios_notas']

class CajasUpdateForm(forms.ModelForm):
    class Meta:
        model = Cajas
        fields = ['numero_caja', 'nombre_caja', 'efectivo_inicial', 'usuario_responsable', 'informacion_auditoria', 'comentarios_notas']

class OpenCajaForm(forms.ModelForm):
    class Meta:
        model = Cajas
        fields = ['efectivo_inicial', 'comentarios_notas']

class CloseCajaForm(forms.ModelForm):
    class Meta:
        model = Cajas
        fields = ['efectivo_cierre', 'comentarios_notas']

class CountCajaForm(forms.ModelForm):
    class Meta:
        model = Cajas
        fields = ['monto_ventas', 'monto_gastos_devoluciones', 'monto_total_efectivo']
        
class CashBoxForm(forms.Form):
    caja = forms.ModelChoiceField(queryset=Cajas.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))