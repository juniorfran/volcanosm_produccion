"""Módulo de VENTAS del punto de venta (POS) de Volcano.

Reglas clave:
- Los precios YA INCLUYEN IVA (13 %). El total se calcula SIEMPRE con los
  precios del servidor, nunca con montos enviados por el cliente.
- Todo descuento/reingreso de stock pasa por el kardex
  (``registrar_movimiento``) y todo movimiento de efectivo por la caja
  (``registrar_movimiento_caja``), dentro de ``transaction.atomic`` y con la
  caja bloqueada con ``select_for_update``.
"""
import json
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from TPV_.Cajas.models import Cajas
from TPV_.Cajas.services import registrar_movimiento_caja
from TPV_.Clientes.models import Cliente
from TPV_.Kardex.services import registrar_movimiento
from TPV_.Productos.models import Categoria, Producto
from TPV_.utils import admin_required, desglose_iva, q

from .models import DetalleVenta, Ventas


def _caja_abierta_usuario(user):
    """Caja abierta del usuario (o None)."""
    return Cajas.objects.filter(estado='abierto', usuario_responsable=user).first()


@login_required
def punto_de_venta(request):
    """Pantalla POS: grilla de productos + carrito (JS)."""
    productos = (
        Producto.objects
        .filter(status='A', stock__gt=0)
        .select_related('categoria')
        .order_by('nombre')
    )
    categorias = Categoria.objects.order_by('nombre')
    caja_abierta = _caja_abierta_usuario(request.user)
    clientes = Cliente.objects.filter(estado='ACTIVO').order_by('nombre', 'apellido')

    context = {
        'productos': productos,
        'categorias': categorias,
        'caja_abierta': caja_abierta,
        'clientes': clientes,
    }
    return render(request, 'tpv/punto_ventas.html', context)


def _parse_items(request):
    """Devuelve la lista de items {producto_id, cantidad} desde el POST.

    El template envía los items como JSON en el campo ``items``. Se admite
    también el formato de POST repetidos (``producto_id`` + ``cantidad``) como
    respaldo.
    """
    raw = request.POST.get('items')
    if raw:
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            return []
        items = []
        for it in data:
            try:
                pid = int(it.get('producto_id'))
                cant = int(it.get('cantidad'))
            except (TypeError, ValueError, AttributeError):
                continue
            if cant > 0:
                items.append({'producto_id': pid, 'cantidad': cant})
        return items

    # Respaldo: listas paralelas en el POST.
    ids = request.POST.getlist('producto_id')
    cantidades = request.POST.getlist('cantidad')
    items = []
    for pid, cant in zip(ids, cantidades):
        try:
            pid = int(pid)
            cant = int(cant)
        except (TypeError, ValueError):
            continue
        if cant > 0:
            items.append({'producto_id': pid, 'cantidad': cant})
    return items


