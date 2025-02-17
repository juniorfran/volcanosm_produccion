from datetime import datetime, timedelta
from html import unescape
import uuid
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404, redirect, render
import requests
#from Transacciones.views import crear_enlace_pago
from Configuraciones.models import Barra_Principal, Contacts, Direccionamiento, General_Description, Urls_info, Urls_interes
from Servicios.models import Servicios
from Transacciones.wompi_connect import authenticate_wompi
from Transacciones.wompi_consulta import make_wompi_get_request
#from Transacciones.wompi_envio import create_payment_link
from django.conf import settings
from .models import ImagenTour, Resena, Tour, Reserva, EnlacePagoTour
from .forms import ResenaForm, ReservaForm
from django.utils import timezone
#from Transacciones.models import EnlacePago
from django.db.models import Q
from django.http import JsonResponse
from Configuraciones.models import wompi_config
from django.core.exceptions import ImproperlyConfigured


def get_wompi_config():
    try:
        config = wompi_config.objects.latest('created_at')
        return config
    except wompi_config.DoesNotExist:
        raise ImproperlyConfigured("No se encontro ninguna configuración de Wompi en la base de datos")

def create_payment_link_reserva(reserva_id, client_id, client_secret, comercio_id, monto, nombre_producto, descripcion_producto, imagen, cantidad_prod, **kwargs):
    """
    Crea un enlace de pago en Wompi para la reserva especificada.
    """
    try:
        # Obtener la configuración de Wompi
        wompi_config = get_wompi_config()
        Client_id = wompi_config.client_id
        Client_secret = wompi_config.client_secret

        # Autenticarse en Wompi
        access_token = authenticate_wompi(Client_id, Client_secret)
        if not access_token:
            print("Error: No se pudo autenticar en Wompi.")
            return None

        # Obtener la instancia de la reserva
        reserva_instance = get_object_or_404(Reserva, pk=reserva_id)

        # Construir la solicitud JSON
        request_data = {
            "identificadorEnlaceComercio": comercio_id,
            "monto": monto,
            "nombreProducto": nombre_producto,
            "infoProducto": {
                "descripcionProducto": descripcion_producto,
                "urlImagenProducto": imagen
            },
            "configuracion": {
                "urlRedirect": "https://volcanosm.net",  # URL a la que se redirige después del pago
                "esMontoEditable": False,
                "esCantidadEditable": False,
                "cantidadPorDefecto": cantidad_prod,
                "emailsNotificacion": "correo@ejemplo.com",
            },
            **kwargs
        }

        # Enviar la solicitud a Wompi
        response = requests.post("https://api.wompi.sv/EnlacePago", json=request_data, headers=get_wompi_headers(access_token))

        # Manejar errores en la respuesta
        if response.status_code != 200:
            print(f"Error al crear el enlace de pago: {response.status_code} - {response.text}")
            return None

        payment_link_data = response.json()

        # Verificar si los datos esperados están en la respuesta
        if not all(k in payment_link_data for k in ["urlQrCodeEnlace", "urlEnlace", "idEnlace"]):
            print(f"Respuesta inesperada de Wompi: {payment_link_data}")
            return None

        # Crear y guardar el enlace de pago en la base de datos
        enlace_pago = EnlacePagoTour.objects.create(
            reserva=reserva_instance,
            comercio_id=comercio_id,
            monto=monto * cantidad_prod,
            nombre_producto=nombre_producto,
            url_qr_code=payment_link_data["urlQrCodeEnlace"],
            url_enlace=payment_link_data["urlEnlace"],
            esta_productivo=payment_link_data.get("estaProductivo", False),
            descripcionProducto=descripcion_producto,
            imagenProducto=imagen,
            cantidad=cantidad_prod,
            idEnlace=payment_link_data["idEnlace"]
        )

        return enlace_pago.url_enlace  # Retornar el enlace de pago

    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud a Wompi: {e}")
        return None
    

def get_wompi_headers(access_token):
    return {
        "content-type": "application/json",
        "authorization": f"Bearer {access_token}"
    }

        
