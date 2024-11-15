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

try:
    latest_config = wompi_config.objects.latest('created_at')
    Client_id = latest_config.client_id
    Client_secret = latest_config.client_secret
except wompi_config.DoesNotExist:
    latest_config = None
    Client_id = None
    Client_secret = None
    # Puedes asignar valores predeterminados aquí si es necesario.

# Autenticarse y obtener el token
access_token = authenticate_wompi(Client_id, Client_secret)

def create_payment_link_reserva(reserva_id, client_id, client_secret, comercio_id, monto, nombre_producto, descripcion_producto, imagen, cantidad_prod, **kwargs):
    # Autenticar con Wompi
    #access_token = authenticate_wompi(client_id, client_secret)
    reserva_instance = get_object_or_404(Reserva, pk=reserva_id)
    
    if not access_token:
        return None

    try:
        # Obtener la instancia de Reserva

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
                "urlRedirect": "https://volcanosm.net",  # URL a la que se redirige después de realizar el pago
                "esMontoEditable": False,
                "esCantidadEditable": False,
                "cantidadPorDefecto": cantidad_prod,
                "emailsNotificacion": "correo@ejemplo.com",
            },    
            **kwargs
        }

        # Realizar la solicitud POST a Wompi para crear el enlace de pago
        response = requests.post("https://api.wompi.sv/EnlacePago", json=request_data, headers=get_wompi_headers(access_token))
        response.raise_for_status()
        payment_link_data = response.json()
        
        # Guardar información del enlace de pago en la base de datos
        # Almacenar la información del enlace de pago en la base de datos
        enlace_pago = EnlacePagoTour.objects.create(
            reserva = reserva_instance,
            comercio_id=comercio_id,
            monto=monto*cantidad_prod,
            nombre_producto=nombre_producto,
            url_qr_code=payment_link_data["urlQrCodeEnlace"],
            url_enlace=payment_link_data["urlEnlace"],
            esta_productivo=payment_link_data["estaProductivo"],
            descripcionProducto=descripcion_producto,
            imagenProducto=imagen,
            cantidad=cantidad_prod,
            idEnlace = payment_link_data["idEnlace"]
        )

    except requests.exceptions.RequestException as e:
        print(f"Error creating payment link: {e}")
        print(f"Response content: {e.response.content}")
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

def reservar_tour(request, tour_id):
    client_id = Client_id
    client_secret = Client_secret
        
    tour = get_object_or_404(Tour, pk=tour_id)
    
    tipo_document = Reserva.DOCUMENTOS_VALIDOS

    barra_principal = Barra_Principal.objects.latest('fecha_creacion') #obtener la barra principal
    data_contact = Contacts.objects.latest()#obtener todos los datos de contacto
    urls_info = Urls_info.objects.all() #obtener todas las url de informacion
    ultima_descripcion = General_Description.objects.latest('fecha_creacion') # Obtén la última descripción general
    urls_interes = Urls_interes.objects.all() #urls de interes  
    
    
    if request.method == 'POST':
        # Obtén los datos del formulario directamente del request.POST
        nombre = request.POST.get('nombre')
        dui = request.POST.get('dui')
        correo_electronico = request.POST.get('correo_electronico')
        direccion = request.POST.get('direccion')
        # Obtén los datos del formulario directamente de request.POST
        cantidad_adultos = int(request.POST.get('cantidad_adultos'))
        #cantidad_ninos = int(request.POST.get('cantidad_ninos'))
        fecha_reserva = request.POST.get('fecha_reserva')
        
        #nuevo campos agregados
        telefono = request.POST.get("telefono")
        pais_residencia = request.POST.get("pais_residencia")
        tipo_documento = request.POST.get("tipo_documento")
        
        # Obtener los precios de adulto y nino del tour
        precio_adulto = tour.precio_adulto
        precio_nino = tour.precio_nino

        reserva = Reserva(
            tour=tour,
            nombre=nombre,
            dui=dui,
            correo_electronico=correo_electronico,
            direccion=direccion,
            cantidad_adultos=cantidad_adultos,
            #cantidad_ninos=cantidad_ninos,
            fecha_reserva=fecha_reserva,
            precio_adulto=precio_adulto,
            precio_nino=precio_nino,
            telefono=telefono,
            pais_residencia=pais_residencia,
            tipo_documento=tipo_documento,
            estado_reserva = " ",
        )
        reserva.save()
        
        # Obtén la instancia de Reserva después de guardarla en la base de datos
        reserva_instance = Reserva.objects.get(pk=reserva.id)
        
        url_imagen_tour = tour.url_azure
        print("Esta es la url que obtengo  en depuracion: ",url_imagen_tour)

        # Asigna el valor de reserva_id después de obtener la instancia
        reserva_id = reserva_instance.id
        
        
        comercio_id = "Volcano SM Tours"
        monto = float(reserva.precio_adulto)
        nombre_producto = tour.titulo
        desc = unescape(str(tour.descripcion))
        desc = BeautifulSoup(str(tour.descripcion), "html.parser").get_text()
        imagenProducto = str(url_imagen_tour)
        cantidad = reserva.cantidad_adultos
        
        print(reserva_id, comercio_id, monto, nombre_producto, imagenProducto, cantidad)

        # Llama a la función para crear el enlace de pago
        enlace_pago = create_payment_link_reserva(
            reserva_id,
            client_id,
            client_secret,
            comercio_id,
            monto,
            nombre_producto,
            desc,
            imagenProducto,
            cantidad
            )
    
        # Redirige a la página de éxito y pasa el reserva_id como parámetro
        return redirect('reserva_exitosa', reserva_id=reserva.id)
    # Renderiza el formulario para el método GET
    
    context = {
        'barra_principal':barra_principal,
        'data_contact':data_contact,
        'urls_info':urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes':urls_interes,
        'tour': tour,
        'tipo_document':tipo_document,
        
    }
    
    return render(request, 'reservar_tour.html', context)


