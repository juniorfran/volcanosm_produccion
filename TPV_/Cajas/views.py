"""Vistas del modulo de Cajas del POS (apertura, cierre/arqueo y reportes)."""
from datetime import datetime, time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from TPV_.utils import admin_required

from .forms import (
    CajasForm,
    CajasUpdateForm,
    CloseCajaForm,
    OpenCajaForm,
    ReporteAperturasForm,
)
from .models import AperturaCaja, Cajas, CierreCaja, MovimientoCaja


@login_required
def cajas_list(request):
    """Lista de cajas. Resalta la caja abierta del usuario actual."""
    cajas = Cajas.objects.select_related('usuario_responsable').order_by('numero_caja')
    caja_abierta_usuario = cajas.filter(
        estado='abierto', usuario_responsable=request.user
    ).first()
    context = {
        'cajas': cajas,
        'caja_abierta_usuario': caja_abierta_usuario,
    }
    return render(request, 'cajas/lista_cajas.html', context)


@admin_required
def cajas_create(request):
    """Crear una caja (solo numero y nombre)."""
    if request.method == 'POST':
        form = CajasForm(request.POST)
        if form.is_valid():
            caja = form.save(commit=False)
            # La caja nace cerrada; se abre con la accion de apertura.
            caja.estado = 'cerrado'
            caja.efectivo_inicial = 0
            caja.monto_total_efectivo = 0
            caja.monto_ventas = 0
            caja.monto_gastos_devoluciones = 0
            caja.fecha_hora_apertura = timezone.now()
            caja.informacion_auditoria = (
                f'Creada por {request.user} el {timezone.now():%Y-%m-%d %H:%M}'
            )
            caja.comentarios_notas = ''
            caja.save()
            messages.success(request, 'Caja creada correctamente.')
            return redirect('cajas_list')
    else:
        form = CajasForm()
    return render(request, 'cajas/caja_form.html', {'form': form, 'titulo': 'Nueva caja'})


@admin_required
def cajas_update(request, pk):
    """Editar datos basicos de una caja."""
    caja = get_object_or_404(Cajas, pk=pk)
    if request.method == 'POST':
        form = CajasUpdateForm(request.POST, instance=caja)
        if form.is_valid():
            form.save()
            messages.success(request, 'Caja actualizada correctamente.')
            return redirect('cajas_list')
    else:
        form = CajasUpdateForm(instance=caja)
    return render(
        request,
        'cajas/caja_form.html',
        {'form': form, 'titulo': f'Editar caja {caja.numero_caja}', 'caja': caja},
    )


@admin_required
def cajas_delete(request, pk):
    """Eliminar una caja (solo POST). Bloquea si tiene ventas asociadas."""
    caja = get_object_or_404(Cajas, pk=pk)
    if request.method == 'POST':
        try:
            caja.delete()
        except ProtectedError:
            messages.error(
                request,
                'No se puede eliminar la caja porque tiene ventas o alquileres asociados.',
            )
            return redirect('cajas_list')
        messages.success(request, 'Caja eliminada correctamente.')
        return redirect('cajas_list')
    return render(request, 'cajas/caja_confirm_delete.html', {'caja': caja})


@login_required
def caja_open(request, pk):
    """Abrir una caja: aplica la logica de apertura en una transaccion."""
    caja = get_object_or_404(Cajas, pk=pk)

    # Un usuario solo puede tener una caja abierta a la vez.
    caja_abierta = (
        Cajas.objects.filter(estado='abierto', usuario_responsable=request.user)
        .exclude(pk=caja.pk)
        .first()
    )
    if caja_abierta:
        messages.error(
            request,
            f'Ya tiene la caja "{caja_abierta.nombre_caja}" abierta. '
            'Debe cerrarla antes de abrir otra.',
        )
        return redirect('cajas_list')

    if caja.estado == 'abierto':
        messages.warning(request, 'Esta caja ya está abierta.')
        return redirect('cajas_list')

    if request.method == 'POST':
        form = OpenCajaForm(request.POST)
        if form.is_valid():
            efectivo_inicial = form.cleaned_data['efectivo_inicial']
            comentarios = form.cleaned_data['comentarios_notas'] or ''
            ahora = timezone.now()
            with transaction.atomic():
                caja = Cajas.objects.select_for_update().get(pk=caja.pk)
                caja.estado = 'abierto'
                caja.efectivo_inicial = efectivo_inicial
                caja.monto_total_efectivo = efectivo_inicial
                caja.monto_ventas = 0
                caja.monto_gastos_devoluciones = 0
                caja.efectivo_cierre = None
                caja.fecha_hora_apertura = ahora
                caja.fecha_hora_cierre = None
                caja.usuario_responsable = request.user
                caja.comentarios_notas = comentarios
                caja.save()
                AperturaCaja.objects.create(
                    caja=caja,
                    efectivo_inicial=efectivo_inicial,
                    fecha_hora_apertura=ahora,
                    usuario_responsable=request.user,
                    comentarios_notas=comentarios,
                )
            messages.success(request, 'Caja abierta correctamente.')
            return redirect('cajas_list')
    else:
        form = OpenCajaForm()
    return render(request, 'cajas/caja_open.html', {'form': form, 'caja': caja})


