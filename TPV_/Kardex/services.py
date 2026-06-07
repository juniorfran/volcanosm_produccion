"""Servicio central de movimientos de inventario (kardex).

Toda variación de stock DEBE pasar por aquí para mantener el historial y
evitar descuadres. Bloquea la fila del producto (select_for_update), por lo
que debe ejecutarse dentro de una transacción atómica.
"""
from django.db import transaction

from TPV_.Productos.models import Producto
from .models import MovimientoInventario


@transaction.atomic
def registrar_movimiento(producto, tipo, cantidad, usuario=None, motivo="", referencia=""):
    """Aplica un movimiento de stock y lo registra en el kardex.

    cantidad > 0 suma stock (entrada/devolución); cantidad < 0 resta (salida).
    Lanza ValueError si el stock resultante sería negativo.
    """
    p = Producto.objects.select_for_update().get(pk=producto.pk)
    anterior = p.stock or 0
    nuevo = anterior + cantidad
    if nuevo < 0:
        raise ValueError(
            f"Stock insuficiente de «{p.nombre}»: disponible {anterior}, se requieren {abs(cantidad)}"
        )
    p.stock = nuevo
    p.save(update_fields=["stock"])
    return MovimientoInventario.objects.create(
        producto=p,
        tipo=tipo,
        cantidad=cantidad,
        stock_anterior=anterior,
        stock_nuevo=nuevo,
        usuario=usuario,
        motivo=motivo,
        referencia=referencia,
    )
