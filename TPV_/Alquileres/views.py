"""Vistas del módulo de Alquileres del POS de Volcano.

Gestión de artículos de alquiler (tiendas, colchonetas, hamacas) y operación
de salida/devolución de equipo con control de inventario y caja.

Las tarifas YA INCLUYEN IVA. El depósito es una garantía: NO se contabiliza
como venta en caja.
"""
import json
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from TPV_.utils import admin_required, q
from TPV_.Cajas.models import Cajas
from TPV_.Cajas.services import registrar_movimiento_caja
from TPV_.Clientes.models import Cliente

from .forms import ArticuloAlquilerForm
from .models import Alquiler, AlquilerDetalle, ArticuloAlquiler


def _caja_abierta(request):
    """Caja abierta del usuario actual (o None)."""
    return Cajas.objects.filter(estado="abierto", usuario_responsable=request.user).first()


def _to_decimal(valor, defecto="0"):
    """Convierte un valor de formulario a Decimal de forma tolerante."""
    if valor is None or valor == "":
        valor = defecto
    try:
        return q(Decimal(str(valor).replace(",", ".")))
    except (InvalidOperation, ValueError):
        return q(Decimal(defecto))


# ---------------------------------------------------------------------------
# ARTÍCULOS (gestión, solo administradores)
# ---------------------------------------------------------------------------

@admin_required
def articulo_list(request):
    articulos = ArticuloAlquiler.objects.all()
    return render(request, "alquileres/articulo_list.html", {"articulos": articulos})


@admin_required
def articulo_create(request):
    if request.method == "POST":
        form = ArticuloAlquilerForm(request.POST, request.FILES)
        if form.is_valid():
            articulo = form.save(commit=False)
            # Al crear, todo el inventario está disponible.
            articulo.cantidad_disponible = articulo.cantidad_total
            articulo.save()
            messages.success(request, f'Artículo "{articulo.nombre}" creado correctamente.')
            return redirect("articulo_list")
    else:
        form = ArticuloAlquilerForm()
    return render(
        request,
        "alquileres/articulo_form.html",
        {"form": form, "titulo": "Nuevo artículo de alquiler"},
    )


@admin_required
def articulo_update(request, pk):
    articulo = get_object_or_404(ArticuloAlquiler, pk=pk)
    if request.method == "POST":
        total_anterior = articulo.cantidad_total
        form = ArticuloAlquilerForm(request.POST, request.FILES, instance=articulo)
        if form.is_valid():
            articulo = form.save(commit=False)
            # Ajusta la disponibilidad de forma coherente con el cambio de total.
            delta = articulo.cantidad_total - total_anterior
            nueva_disponible = articulo.cantidad_disponible + delta
            # No dejar disponible negativo ni mayor que el total.
            nueva_disponible = max(0, min(nueva_disponible, articulo.cantidad_total))
            articulo.cantidad_disponible = nueva_disponible
            articulo.save()
            messages.success(request, f'Artículo "{articulo.nombre}" actualizado.')
            return redirect("articulo_list")
    else:
        form = ArticuloAlquilerForm(instance=articulo)
    return render(
        request,
        "alquileres/articulo_form.html",
        {"form": form, "titulo": f"Editar: {articulo.nombre}", "articulo": articulo},
    )


@admin_required
def articulo_delete(request, pk):
    articulo = get_object_or_404(ArticuloAlquiler, pk=pk)
    if request.method == "POST":
        nombre = articulo.nombre
        articulo.delete()
        messages.success(request, f'Artículo "{nombre}" eliminado.')
        return redirect("articulo_list")
    return render(
        request,
        "alquileres/articulo_confirm_delete.html",
        {"articulo": articulo},
    )


# ---------------------------------------------------------------------------
# ALQUILERES (operación)
# ---------------------------------------------------------------------------