@login_required
def caja_close(request, pk):
    """Cierre/arqueo de caja: compara efectivo esperado vs contado."""
    caja = get_object_or_404(Cajas, pk=pk)

    if caja.estado != 'abierto':
        messages.warning(request, 'Solo se pueden cerrar cajas abiertas.')
        return redirect('cajas_list')

    arqueo = None
    if request.method == 'POST':
        form = CloseCajaForm(request.POST)
        if form.is_valid():
            efectivo_cierre = form.cleaned_data['efectivo_cierre']
            comentarios = form.cleaned_data['comentarios_notas'] or ''
            ahora = timezone.now()
            with transaction.atomic():
                caja = Cajas.objects.select_for_update().get(pk=caja.pk)
                esperado = caja.monto_total_efectivo or 0
                diferencia = efectivo_cierre - esperado
                caja.efectivo_cierre = efectivo_cierre
                caja.fecha_hora_cierre = ahora
                caja.estado = 'cerrado'
                caja.comentarios_notas = comentarios
                caja.save()
                CierreCaja.objects.create(
                    caja=caja,
                    efectivo_cierre=efectivo_cierre,
                    fecha_hora_cierre=ahora,
                    usuario_responsable=request.user,
                    comentarios_notas=comentarios,
                )
            arqueo = {
                'esperado': esperado,
                'contado': efectivo_cierre,
                'diferencia': diferencia,
            }
            messages.success(request, 'Caja cerrada correctamente.')
            return render(
                request,
                'cajas/caja_close.html',
                {'caja': caja, 'arqueo': arqueo, 'cerrada': True},
            )
    else:
        form = CloseCajaForm()
    return render(
        request,
        'cajas/caja_close.html',
        {'form': form, 'caja': caja, 'esperado': caja.monto_total_efectivo},
    )


@login_required
def caja_detalle(request, caja_id):
    """Detalle de una caja con sus movimientos y totales."""
    caja = get_object_or_404(Cajas, pk=caja_id)
    movimientos = MovimientoCaja.objects.filter(caja=caja).order_by('-fecha_creacion')
    diferencia = None
    if caja.efectivo_cierre is not None:
        diferencia = caja.efectivo_cierre - (caja.monto_total_efectivo or 0)
    context = {
        'caja': caja,
        'movimientos': movimientos,
        'diferencia': diferencia,
    }
    return render(request, 'cajas/detalle_caja.html', context)


@login_required
def reporte_aperturas(request):
    """Reporte HTML imprimible de aperturas/cierres por rango de fechas."""
    form = ReporteAperturasForm(request.GET or None)
    aperturas = cierres = None
    filtros = None

    if request.GET and form.is_valid():
        caja = form.cleaned_data['caja']
        fecha_inicio = form.cleaned_data['fecha_inicio']
        fecha_fin = form.cleaned_data['fecha_fin']
        # Rango inclusivo (00:00 del inicio a 23:59:59 del fin).
        inicio_dt = timezone.make_aware(datetime.combine(fecha_inicio, time.min))
        fin_dt = timezone.make_aware(datetime.combine(fecha_fin, time.max))

        aperturas = AperturaCaja.objects.select_related('caja', 'usuario_responsable').filter(
            fecha_hora_apertura__range=(inicio_dt, fin_dt)
        )
        cierres = CierreCaja.objects.select_related('caja', 'usuario_responsable').filter(
            fecha_hora_cierre__range=(inicio_dt, fin_dt)
        )
        if caja:
            aperturas = aperturas.filter(caja=caja)
            cierres = cierres.filter(caja=caja)
        aperturas = aperturas.order_by('fecha_hora_apertura')
        cierres = cierres.order_by('fecha_hora_cierre')
        filtros = {
            'caja': caja,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
        }

    context = {
        'form': form,
        'aperturas': aperturas,
        'cierres': cierres,
        'filtros': filtros,
        'generado': timezone.now(),
    }
    return render(request, 'cajas/apertura/reporte_form.html', context)