def reserva_exitosa(request, reserva_id):
    reserva = Reserva.objects.get(pk=reserva_id)
    enlace_pago = reserva.enlace_pago_set.get()
        #obtener todos los datos de contacto
    data_contact = Contacts.objects.latest()
    barra_principal = Barra_Principal.objects.latest('fecha_creacion') #obtener la barra principal
    data_contact = Contacts.objects.latest()#obtener todos los datos de contacto
    urls_info = Urls_info.objects.all() #obtener todas las url de informacion
    ultima_descripcion = General_Description.objects.latest('fecha_creacion') # Obtén la última descripción general
    urls_interes = Urls_interes.objects.all() #urls de interes
    
    
    context = {
        'barra_principal':barra_principal,
        'data_contact':data_contact,
        'urls_info':urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes':urls_interes,
        'reserva': reserva,
        'enlace_pago': enlace_pago,
    }

    return render(request, 'reserva_exitosa.html', context)


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


def actualizar_estado_reserva(request):
    '''Actualizar el estado de la reserva según las condiciones dadas.'''
    
    try:
        # Obtener la última reserva registrada
        ultima_reserva = Reserva.objects.latest('id')

        # Buscar enlace relacionado a la reserva
        enlace_pago = EnlacePagoTour.objects.filter(reserva=ultima_reserva).first()
        
        if ultima_reserva.estado_reserva != 'PAGADO':
            if enlace_pago:
                # Consultar la información del enlace de pago
                enlace_pago_info = consultar_enlace_pago(enlace_pago.idEnlace, Client_id, Client_secret)
                
                # Verificar si se encontró información del enlace de pago y si tiene transacciones
                if enlace_pago_info:
                    transacciones = enlace_pago_info.get('transaccionCompra')
                    if transacciones:
                        mensaje_transaccion = transacciones.get('mensaje')
                        fecha_transaccion = transacciones.get('fechaTransaccion')
                        
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
                else:
                    print("La reserva no fue pagada, no se encontró información de la transacción")
            else:
                print("No se encontró ningún enlace de pago asociado a la reserva")
        else:
            print("Reserva actualizada, el estado es: ", ultima_reserva.estado_reserva)

    except Reserva.DoesNotExist:
        print('No hay ninguna reserva registrada')

    ultima_reserva.save()

    # Devuelve una respuesta JSON
    return JsonResponse({'estado_reserva': ultima_reserva.estado_reserva})
