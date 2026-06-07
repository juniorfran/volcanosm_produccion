from django import forms

from TPV_.Productos.models import Producto


class MovimientoForm(forms.Form):
    """Registro de entrada de mercadería o ajuste de inventario.

    - entrada: la cantidad debe ser positiva (suma stock).
    - ajuste: la cantidad puede ser positiva o negativa (corrige el stock).
    """

    TIPO_CHOICES = [
        ("entrada", "Entrada (compra/recepción)"),
        ("ajuste", "Ajuste manual"),
    ]

    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all().order_by("nombre"),
        label="Producto",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        label="Tipo de movimiento",
        initial="entrada",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    cantidad = forms.IntegerField(
        label="Cantidad",
        help_text="En entradas usa un número positivo. En ajustes puede ser positivo o negativo.",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    motivo = forms.CharField(
        label="Motivo",
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get("tipo")
        cantidad = cleaned.get("cantidad")
        if cantidad is None:
            return cleaned
        if cantidad == 0:
            self.add_error("cantidad", "La cantidad no puede ser cero.")
        elif tipo == "entrada" and cantidad < 0:
            self.add_error("cantidad", "En una entrada la cantidad debe ser positiva.")
        return cleaned
