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

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max
from django.core.exceptions import FieldError



def tours_index(request):
    now = timezone.now()

    # Base queryset
    tours_qs = Tour.objects.all()

    # ---- Filtros GET ----
    q = (request.GET.get('q') or '').strip()
    tipo = (request.GET.get('tipo') or '').strip()           # si es FK vendrá un id en str
    duracion_range = (request.GET.get('duracion') or '').strip()
    solo_finde = request.GET.get('solo_finde')
    orden = (request.GET.get('orden') or '').strip()
    precio_param = request.GET.get('precio')

    # Buscador (intenta FK.nombre y cae a campos de texto)
    if q:
        try:
            tours_qs = tours_qs.filter(
                Q(titulo__icontains=q) |
                Q(descripcion__icontains=q) |
                Q(tipo_tour__nombre__icontains=q) |   # si es FK con campo nombre
                Q(tipo_tour__icontains=q)             # si fuera CharField
            )
        except FieldError:
            tours_qs = tours_qs.filter(
                Q(titulo__icontains=q) |
                Q(descripcion__icontains=q)
            )

    # Filtro por tipo (si es FK, usa _id; si fuera Char, igual funciona porque value es el mismo)
    if tipo:
        try:
            tipo_id = int(tipo)
            tours_qs = tours_qs.filter(tipo_tour_id=tipo_id)
        except ValueError:
            # Si llegó texto (para CharField):
            tours_qs = tours_qs.filter(tipo_tour=tipo)

    # Filtro rango duración
    if duracion_range:
        try:
            lo, hi = map(int, duracion_range.split('-'))
            tours_qs = tours_qs.filter(duracion__gte=lo, duracion__lte=hi)
        except Exception:
            pass

    # Solo fines de semana
    if solo_finde:
        tours_qs = tours_qs.filter(solo_finde=True)

    # ---- Precio máx dinámico (antes de aplicar filtro por precio) ----
    agg = tours_qs.aggregate(precio_max=Max('precio_adulto'))
    precio_max = int(agg['precio_max']) if agg['precio_max'] is not None else 300

    try:
        precio_val = int(float(precio_param)) if precio_param is not None else precio_max
    except (TypeError, ValueError):
        precio_val = precio_max

    precio_val = max(0, min(precio_val, precio_max))
    tours_qs = tours_qs.filter(precio_adulto__lte=precio_val)

    # ---- Orden ----
    order_map = {
        'precio': 'precio_adulto',
        '-precio': '-precio_adulto',
        'duracion': 'duracion',
        '-duracion': '-duracion',
    }
    if orden in order_map:
        tours_qs = tours_qs.order_by(order_map[orden])

    # Marca disponibilidad sin tocar BD
    tours = list(tours_qs)
    for t in tours:
        if getattr(t, 'fecha_inicio', None) and getattr(t, 'fecha_fin', None):
            t.disponible = (t.fecha_inicio <= now <= t.fecha_fin)
        else:
            t.disponible = False

    # ---- Opciones de "tipo" para el <select> (soporta FK o CharField) ----
    try:
        # Si es FK con campo "nombre"
        tipos_pairs = (
            Tour.objects.filter(tipo_tour__isnull=False)
                        .values_list('tipo_tour__id', 'tipo_tour__nombre')
                        .distinct()
        )
        tipos = list(tipos_pairs)
    except FieldError:
        # Si es CharField
        tipos_vals = (
            Tour.objects.exclude(tipo_tour__isnull=True)
                        .exclude(tipo_tour='')       # aquí sí es seguro: es CharField
                        .values_list('tipo_tour', flat=True)
                        .distinct()
        )
        tipos = [(v, v) for v in tipos_vals]

    # Paginación
    paginator = Paginator(tours, 9)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Datos globales
    titulo = "Nuestros Tours"
    direccion_actual = "tours"
    barra_principal = Barra_Principal.objects.latest('fecha_creacion')
    data_contact = Contacts.objects.latest()
    urls_info = Urls_info.objects.all()
    ultima_descripcion = General_Description.objects.latest('fecha_creacion')
    urls_interes = Urls_interes.objects.all()
    conf_direccionamiento = Direccionamiento.objects.latest('fecha_creacion')
    servicio = Servicios.objects.first()

    # Imagen header opcional
    header_bg = None
    if hasattr(conf_direccionamiento, 'imagen_principal') and getattr(conf_direccionamiento, 'imagen_principal'):
        img = getattr(conf_direccionamiento, 'imagen_principal')
        header_bg = getattr(img, 'url', None)
    elif hasattr(conf_direccionamiento, 'url_azure'):
        header_bg = conf_direccionamiento.url_azure

    context = {
        'servicio': servicio,
        'titulo': titulo,
        'direccion_actual': direccion_actual,

        'tours': page_obj.object_list,
        'is_paginated': page_obj.paginator.num_pages > 1,
        'page_obj': page_obj,
        'paginator': paginator,

        'barra_principal': barra_principal,
        'data_contact': data_contact,
        'urls_info': urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes': urls_interes,
        'direccionamiento': conf_direccionamiento,

        # UI / Filtros
        'tipos': tipos,
        'precio_max': precio_max,
        'precio_val': precio_val,
        'header_bg': header_bg,
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

def get_wompi_config():
    try:
        config = wompi_config.objects.latest('created_at')
        return config
    except wompi_config.DoesNotExist:
        raise ImproperlyConfigured("No se encontro ninguna configuración de Wompi en la base de datos")

def create_payment_link_reserva(reserva_id, client_id, client_secret, comercio_id, monto, nombre_producto, descripcion_producto, imagen, cantidad_prod, url_redir, **kwargs):
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

        #urlRedirect es la url de reserva_exitosa/id_reserva
        #url_redir = f"https://volcanosm.com/tours/reserva_exitosa/{reserva_instance.reserva.id}/",

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
                "urlRedirect": url_redir,  # URL a la que se redirige después del pago
                "esMontoEditable": False,
                "esCantidadEditable": False,
                "cantidadPorDefecto": cantidad_prod,
                "emailsNotificacion": reserva_instance.correo_electronico,
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

from django.db import transaction

def reservar_tour(request, tour_id):
    """
    Permite a un usuario reservar un tour y genera un nuevo enlace de pago en Wompi.
    No verifica reservas previas, permitiendo múltiples reservas sin restricciones.
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
            # Crear la reserva
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

            # Generar el enlace de pago con Wompi
            enlace_pago_data = create_payment_link_reserva(
                reserva.id,                                # reserva_id
                client_id,                                 # client_id
                client_secret,                             # client_secret
                "Volcano SM Tours",                        # comercio_id
                float(reserva.precio_adulto),              # monto
                tour.titulo,                               # nombre_producto
                BeautifulSoup(str(tour.descripcion), "html.parser").get_text(),  # descripcion_producto
                tour.url_azure,                            # imagen
                cantidad_adultos,                          # cantidad_prod
                url_redir = f"https://volcanosm.com/tours/reserva_exitosa/{reserva.id}/",
                emailsNotificacion=reserva.correo_electronico
            )

            print(f"🔍 Respuesta completa de Wompi: {enlace_pago_data}")  # Log para depuración

        # Redirigir a la página de éxito
        return redirect('reserva_exitosa', reserva_id=reserva.id)
                
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

        transaccion = enlace_pago_info.get('transaccionCompra', {})
        mensaje_transaccion = transaccion.get('mensaje', 'AUTORIZADO')
        print(mensaje_transaccion)

        return enlace_pago_info
    else:
        print("Error al obtener información del enlace de pago.")
        return None


from datetime import datetime, timedelta

def actualizar_estado_reserva(request, reserva_id):
    """
    Actualiza el estado de la reserva basada en la transacción de pago en Wompi.
    """

    # 1️⃣ Autenticarse en Wompi
    wompi_configuracion = get_wompi_config()
    client_id = wompi_configuracion.client_id
    client_secret = wompi_configuracion.client_secret

    access_token = authenticate_wompi(client_id, client_secret)
    if not access_token:
        return JsonResponse({'error': 'No se pudo autenticar en Wompi'}, status=500)

    # 2️⃣ Obtener la reserva específica
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # 3️⃣ Buscar el enlace de pago asociado a la reserva
    enlace_pago = EnlacePagoTour.objects.filter(reserva=reserva).first()
    if not enlace_pago:
        return JsonResponse({'error': 'No se encontró un enlace de pago asociado'}, status=404)

    # Si la reserva ya está pagada, no hacemos nada
    if reserva.estado_reserva == 'PAGADO':
        return JsonResponse({'estado_reserva': reserva.estado_reserva, 'mensaje': 'Reserva ya pagada'})

    print(f"Estado actual en BD antes de consulta: {reserva.estado_reserva}")

    # 4️⃣ Consultar el estado del pago en Wompi
    enlace_pago_info = make_wompi_get_request(f"EnlacePago/{enlace_pago.idEnlace}", access_token)
    if not isinstance(enlace_pago_info, dict):
        return JsonResponse({'error': 'No se pudo obtener información del enlace de pago'}, status=400)

    # 5️⃣ Extraer transacción si existe
    transaccion = enlace_pago_info.get('transaccionCompra')

    if transaccion:  # Si la transacción existe
        mensaje_transaccion = transaccion.get('mensaje', 'PENDIENTE')
        fecha_transaccion = transaccion.get('fechaTransaccion')
    else:
        mensaje_transaccion = 'PENDIENTE'
        fecha_transaccion = None

    print(f"Estado recibido de Wompi: {mensaje_transaccion}")

    # Actualizar estado basado en la respuesta de Wompi
    if mensaje_transaccion.upper() == 'AUTORIZADO':
        Reserva.objects.filter(id=reserva.id).update(estado_reserva='PAGADO')
        #enviar el detalle de la reserva por correo
        reserva.enviar_codigo_por_correo()
    else:
        Reserva.objects.filter(id=reserva.id).update(estado_reserva='PENDIENTE')

    # Volver a obtener el objeto actualizado
    reserva.refresh_from_db()

    print(f"Estado actualizado en BD después de la consulta: {reserva.estado_reserva}")

    return JsonResponse({'estado_reserva': reserva.estado_reserva, 'reserva_id': reserva.id})
