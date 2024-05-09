from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from Transacciones.wompi_connect import authenticate_wompi
from Transacciones.wompi_consulta import make_wompi_get_request
from Transacciones.wompi_envio import create_payment_link
from Tours.models import ImagenTour, Resena, Tour, Reserva
from Tours.models import EnlacePagoTour
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from Internet.models import Accesos, Tipos
import csv
import pandas as pd

Client_id = settings.CLIENT_ID
Client_secret = settings.CLIENT_SECRET

@login_required
def index_utilidades(request):
    
    return render(request, 'base_utilities.html')


def consultar_enlace_pago(enlace_pago_id, client_id, client_secret):
    # Autenticar con Wompi y obtener el token
    access_token = authenticate_wompi(client_id, client_secret)

    if not access_token:
        print("Error de autenticación con Wompi.")
        return None

    # Utilizar la función make_wompi_get_request para realizar la solicitud GET
    endpoint = f"EnlacePago/{enlace_pago_id}"
    enlace_pago_info = make_wompi_get_request(endpoint, access_token)

    if enlace_pago_info:
        # Imprimir la información del enlace de pago
        print("Información del enlace de pago:")
        print(enlace_pago_info)
        return enlace_pago_info
    else:
        print("Error al obtener información del enlace de pago.")
        return None

# Ejemplo de uso
# enlace_pago_id = "1072404"
# consultar_enlace_pago(enlace_pago_id, Client_id, Client_secret)


@login_required
def consultar_detalle (request):
    user = request.user
    if request.method == 'POST':
        
        numero_reserva = request.POST.get('numero_reserva')
        try:
            # Filtrar las reservas que coinciden con los últimos 4 dígitos
            reservas = Reserva.objects.filter(
                Q(codigo_reserva__endswith=numero_reserva) |
                Q(codigo_reserva=numero_reserva)
            )

            if reservas.exists():
                # Tomar la primera reserva encontrada
                reserva = reservas.first()

                # Buscar enlace relacionado a la reserva
                enlace_pago = EnlacePago.objects.filter(reserva=reserva).first()

                # Si se encuentra un enlace, consultar la información
                if enlace_pago:
                    enlace_pago_info = consultar_enlace_pago(enlace_pago.idEnlace, Client_id, Client_secret)
                    if enlace_pago_info:
                        return render(request, 'detalle.html', {'enlace_pago': enlace_pago_info, 'reserva': reserva})
                    else:
                        return render(request, 'detalle.html', {'error_message': 'Error al obtener información del enlace de pago.'})
                else:
                    return render(request, 'detalle.html', {'error_message': 'No se encontró un enlace de pago para la reserva.'})
            else:
                return render(request, 'detalle.html', {'error_message': 'Reserva no encontrada.'})

        except Reserva.DoesNotExist:
            return render(request, 'detalle.html', {'error_message': 'Enlace de pago no encontrada.'})
    else:
        return render(request, 'detalle.html', {})

def upload_data(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        if file.name.endswith('.csv'):
            data = csv.DictReader(file.read().decode('utf-8').splitlines())
        elif file.name.endswith('.xlsx'):
            data = pd.read_excel(file)
            data = data.to_dict('records')
        else:
            messages.error(request, 'Formato de archivo no válido. Solo se admiten archivos CSV o Excel.')
            return redirect('upload_data')
        
        for row in data:
            tipo_acceso_id = row.get('tipo_acceso_id')  # Obtener el ID del tipo de acceso
            tipo_acceso_instance = Tipos.objects.get(id=tipo_acceso_id)  # Obtener la instancia del tipo de acceso
            
            acceso = Accesos(
                usuario=row.get('usuario'),
                password=row.get('password'),
                descripcion=row.get('descripcion'),
                cant_usuarios=row.get('cant_usuarios'),
                acceso_tipo=tipo_acceso_instance,  # Asignar la instancia del tipo de acceso
                fecha_expiracion=row.get('fecha_expiracion'),
                estado=row.get('estado')
            )
            acceso.save()
        
        messages.success(request, 'Los datos se han cargado correctamente.')
        return redirect('utilidades:upload_data')
    return render(request, 'internet/upload_data.html')

