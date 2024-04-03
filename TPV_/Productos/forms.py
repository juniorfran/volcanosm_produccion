from decimal import Decimal
from django import forms
from django.core.validators import MinValueValidator

from TPV_.Productos.models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'