@login_required
def alquiler_nuevo(request):
    """POS de salida de equipo."""
    if request.method == "POST":
        caja = _caja_abierta(request)
        if not caja:
            messages.error(request, "No tienes una caja abierta. Abre una caja antes de registrar un alquiler.")
            return redirect("alquiler_nuevo")

        # Items: JSON [{articulo_id, cantidad}, ...]
        try:
            items = json.loads(request.POST.get("items", "[]"))
        except (ValueError, TypeError):
            items = []

        items = [
            it for it in items
            if int(it.get("cantidad", 0) or 0) > 0 and it.get("articulo_id")
        ]
        if not items:
            messages.error(request, "Debes agregar al menos un artículo al alquiler.")
            return redirect("alquiler_nuevo")

        cliente_id = request.POST.get("cliente_id") or None
        deposito = _to_decimal(request.POST.get("deposito"))
        tipo_pago = request.POST.get("tipo_pago") or "efectivo"

        try:
            with transaction.atomic():
                # Bloquea la caja.
                caja = Cajas.objects.select_for_update().get(pk=caja.pk)

                cliente = None
                if cliente_id:
                    cliente = Cliente.objects.filter(pk=cliente_id).first()

                total_tarifa = Decimal("0")
                lineas = []  # (articulo, cantidad)
                for it in items:
                    cantidad = int(it.get("cantidad", 0) or 0)
                    articulo = ArticuloAlquiler.objects.select_for_update().get(pk=it["articulo_id"])
                    if cantidad > articulo.cantidad_disponible:
                        raise ValueError(f"No hay suficientes {articulo.nombre} disponibles "
                                         f"(disponibles: {articulo.cantidad_disponible}, solicitados: {cantidad}).")
                    articulo.cantidad_disponible -= cantidad
                    articulo.save(update_fields=["cantidad_disponible"])
                    total_tarifa += articulo.tarifa * cantidad
                    lineas.append((articulo, cantidad))

                total_tarifa = q(total_tarifa)

                alquiler = Alquiler.objects.create(
                    cliente=cliente,
                    caja=caja,
                    usuario=request.user,
                    estado="activo",
                    tipo_pago=tipo_pago,
                    deposito=deposito,
                    total_tarifa=total_tarifa,
                    notas=request.POST.get("notas", ""),
                )
                alquiler.numero = f"AL-{alquiler.pk:05d}"
                alquiler.save(update_fields=["numero"])

                for articulo, cantidad in lineas:
                    AlquilerDetalle.objects.create(
                        alquiler=alquiler,
                        articulo=articulo,
                        cantidad=cantidad,
                        tarifa_unitaria=articulo.tarifa,
                    )

                # Cobro de la tarifa de alquiler. El depósito NO entra como venta.
                registrar_movimiento_caja(
                    caja,
                    request.user,
                    "venta",
                    efectivo=(total_tarifa if tipo_pago == "efectivo" else Decimal("0")),
                    venta=total_tarifa,
                    motivo=f"Alquiler {alquiler.numero}",
                )
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("alquiler_nuevo")
        except ArticuloAlquiler.DoesNotExist:
            messages.error(request, "Uno de los artículos seleccionados ya no existe.")
            return redirect("alquiler_nuevo")

        messages.success(request, f"Alquiler {alquiler.numero} registrado correctamente.")
        return redirect("alquiler_detalle", pk=alquiler.pk)

    # GET
    articulos = ArticuloAlquiler.objects.filter(activo=True, cantidad_disponible__gt=0)
    clientes = Cliente.objects.all().order_by("nombre", "apellido")
    caja = _caja_abierta(request)
    return render(
        request,
        "alquileres/alquiler_nuevo.html",
        {"articulos": articulos, "clientes": clientes, "caja": caja},
    )


@login_required
def alquiler_list(request):
    alquileres = (
        Alquiler.objects
        .select_related("cliente", "usuario", "caja")
        .order_by("estado", "-fecha_creacion")
    )
    return render(request, "alquileres/alquiler_list.html", {"alquileres": alquileres})


@login_required
def alquiler_detalle(request, pk):
    alquiler = get_object_or_404(
        Alquiler.objects.select_related("cliente", "usuario", "caja"), pk=pk
    )
    detalles = alquiler.detalles.select_related("articulo").all()
    return render(
        request,
        "alquileres/alquiler_detalle.html",
        {"alquiler": alquiler, "detalles": detalles},
    )


@login_required
def alquiler_devolver(request, pk):
    """Devolución total o parcial de un alquiler."""
    alquiler = get_object_or_404(
        Alquiler.objects.select_related("cliente", "usuario"), pk=pk
    )

    if alquiler.estado == "devuelto":
        messages.info(request, f"El alquiler {alquiler.numero} ya fue devuelto por completo.")
        return redirect("alquiler_detalle", pk=alquiler.pk)

    if request.method == "POST":
        try:
            with transaction.atomic():
                alq = (
                    Alquiler.objects.select_for_update()
                    .prefetch_related("detalles")
                    .get(pk=alquiler.pk)
                )
                detalles = list(alq.detalles.all())

                algo_devuelto = False
                for detalle in detalles:
                    campo = f"devolver_{detalle.pk}"
                    cantidad = int(request.POST.get(campo, 0) or 0)
                    if cantidad <= 0:
                        continue
                    if cantidad > detalle.pendiente:
                        raise ValueError(
                            f"No puedes devolver {cantidad} de {detalle.articulo.nombre}; "
                            f"solo hay {detalle.pendiente} pendiente(s)."
                        )
                    articulo = ArticuloAlquiler.objects.select_for_update().get(pk=detalle.articulo_id)
                    articulo.cantidad_disponible += cantidad
                    if articulo.cantidad_disponible > articulo.cantidad_total:
                        articulo.cantidad_disponible = articulo.cantidad_total
                    articulo.save(update_fields=["cantidad_disponible"])

                    detalle.cantidad_devuelta += cantidad
                    detalle.save(update_fields=["cantidad_devuelta"])
                    algo_devuelto = True

                if not algo_devuelto:
                    raise ValueError("No indicaste ninguna cantidad a devolver.")

                # Recalcula estado del alquiler.
                detalles = list(alq.detalles.all())
                total_pendiente = sum(d.pendiente for d in detalles)
                if total_pendiente == 0:
                    alq.estado = "devuelto"
                    if not alq.fecha_devolucion:
                        alq.fecha_devolucion = timezone.now()
                    alq.save(update_fields=["estado", "fecha_devolucion"])
                else:
                    alq.estado = "parcial"
                    alq.save(update_fields=["estado"])
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("alquiler_devolver", pk=alquiler.pk)

        messages.success(request, f"Devolución registrada para el alquiler {alquiler.numero}.")
        return redirect("alquiler_detalle", pk=alquiler.pk)

    # GET
    detalles = alquiler.detalles.select_related("articulo").all()
    pendientes = [d for d in detalles if d.pendiente > 0]
    return render(
        request,
        "alquileres/alquiler_devolver.html",
        {"alquiler": alquiler, "detalles": pendientes},
    )
