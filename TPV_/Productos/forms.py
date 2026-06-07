from django import forms

from TPV_.Productos.models import Categoria, Producto


class ProductoForm(forms.ModelForm):
    """Alta/edición de productos.

    El stock NO se edita aquí: se maneja mediante movimientos de kardex
    (entradas/ajustes). En la creación se captura `stock_inicial`, que la
    vista aplica con `registrar_movimiento` para que quede registrado.
    """

    stock_inicial = forms.IntegerField(
        label="Stock inicial",
        min_value=0,
        required=False,
        initial=0,
        help_text="Existencia con la que ingresa el producto. Se registra como entrada en el kardex.",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0}),
    )

    class Meta:
        model = Producto
        fields = [
            "nombre",
            "categoria",
            "codigo_de_barras",
            "precio_de_venta",
            "precio_de_compra",
            "stock_minimo",
            "status",
            "descripcion",
            "imagen",
        ]
        labels = {
            "precio_de_venta": "Precio de venta (con IVA)",
            "precio_de_compra": "Precio de compra (costo)",
            "codigo_de_barras": "Código de barras",
            "stock_minimo": "Alerta de stock mínimo",
            "status": "Estado",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Jugo de naranja 500ml"}),
            "codigo_de_barras": forms.TextInput(attrs={"class": "form-control", "placeholder": "Opcional"}),
            "stock_minimo": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "precio_de_compra": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}),
            "precio_de_venta": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Campos opcionales: no obligar al usuario
        for f in ("codigo_de_barras", "precio_de_compra", "stock_minimo", "descripcion", "imagen"):
            if f in self.fields:
                self.fields[f].required = False
        # En edición no se captura stock inicial (el stock se ajusta por kardex).
        if self.instance and self.instance.pk:
            self.fields.pop("stock_inicial", None)


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
        }
