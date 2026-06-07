"""Formularios del módulo de Alquileres."""
from django import forms

from .models import ArticuloAlquiler


class ArticuloAlquilerForm(forms.ModelForm):
    """Alta/edición de artículos de alquiler.

    La cantidad_disponible NO se edita aquí: al crear se iguala a la cantidad
    total y al editar se ajusta de forma coherente en la vista.
    """

    class Meta:
        model = ArticuloAlquiler
        fields = [
            "nombre",
            "descripcion",
            "categoria",
            "cantidad_total",
            "tarifa",
            "deposito_sugerido",
            "activo",
            "imagen",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Tienda de campaña 4 personas"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Descripción opcional"}),
            "categoria": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tienda / Colchoneta / Hamaca", "list": "categorias-list"}),
            "cantidad_total": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "tarifa": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "deposito_sugerido": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "categoria": "Categoría",
            "cantidad_total": "Cantidad total (inventario)",
            "tarifa": "Tarifa por unidad (IVA incluido)",
            "deposito_sugerido": "Depósito sugerido",
            "activo": "Activo",
            "imagen": "Imagen",
        }