def tours_index(request):
    # Obtener la fecha actual
    fecha_actual = timezone.now()

    # Obtener todos los tours desde la base de datos
    tours = Tour.objects.all()

    # Verificar la disponibilidad de cada tour
    for tour in tours:
        if tour.fecha_inicio <= fecha_actual <= tour.fecha_fin:
            tour.disponible = True
        else:
            tour.disponible = False
            
    titulo = "Nuestros Tours"
    direccion_actual = "tours"

    barra_principal = Barra_Principal.objects.latest('fecha_creacion') # Obtener la barra principal
    data_contact = Contacts.objects.latest() # Obtener todos los datos de contacto
    urls_info = Urls_info.objects.all() # Obtener todas las URL de información
    ultima_descripcion = General_Description.objects.latest('fecha_creacion') # Obtener la última descripción general
    urls_interes = Urls_interes.objects.all() # URLs de interés
    conf_direccionamiento = Direccionamiento.objects.latest('fecha_creacion')
    servicio = Servicios.objects.first()
    

    # Renderizar la plantilla 'show_tours.html' con la lista de tours y otros datos
    context = {
        'servicio': servicio,
        'titulo':titulo,
        'direccion_actual':direccion_actual,
        'tours': tours,
        'barra_principal': barra_principal,
        'data_contact': data_contact,
        'urls_info': urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes': urls_interes,
        'direccionamiento':conf_direccionamiento,
    }
    return render(request, 'show_tours.html', context)

def tour_detail(request, tour_id):
    tour = Tour.objects.get(pk=tour_id)
    barra_principal = Barra_Principal.objects.latest('fecha_creacion')
    resenas = Resena.objects.filter(tour=tour)
    data_contact = Contacts.objects.latest()
    urls_info = Urls_info.objects.all()
    ultima_descripcion = General_Description.objects.latest('fecha_creacion')
    urls_interes = Urls_interes.objects.all()
    conf_direccionamiento = Direccionamiento.objects.latest('fecha_creacion')

    # Crear una lista con todas las imágenes relacionadas, incluida la principal
    imagenes = [tour.url_azure] + [getattr(imagen_tour, f'url_azure_{i}') for i in range(1, 5) for imagen_tour in ImagenTour.objects.filter(tour=tour)]
    
    titulo = "Nuestros Tours"
    direccion_actual = f"tour/{tour.pk}"

    if request.method == 'POST':
        estrellas = int(request.POST.get('rating'))
        comentario = request.POST.get('comentario')

        if estrellas < 1 or estrellas > 5:
            return redirect('tour_detail', tour_id=tour_id)

        resena = Resena.objects.create(tour=tour, estrellas=estrellas, comentario=comentario)
        return redirect('tour_detail', tour_id=tour_id)
    
    context = {
        'tour': tour,
        'imagenes': imagenes,
        'resenas': resenas,
        'barra_principal': barra_principal,
        'data_contact': data_contact,
        'urls_info': urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes': urls_interes,
        'titulo':titulo,
        'direccion_actual':direccion_actual,
        'direccionamiento':conf_direccionamiento,
    }

    return render(request, 'detail_tours.html', context)

from django.db import transaction

