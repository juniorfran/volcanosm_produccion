import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cajas, AperturaCaja, CierreCaja
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from .forms import CajasForm, CajasUpdateForm, CloseCajaForm, CountCajaForm, OpenCajaForm, CashBoxForm
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# VISTAS PARA CAJAS
def cajas_list(request):
    cajas = Cajas.objects.all()
    return render(request, 'cajas/lista_cajas.html', {'cajas': cajas})

def cajas_create(request):
    if request.method == 'POST':
        form = CajasForm(request.POST)
        if form.is_valid():
            caja = form.save(commit=False)
            caja.estado = 'abierto'
            caja.fecha_hora_apertura = timezone.now()
            caja.monto_total_efectivo = caja.efectivo_inicial
            caja.save()
            return redirect('cajas_list')
    else:
        form = CajasForm()
    return render(request, 'cajas/caja_form.html', {'form': form})

def cajas_update(request, pk):
    caja = get_object_or_404(Cajas, pk=pk)
    if request.method == 'POST':
        form = CajasUpdateForm(request.POST, instance=caja)
        if form.is_valid():
            caja = form.save()
            if caja.estado == 'cerrado':
                total_ventas = caja.monto_ventas + caja.monto_gastos_devoluciones
                caja.monto_total_efectivo = caja.efectivo_cierre + total_ventas
                caja.save()
            return redirect('cajas_list')
    else:
        form = CajasUpdateForm(instance=caja)
    return render(request, 'cajas/caja_form.html', {'form': form})

def cajas_delete(request, pk):
    caja = get_object_or_404(Cajas, pk=pk)
    if request.method == 'POST':
        caja.delete()
        return redirect('cajas_list')
    else:
        return render(request, 'cajas/caja_confirm_delete.html', {'caja': caja})

def caja_open(request, pk):
    caja = get_object_or_404(Cajas, pk=pk)
    if request.method == 'POST':
        form = OpenCajaForm(request.POST, instance=caja)
        if form.is_valid():
            caja = form.save(commit=False)
            caja.estado = 'abierto'
            caja.fecha_hora_apertura = timezone.now()
            caja.monto_total_efectivo = caja.efectivo_inicial
            caja.save()
            
            # add new aperturaCaja record
            apertura_caja = AperturaCaja(
                caja = caja, 
                efectivo_inicial = caja.efectivo_inicial,
                usuario_responsable = request.user,
                fecha_hora_apertura = timezone.now(),
                comentarios_notas = form.cleaned_data['comentarios_notas']
            )
            apertura_caja.save()
            return redirect('cajas_list')
    else:
        form = OpenCajaForm(instance=caja)
    return render(request, 'cajas/caja_open.html', {'form': form, 'caja': caja})

def caja_close(request, pk):
    caja = get_object_or_404(Cajas, pk=pk)
    if request.method == 'POST':
        form = CloseCajaForm(request.POST, instance=caja)
        if form.is_valid():
            caja = form.save(commit=False)
            caja.estado = 'cerrado'
            caja.fecha_hora_cierre = timezone.now()
            caja.monto_total_efectivo = caja.efectivo_cierre
            caja.save()
            
            # Add new CierreCaja record
            cierre_caja = CierreCaja(
                caja=caja,
                efectivo_cierre = caja.efectivo_cierre,
                usuario_responsable=request.user,
                fecha_hora_cierre = timezone.now(),
                comentarios_notas=form.cleaned_data['comentarios_notas']
            )
            cierre_caja.save()
            
            return redirect('cajas_list')
    else:
        form = CloseCajaForm(instance=caja)
    return render(request, 'cajas/caja_close.html', {'form': form, 'caja': caja})

def caja_count(request, pk):
    caja = get_object_or_404(Cajas, pk=pk)
    if request.method == 'POST':
        form = CountCajaForm(request.POST, instance=caja)
        if form.is_valid():
            caja = form.save()
            if caja.efectivo_cierre is None:
                caja.efectivo_cierre = caja.monto_total_efectivo
            caja.estado = 'cerrado'
            caja.fecha_hora_cierre = timezone.now()
            caja.save()
            return redirect('cajas_list')
    else:
        form = CountCajaForm(instance=caja)
    return render(request, 'cajas/caja_count.html', {'form': form, 'caja': caja})

def generar_reporte(request):
    if request.method == 'POST':
        form = CashBoxForm(request.POST)
        if form.is_valid():
            caja = form.cleaned_data['caja']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            aperturas = AperturaCaja.objects.filter(caja=caja, fecha_hora_apertura__range=[start_date, end_date]).order_by('fecha_hora_apertura')
            cierres = CierreCaja.objects.filter(caja=caja, fecha_hora_cierre__range=[start_date, end_date]).order_by('fecha_hora_cierre')

            # Prepare data for the table
            table_data = [['Fecha Hora Apertura', 'Monto Apertura', 'Fecha Hora Cierre', 'Monto Cierre']]
            for apertura, cierre in zip(aperturas, cierres):
                table_data.append([apertura.fecha_hora_apertura, apertura.monto_apertura, cierre.fecha_hora_cierre, cierre.monto_cierre])

            # Create the PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="reporte_aperturas_cajas.pdf"'
            doc = SimpleDocTemplate("reporte_pdf.pdf", pagesize=landscape(letter))

            # Generate the table
            table = Table(table_data)
            table.setTableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])

            # Add the table to the PDF
            doc.build([table])

            return response
    else:
        form = CashBoxForm()

    context = {
        'form': form,
    }

    return render(request, 'cajas/apertura/reporte_form.html', context)