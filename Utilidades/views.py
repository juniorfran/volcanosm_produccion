from django.shortcuts import render
from Transacciones.wompi_connect import authenticate_wompi
from Transacciones.wompi_consulta import make_wompi_get_request
from Transacciones.wompi_envio import create_payment_link
from Tours.models import ImagenTour, Resena, Tour, Reserva
from Transacciones.models import EnlacePago
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required

Client_id = settings.CLIENT_ID
Client_secret = settings.CLIENT_SECRET

@login_required
def index_utilidades(request):
    
    return render(request, 'base_utilities.html')

@login_required
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
    