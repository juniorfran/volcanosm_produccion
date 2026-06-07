"""Utilidades compartidas del TPV: IVA (precios incluyen IVA) y roles."""
from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.decorators import login_required, user_passes_test

IVA_RATE = Decimal("0.13")
CENT = Decimal("0.01")


def q(valor):
    """Redondea a 2 decimales."""
    return Decimal(valor).quantize(CENT, rounding=ROUND_HALF_UP)


def desglose_iva(total_con_iva):
    """Dado un total que YA incluye IVA, devuelve (subtotal_sin_iva, monto_iva)."""
    total = Decimal(total_con_iva)
    base = q(total / (Decimal("1") + IVA_RATE))
    iva = q(total - base)
    return base, iva


def es_admin(user):
    """Admin del TPV = staff o superuser."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def admin_required(view_func):
    """Solo administradores (gestión de productos, inventario, reportes, etc.)."""
    return login_required(user_passes_test(es_admin)(view_func))
