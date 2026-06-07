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
            "descripcion",
            "codigo_de_barras",
            "sku",
            "stock_minimo",
            "presentacion_producto",
            "precio",
            "precio_de_compra",
            "precio_de_venta",
            "precio_al_por_mayor",
            "porcentaje_de_descuento",
            "marca",
            "modelo",
            "producto_perecedero",
            "fecha_de_expiracion",
            "tiempo_de_garantia",
            "tiempo_de_garantia_tipo",
            "proveedor",
            "categoria",
            "status",
            "imagen",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "codigo_de_barras": forms.TextInput(attrs={"class": "form-control"}),
            "sku": forms.NumberInput(attrs={"class": "form-control"}),
            "stock_minimo": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "presentacion_producto": forms.TextInput(attrs={"class": "form-control"}),
            "precio": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "precio_de_compra": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "precio_de_venta": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "precio_al_por_mayor": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "porcentaje_de_descuento": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "marca": forms.TextInput(attrs={"class": "form-control"}),
            "modelo": forms.TextInput(attrs={"class": "form-control"}),
            "producto_perecedero": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "fecha_de_expiracion": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "tiempo_de_garantia": forms.TextInput(attrs={"class": "form-control"}),
            "tiempo_de_garantia_tipo": forms.TextInput(attrs={"class": "form-control"}),
            "proveedor": forms.Select(attrs={"class": "form-select"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha_de_expiracion"].input_formats = ["%Y-%m-%dT%H:%M"]
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