def reservar_tour(request, tour_id):
    """
    Permite a un usuario reservar un tour y generar un enlace de pago en Wompi.
    Si ya existe una reserva sin enlace de pago, se genera uno nuevo y se actualiza.
    """

    wompi_config = get_wompi_config()
    client_id = wompi_config.client_id
    client_secret = wompi_config.client_secret

    tour = get_object_or_404(Tour, pk=tour_id)
    tipo_document = Reserva.DOCUMENTOS_VALIDOS

    barra_principal = Barra_Principal.objects.latest('fecha_creacion')
    data_contact = Contacts.objects.latest()
    urls_info = Urls_info.objects.all()
    ultima_descripcion = General_Description.objects.latest('fecha_creacion')
    urls_interes = Urls_interes.objects.all()

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        dui = request.POST.get('dui')
        correo_electronico = request.POST.get('correo_electronico')
        direccion = request.POST.get('direccion')
        cantidad_adultos = int(request.POST.get('cantidad_adultos'))
        fecha_reserva = request.POST.get('fecha_reserva')
        telefono = request.POST.get("telefono")
        pais_residencia = request.POST.get("pais_residencia")
        tipo_documento = request.POST.get("tipo_documento")

        with transaction.atomic():
            # Buscar si ya existe una reserva con los mismos datos
            reserva = Reserva.objects.filter(
                correo_electronico=correo_electronico,
                tour=tour,
                fecha_reserva=fecha_reserva
            ).first()

            # Si la reserva ya existe
            if reserva:
                # Buscar si tiene un enlace de pago asociado
                enlace_pago = EnlacePagoTour.objects.filter(reserva=reserva).first()

                if enlace_pago and enlace_pago.url_enlace:
                    # Si ya tiene un enlace de pago, redirigir directamente
                    return redirect('reserva_exitosa', reserva_id=reserva.id)
                else:
                    # Si no tiene enlace de pago, generar uno nuevo y actualizar
                    enlace_pago_url = create_payment_link_reserva(
                        reserva.id,
                        client_id,
                        client_secret,
                        "Volcano SM Tours",
                        float(reserva.precio_adulto),
                        tour.titulo,
                        BeautifulSoup(str(tour.descripcion), "html.parser").get_text(),
                        tour.url_azure,
                        reserva.cantidad_adultos
                    )

                    if enlace_pago_url:
                        # Crear o actualizar el enlace de pago en la base de datos
                        enlace_pago, created = EnlacePagoTour.objects.update_or_create(
                            reserva=reserva,
                            defaults={
                                'url_enlace': enlace_pago_url,
                                'esta_productivo': True
                            }
                        )

                        # Redirigir a la página de éxito
                        return redirect('reserva_exitosa', reserva_id=reserva.id)
                    else:
                        return JsonResponse({'error': 'No se pudo generar el enlace de pago'}, status=500)

            # Si la reserva no existe, crear una nueva
            reserva = Reserva.objects.create(
                tour=tour,
                nombre=nombre,
                dui=dui,
                correo_electronico=correo_electronico,
                direccion=direccion,
                cantidad_adultos=cantidad_adultos,
                fecha_reserva=fecha_reserva,
                precio_adulto=tour.precio_adulto,
                precio_nino=tour.precio_nino,
                telefono=telefono,
                pais_residencia=pais_residencia,
                tipo_documento=tipo_documento,
                estado_reserva="PENDIENTE",
            )

            # Generar el enlace de pago para la nueva reserva
            enlace_pago_url = create_payment_link_reserva(
                reserva.id,
                client_id,
                client_secret,
                "Volcano SM Tours",
                float(reserva.precio_adulto),
                tour.titulo,
                BeautifulSoup(str(tour.descripcion), "html.parser").get_text(),
                tour.url_azure,
                reserva.cantidad_adultos
            )

            if enlace_pago_url:
                # Guardar el nuevo enlace de pago en la base de datos
                EnlacePagoTour.objects.create(
                    reserva=reserva,
                    url_enlace=enlace_pago_url,
                    esta_productivo=True
                )

                # Redirigir a la página de éxito
                return redirect('reserva_exitosa', reserva_id=reserva.id)
            else:
                return JsonResponse({'error': 'No se pudo generar el enlace de pago'}, status=500)

    # Renderizar el formulario
    context = {
        'barra_principal': barra_principal,
        'data_contact': data_contact,
        'urls_info': urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes': urls_interes,
        'tour': tour,
        'tipo_document': tipo_document,
    }

    return render(request, 'reservar_tour.html', context)



def reserva_exitosa(request, reserva_id):
    """
    Muestra la página de reserva exitosa con la opción de pagar si aún no está pagado.
    """
    reserva = get_object_or_404(Reserva, pk=reserva_id)
    
    # Obtener el enlace de pago asociado a la reserva
    #enlace_pago = EnlacePagoTour.objects.filter(reserva=reserva).first()
    enlace_pago = reserva.enlace_pago_set.first()
    print("Enlace de Pago Obtenido:", enlace_pago)
    print("URL de Enlace:", enlace_pago.url_enlace if enlace_pago else "No hay enlace")
    print("ID de Enlace:", enlace_pago.idEnlace if enlace_pago else "No hay ID")

    # # Verificar si existe el enlace de pago y es válido
    # if enlace_pago:
    #     try:
    #         response = requests.head(enlace_pago.url_enlace, timeout=5)
    #         if response.status_code != 200:
    #             enlace_pago = None  # Si el enlace no es válido, establece None
    #     except requests.RequestException:
    #         enlace_pago = None
    # else:
    #     enlace_pago = None  # Si no existe, establece None

    # Obtener otros datos necesarios para la plantilla
    data_contact = Contacts.objects.latest()
    barra_principal = Barra_Principal.objects.latest('fecha_creacion')
    urls_info = Urls_info.objects.all()
    ultima_descripcion = General_Description.objects.latest('fecha_creacion')
    urls_interes = Urls_interes.objects.all()

    context = {
        'barra_principal': barra_principal,
        'data_contact': data_contact,
        'urls_info': urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes': urls_interes,
        'reserva': reserva,
        'enlace_pago': enlace_pago  # Pasa el enlace de pago a la plantilla
    }

    return render(request, 'reserva_exitosa.html', context)


# def reserva_exitosa1(request, reserva_id):
#     reserva = get_object_or_404(Reserva, pk=reserva_id)

#     # Obtener el enlace de pago asociado a la reserva
#     enlace_pago = EnlacePagoTour.objects.filter(reserva=reserva).first()

