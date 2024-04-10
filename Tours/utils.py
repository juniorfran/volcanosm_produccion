from datetime import datetime, timedelta
import threading
import time
import schedule
from django.conf import settings
from Transacciones.models import EnlacePago
from Transacciones.wompi_connect import authenticate_wompi
from Transacciones.wompi_consulta import make_wompi_get_request
from .models import Reserva
#from Transacciones.views import consultar_enlace_pago

Client_id = settings.CLIENT_ID
Client_secret = settings.CLIENT_SECRET

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

def actualizar_estado(request):
    '''Actualizar el estado de la reserva según las condiciones dadas.'''
    
    try:
        # Obtener la última reserva registrada
        ultima_reserva = Reserva.objects.latest('id')

        # Buscar enlace relacionado a la reserva
        enlace_pago = EnlacePago.objects.filter(reserva=ultima_reserva).first()
        
        if ultima_reserva.estado_reserva != 'PAGADO':
            if enlace_pago:
                # Consultar la información del enlace de pago
                enlace_pago_info = consultar_enlace_pago(enlace_pago.idEnlace, Client_id, Client_secret)
                
                # Imprimir la información del enlace de pago para fines de depuración
                print("Información del Enlace de Pago:", enlace_pago_info)

                # Verificar si se encontró información del enlace de pago y si tiene transacciones
                if enlace_pago_info:
                    transacciones = enlace_pago_info.get('transaccionCompra')
                    if transacciones:
                        mensaje_transaccion = transacciones.get('mensaje')
                        fecha_transaccion = transacciones.get('fechaTransaccion')
                        # Imprimir la fecha de la transacción
                        print("Fecha de la transacción:", fecha_transaccion)
                        print("fecha de la ultima reserva: ", ultima_reserva.fecha_reserva)
                        
                        # Si el mensaje de la transacción es AUTORIZADO, el estado es PAGADO
                        if mensaje_transaccion == 'AUTORIZADO':
                            ultima_reserva.estado_reserva = 'PAGADO'
                        else:
                            # Si no es AUTORIZADO, pero hay una transacción, el estado es PENDIENTE
                            ultima_reserva.estado_reserva = 'PENDIENTE'
                            
                        fecha_ultima_reserva = str(ultima_reserva.fecha_reserva)

                        # Convertir la fecha de la transacción a un objeto datetime
                        fecha_transaccion_dt = datetime.fromisoformat(fecha_transaccion)
                        fecha_ultima_reserva_dt = datetime.fromisoformat(fecha_ultima_reserva)
                        
                        
                        # Verificar y actualizar el estado según el tiempo transcurrido
                        if ultima_reserva.estado_reserva == "RESERVADO":
                            fecha_reserva = ultima_reserva.fecha_reserva
                            if (datetime.now(tz=fecha_transaccion_dt.tzinfo) - fecha_transaccion_dt) > timedelta(minutes=5):
                                ultima_reserva.estado_reserva = 'PENDIENTE'
                        
                        # Cambiar a estado "CANCELADO" si la reserva ha estado en estado "RESERVADO" durante más de 24 horas
                        if ultima_reserva.estado_reserva == 'PENDIENTE':
                            fecha_reserva = ultima_reserva.fecha_reserva
                            if (datetime.now(tz=fecha_transaccion_dt.tzinfo) - fecha_transaccion_dt) > timedelta(minutes=25):
                                ultima_reserva.estado_reserva = 'CANCELADO'
                    else:
                        # Si no hay transacciones, establecer el estado como RESERVADO
                        ultima_reserva.estado_reserva = 'RESERVADO'
                        print("No se encontraron transacciones para el enlace de pago. La reserva se colocó como reservado.")
                else:
                    print("La reserva no fue pagada, no se encontró información de la transacción")
            else:
                print("No se encontró ningún enlace de pago asociado a la reserva")
        else:
            print("Reserva actualizada, el estado es: ", ultima_reserva.estado_reserva)

    except Reserva.DoesNotExist:
        print('No hay ninguna reserva registrada')

    ultima_reserva.save()


def actualizar_estado_reserva():
    # Obtener la última reserva registrada
    ultima_reserva = Reserva.objects.latest('id')
    while True:
        try:
            if Reserva.objects.exists():
                r = Reserva.objects.order_by('id').first()
                actualizar_estado(r)
                print("Actualizando estados...")
        except Exception as e:
            print("Error al actualizar estados:", str(e))
            
        time.sleep(10)
        
# Lanzar el hilo en el inicio del servidor
def start_background_thread():
    thread = threading.Thread(target=actualizar_estado_reserva)
    thread.daemon = True
    thread.start()
