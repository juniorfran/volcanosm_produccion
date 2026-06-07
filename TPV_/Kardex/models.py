from django.db import models
from django.contrib.auth.models import User

from TPV_.Productos.models import Producto


class MovimientoInventario(models.Model):
    """Historial (kardex) de cada cambio de stock de un producto."""

    TIPOS = [
        ("entrada", "Entrada (compra/recepción)"),
        ("salida", "Salida (venta)"),
        ("ajuste", "Ajuste manual"),
        ("devolucion", "Devolución (reingreso)"),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="movimientos")
    tipo = models.CharField(max_length=20, choices=TIPOS)
    cantidad = models.IntegerField(help_text="Positivo suma stock, negativo resta")
    stock_anterior = models.IntegerField()
    stock_nuevo = models.IntegerField()
    motivo = models.CharField(max_length=255, blank=True)
    referencia = models.CharField(max_length=100, blank=True, help_text="Ej. Venta VL-0001")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_creacion"]
        verbose_name = "Movimiento de inventario"
        verbose_name_plural = "Kardex"

    def __str__(self):
        return f"{self.get_tipo_display()} {self.cantidad} - {self.producto}"