#     # Debugging: Verifica si el objeto `enlace_pago` tiene datos antes de enviarlo a la plantilla
#     print("🔹 Enlace de Pago:", enlace_pago)
#     if enlace_pago:
#         print("🔹 ID Enlace:", enlace_pago.idEnlace)
#         print("🔹 URL Enlace:", enlace_pago.url_enlace)
#         print("🔹 URL QR Code:", enlace_pago.url_qr_code)
#     else:
#         print("⚠ No se encontró un enlace de pago.")

#     data_contact = Contacts.objects.latest()
#     barra_principal = Barra_Principal.objects.latest('fecha_creacion')
#     urls_info = Urls_info.objects.all()
#     ultima_descripcion = General_Description.objects.latest('fecha_creacion')
#     urls_interes = Urls_interes.objects.all()

#     # Pasamos los datos a la plantilla
#     context = {
#         'barra_principal': barra_principal,
#         'data_contact': data_contact,
#         'urls_info': urls_info,
#         'ultima_descripcion': ultima_descripcion,
#         'urls_interes': urls_interes,
#         'reserva': reserva,
#         'enlace_pago': enlace_pago  # Asegúrate de que esto se envía
#     }

#     return render(request, 'reserva_exi.html', context)

def consultar_enlace_pago(enlace_pago_id, client_id, client_secret):

    # Cargar la configuración de Wompi
    wompi_config = get_wompi_config()
    client_id = wompi_config.client_id
    client_secret = wompi_config.client_secret

    # Autenticarse y obtener el token
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


from datetime import datetime, timedelta

def actualizar_estado_reserva(request, reserva_id):
    """
    Actualiza el estado de la reserva basada en la transacción de pago en Wompi.
    Recibe el ID de la reserva como parámetro en la URL.
    """

    # Cargar la configuración de Wompi
    wompi_configuracion = get_wompi_config()
    Client_id = wompi_configuracion.client_id
    Client_secret = wompi_configuracion.client_secret

    # Autenticarse en Wompi
    access_token = authenticate_wompi(Client_id, Client_secret)
    if not access_token:
        return JsonResponse({'error': 'No se pudo autenticar en Wompi'}, status=500)

    # Obtener la reserva específica
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Buscar el enlace de pago asociado a la reserva
    enlace_pago = EnlacePagoTour.objects.filter(reserva=reserva).first()
    if not enlace_pago:
        return JsonResponse({'error': 'No se encontró un enlace de pago asociado'}, status=404)

    # No actualizar si ya está pagado
    if reserva.estado_reserva == 'PAGADO':
        return JsonResponse({'estado_reserva': reserva.estado_reserva, 'mensaje': 'Reserva ya pagada'})

    # Consultar el estado del pago en Wompi
    enlace_pago_info = consultar_enlace_pago(enlace_pago.idEnlace, Client_id, Client_secret)
    if not isinstance(enlace_pago_info, dict):
        return JsonResponse({'error': 'No se pudo obtener información del enlace de pago'}, status=400)

    # Verificar si 'transaccionCompra' existe y tiene datos
    transacciones = enlace_pago_info.get('transaccionCompra')
    if transacciones is None:
        return JsonResponse({'estado_reserva': reserva.estado_reserva, 'mensaje': 'No hay transacción asociada'}, status=200)

    mensaje_transaccion = transacciones.get('mensaje', 'PENDIENTE')
    fecha_transaccion = transacciones.get('fechaTransaccion')

    # Actualizar estado basado en la respuesta de Wompi
    if mensaje_transaccion == 'AUTORIZADO':
        reserva.estado_reserva = 'PAGADO'
    else:
        reserva.estado_reserva = 'PENDIENTE'

    # Manejar tiempos de expiración del pago
    if fecha_transaccion:
        try:
            fecha_transaccion_dt = datetime.fromisoformat(fecha_transaccion)
        except ValueError:
            return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)

        tiempo_transcurrido = datetime.now(tz=fecha_transaccion_dt.tzinfo) - fecha_transaccion_dt

        # Si han pasado más de 5 minutos, marcar como PENDIENTE
        if tiempo_transcurrido > timedelta(minutes=5):
            reserva.estado_reserva = 'PENDIENTE'

        # Si han pasado más de 24 horas y sigue pendiente, marcar como CANCELADO
        if reserva.estado_reserva == 'PENDIENTE' and tiempo_transcurrido > timedelta(hours=24):
            reserva.estado_reserva = 'CANCELADO'

    # Guardar la actualización en la base de datos
    reserva.save()

    return JsonResponse({'estado_reserva': reserva.estado_reserva, 'reserva_id': reserva.id})