@login_required
@require_POST
def process_sale(request):
    """Procesa una venta: descuenta stock, registra caja y crea la venta."""
    caja = _caja_abierta_usuario(request.user)
    if not caja:
        messages.error(
            request,
            'No tienes una caja abierta. Abre una caja antes de vender.',
        )
        return redirect('punto_de_venta')

    items = _parse_items(request)
    if not items:
        messages.error(request, 'No hay productos en la venta.')
        return redirect('punto_de_venta')

    tipo_pago = request.POST.get('tipo_pago', 'efectivo')
    if tipo_pago not in ('efectivo', 'tarjeta', 'otro'):
        tipo_pago = 'efectivo'

    cliente = None
    cliente_id = request.POST.get('cliente_id')
    if cliente_id:
        cliente = Cliente.objects.filter(pk=cliente_id).first()

    try:
        with transaction.atomic():
            # Bloquea la caja para la duración de la transacción.
            caja = Cajas.objects.select_for_update().get(pk=caja.pk)

            # Carga productos y consolida cantidades por producto.
            cantidades = {}
            for it in items:
                cantidades[it['producto_id']] = cantidades.get(it['producto_id'], 0) + it['cantidad']

            productos = {
                p.pk: p
                for p in Producto.objects.filter(pk__in=cantidades.keys(), status='A')
            }
            if len(productos) != len(cantidades):
                raise ValueError('Uno o más productos ya no están disponibles.')

            # Total calculado SOLO con precios del servidor.
            total = Decimal('0')
            for pid, cant in cantidades.items():
                total += productos[pid].precio_de_venta * cant
            total = q(total)

            if total <= 0:
                raise ValueError('El total de la venta debe ser mayor que cero.')

            # Resuelve el pago.
            if tipo_pago == 'efectivo':
                recibe_raw = (request.POST.get('recibe') or '0').replace(',', '.')
                try:
                    recibe = Decimal(recibe_raw)
                except InvalidOperation:
                    raise ValueError('El monto recibido no es válido.')
                if recibe < total:
                    raise ValueError('El efectivo recibido es menor que el total.')
                recibe = q(recibe)
                cambio = q(recibe - total)
            else:
                recibe = total
                cambio = Decimal('0')

            subtotal, iva = desglose_iva(total)

            # Crea la venta (sin número aún para conocer el pk).
            venta = Ventas.objects.create(
                estado='F',
                caja=caja,
                cliente=cliente,
                usuario=request.user,
                tipo_pago=tipo_pago,
                descuento=Decimal('0'),
                recibe_caja=recibe,
                cambio=cambio,
                subtotal=subtotal,
                iva=iva,
                total=total,
            )
            venta.numero = f"VL-{venta.pk:05d}"
            venta.save(update_fields=['numero'])

            # Descuenta stock (kardex) y crea los detalles.
            for pid, cant in cantidades.items():
                producto = productos[pid]
                # Lanza ValueError si no hay stock suficiente -> rollback.
                registrar_movimiento(
                    producto,
                    'salida',
                    -cant,
                    usuario=request.user,
                    motivo=f"Venta {venta.numero}",
                    referencia=venta.numero,
                )
                linea_total = q(producto.precio_de_venta * cant)
                _, linea_iva = desglose_iva(linea_total)
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cant,
                    precio_unitario=producto.precio_de_venta,
                    iva=linea_iva,
                    subtotal=linea_total,
                )

            # Movimiento de caja: el efectivo solo varía si el pago fue efectivo.
            registrar_movimiento_caja(
                caja,
                request.user,
                'venta',
                efectivo=(total if tipo_pago == 'efectivo' else Decimal('0')),
                venta=total,
                motivo=f"Venta {venta.numero}",
            )
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect('punto_de_venta')

    messages.success(request, f"Venta {venta.numero} registrada correctamente.")
    return redirect('venta_detalle', venta_id=venta.pk)


@login_required
def ventas_por_caja(request):
    """Lista de ventas, filtrable por rango de fechas (opcional)."""
    ventas = (
        Ventas.objects
        .select_related('caja', 'cliente', 'usuario')
        .order_by('-fecha_hora_venta')
    )

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        ventas = ventas.filter(fecha_hora_venta__date__gte=start_date)
    if end_date:
        ventas = ventas.filter(fecha_hora_venta__date__lte=end_date)

    context = {
        'ventas': ventas,
        'start_date': start_date or '',
        'end_date': end_date or '',
    }
    return render(request, 'tpv/general_ventas.html', context)


@login_required
def venta_detalle(request, venta_id):
    """Ticket / recibo imprimible de una venta."""
    venta = get_object_or_404(
        Ventas.objects
        .select_related('caja', 'cliente', 'usuario')
        .prefetch_related('detalles__producto'),
        pk=venta_id,
    )
    return render(request, 'tpv/detalle_venta.html', {'venta': venta})


@admin_required
@require_POST
def anular_venta(request, venta_id):
    """Anula una venta: reingresa stock y revierte el movimiento de caja."""
    venta = get_object_or_404(
        Ventas.objects.select_related('caja').prefetch_related('detalles__producto'),
        pk=venta_id,
    )

    if venta.estado == 'A':
        messages.info(request, f"La venta {venta.numero} ya estaba anulada.")
        return redirect('ventas_por_caja')

    try:
        with transaction.atomic():
            caja = Cajas.objects.select_for_update().get(pk=venta.caja_id)

            for detalle in venta.detalles.all():
                if detalle.producto_id:
                    registrar_movimiento(
                        detalle.producto,
                        'devolucion',
                        detalle.cantidad,
                        usuario=request.user,
                        motivo=f"Anulación venta {venta.numero}",
                        referencia=venta.numero,
                    )

            registrar_movimiento_caja(
                caja,
                request.user,
                'devuelta',
                efectivo=(-venta.total if venta.tipo_pago == 'efectivo' else Decimal('0')),
                venta=-venta.total,
                motivo=f"Anulación venta {venta.numero}",
            )

            venta.estado = 'A'
            venta.save(update_fields=['estado'])
    except ValueError as exc:
        messages.error(request, f"No se pudo anular la venta: {exc}")
        return redirect('ventas_por_caja')

    messages.success(request, f"Venta {venta.numero} anulada y stock reingresado.")
    return redirect('ventas_por_caja')
