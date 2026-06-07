"""Servicio de movimientos de caja (efectivo).

Actualiza los acumulados de la caja y deja rastro en MovimientoCaja. Debe
llamarse dentro de transaction.atomic con la caja bloqueada por el llamador
(select_for_update).
"""
from decimal import Decimal

from .models import MovimientoCaja


def registrar_movimiento_caja(caja, usuario, tipo, efectivo=Decimal("0"), venta=Decimal("0"), motivo=""):
    """Registra un movimiento de caja.

    efectivo: variación del efectivo en caja (+ entra, - sale). 0 si el pago
              no fue en efectivo (ej. tarjeta).
    venta:    variación del total vendido (para reportes). + venta, - devolución.
    """
    efectivo = Decimal(efectivo)
    venta = Decimal(venta)
    anterior = caja.monto_total_efectivo or Decimal("0")
    actual = anterior + efectivo
    caja.monto_total_efectivo = actual
    if venta >= 0:
        caja.monto_ventas = (caja.monto_ventas or Decimal("0")) + venta
    else:
        caja.monto_gastos_devoluciones = (caja.monto_gastos_devoluciones or Decimal("0")) + (-venta)
    caja.save(update_fields=["monto_total_efectivo", "monto_ventas", "monto_gastos_devoluciones"])
    return MovimientoCaja.objects.create(
        caja=caja,
        usuario=usuario,
        tipo_movimiento=tipo,
        efectivo_anterior=anterior,
        cantidad_efectivo=efectivo,
        efectivo_actual=actual,
        motivo=motivo,
    )
