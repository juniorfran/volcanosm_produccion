from django.utils import timezone
from datetime import datetime, timedelta
import json
from django.shortcuts import get_object_or_404, redirect, render
import requests
from .models import EnlacePagoAcceso, Accesos, Tipos, Clientes, TransaccionCompra, Transaccion3DS, Transaccion3DS_Respuesta, TransaccionCompra3DS
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from Configuraciones.models import Barra_Principal, Contacts, Direccionamiento, General_Description, Urls_info, Urls_interes
from django.db import transaction

from Transacciones.wompi_connect import authenticate_wompi
from Transacciones.wompi_consulta import make_wompi_get_request
from Transacciones.wompi_envio import create_payment_link

from azure.communication.email import EmailClient
from django.conf import settings
import qrcode
from io import BytesIO
from django.template.loader import render_to_string
from django.utils.html import strip_tags
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

def crear_transaccion_3ds(acceso_id, numeroTarjeta, cvv, mesVencimiento, anioVencimiento, monto, nombre, apellido, email, ciudad, direccion, telefono, client_id, client_secret, **kwargs):
    access_token = authenticate_wompi(client_id, client_secret)
    acceso_instance = get_object_or_404(Accesos, pk=acceso_id)
    
    if not access_token:
        print("Error: No se pudo obtener el token de acceso")
        return None
    
    try:
        # Construir la solicitud JSON
        request_data = {
            "tarjetaCreditoDebido": {
                "numeroTarjeta": numeroTarjeta,
                "cvv": cvv,
                "mesVencimiento": mesVencimiento,
                "anioVencimiento": anioVencimiento
            },
            "monto": monto,
            "urlRedirect": "https://volcanosm.net/internet",
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "ciudad": ciudad,
            "direccion": direccion,
            "idPais": "SV",
            "idRegion": "SV-SM",
            "codigoPostal": "2401",
            "telefono": telefono,
            **kwargs
        }
        # Log request data
        print("Request Data:", request_data)
        
        # Realizar la solicitud POST para la transacción 3DS
        response = requests.post("https://api.wompi.sv/TransaccionCompra/3Ds", json=request_data, headers=get_wompi_headers(access_token))
        response.raise_for_status()
        transaccion_data = response.json()
        
        # Log response status and content
        print("Response Status Code:", response.status_code)
        if response.content:
            print("Response Content:", response.content)
        else:
            print("Response content is empty")
        
        # Guardar la información de la transacción en la base de datos
        transaccion3ds = Transaccion3DS.objects.create(
            #cliente=get_object_or_404(Clientes, pk=client_id),  # Asumiendo que `client_id` es el ID del cliente
            acceso=acceso_instance,
            numeroTarjeta=numeroTarjeta,
            mesVencimiento=mesVencimiento,
            anioVencimiento=anioVencimiento,
            cvv=cvv,
            monto=monto,
            nombre=nombre,
            apellido=apellido,
            email=email,
            ciudad=ciudad,
            direccion=direccion,
            telefono=telefono,
            estado=True
        )
        
        transaccion3ds_respuesta = Transaccion3DS_Respuesta.objects.create(
            transaccion3ds=transaccion3ds,
            idTransaccion=transaccion_data["idTransaccion"],
            esReal=transaccion_data["esReal"],
            urlCompletarPago3Ds=transaccion_data["urlCompletarPago3Ds"],
            monto=transaccion_data["monto"]
        )
        
        return transaccion_data
    
    
    
    except requests.exceptions.RequestException as e:
        print(f"Error during POST request: {e}")
        if e.response is not None:
            if e.response.content:
                print(f"Response content: {e.response.content}")
            else:
                print("Error: Response content is empty")
        return None


def create_payment_link_acceso(acceso_id, client_id, client_secret, comercio_id, monto, nombre_producto, descripcion_Producto, imagenProducto, cantidad, **kwargs):
    # Autenticar con Wompi
    access_token = authenticate_wompi(client_id, client_secret)
    acceso_instance = get_object_or_404(Accesos, pk=acceso_id)
    
    if not access_token:
        return None

    try:
        # Obtener la instancia de Reserva

        # Construir la solicitud JSON
        request_data = {
            "identificadorEnlaceComercio": comercio_id,
            "monto": monto,
            "nombreProducto": nombre_producto,
            # "descripcionProducto":descripcion_Producto,
            # "urlImagenProducto": imagenProducto,
            # "cantidadPorDefecto": cantidad,
            "infoProducto": {
                    "descripcionProducto": descripcion_Producto,
                    "urlImagenProducto": imagenProducto
                },
            "configuracion": {
                "urlRedirect": "https://volcanosm.net",  # URL a la que se redirige después de realizar el pago
                "esMontoEditable": False,
                "esCantidadEditable": False,
                "cantidadPorDefecto": cantidad,
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
        enlace_pago = EnlacePagoAcceso.objects.create(
            acceso=acceso_instance,
            comercio_id=comercio_id,
            monto=monto*cantidad,
            nombre_producto=nombre_producto,
            url_qr_code=payment_link_data["urlQrCodeEnlace"],
            url_enlace=payment_link_data["urlEnlace"],
            esta_productivo=payment_link_data["estaProductivo"],
            descripcionProducto=descripcion_Producto,
            imagenProducto=imagenProducto,
            cantidad=cantidad,
            idEnlace = payment_link_data["idEnlace"]
        )

    except requests.exceptions.RequestException as e:
        print(f"Error creating payment link: {e}")
        print(f"Response content: {e.response.content}")
        return None



def get_wompi_headers(access_token):
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

def servicio_inter_index(request):
    
    barra_principal = Barra_Principal.objects.latest('fecha_creacion')
    data_contact = Contacts.objects.latest()
    urls_info = Urls_info.objects.all()
    ultima_descripcion = General_Description.objects.latest('fecha_creacion')
    urls_interes = Urls_interes.objects.all()
    
    #obtener fecha actual
    fecha_actual = timezone.now()
    
    #obtener todos los tipos de accesos desde la base de datos
    tipos_accesos = Tipos.objects.all()
    
    for tipo in tipos_accesos:
        if tipo.fecha_inicio <= fecha_actual <= tipo.fecha_fin:
            tipo.disponible = True
        else:
            tipo.disponible = False
            
    context = {
        'tipos_accesos':tipos_accesos,
        'barra_principal': barra_principal,
        'data_contact': data_contact,
        'urls_info': urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes': urls_interes,
}
    
    return render(request, 'list_planes.html', context)




#########################################################################33
from librouteros import connect
from librouteros.query import Key
import ssl
from functools import partial
import librouteros as ros
from .models import MikrotikConfig


def connect_to_router(router_ip, username, password, use_ssl=False):
    if use_ssl:
        api = ros.connect_ssl(router_ip, username=username, password=password)
    else:
        api = ros.connect(router_ip, username=username, password=password)
    return api


#funcion para hacer login en el router mikrotik

def login_mikrotik(router_ip, username, password):
    api = connect_to_router(router_ip, username, password, use_ssl=False)
    return api

#funcion para obtener la lista de clientes del router mikrotik
#Transaccion comprar acceso


def transaccion3ds_compra_acceso(request, tipo_acceso_id):
    barra_principal = Barra_Principal.objects.latest('fecha_creacion')
    data_contact = Contacts.objects.latest()
    urls_info = Urls_info.objects.all()
    ultima_descripcion = General_Description.objects.latest('fecha_creacion')
    urls_interes = Urls_interes.objects.all()
    
    tipo_acceso = get_object_or_404(Tipos, id=tipo_acceso_id)
    accesos_relacionados = Accesos.objects.filter(acceso_tipo=tipo_acceso)
    transacciones_3ds = Transaccion3DS.objects.filter(acceso__in=accesos_relacionados)
    transaccion3ds_respuesta = Transaccion3DS_Respuesta.objects.filter(transaccion3ds__in=transacciones_3ds).first()
    
    acceso_disponible = Accesos.objects.filter(acceso_tipo=tipo_acceso, estado=True).first()
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        numtarjeta = request.POST.get('numtarjeta')
        cvv = request.POST.get('cvv')
        dui = request.POST.get('dui')
        mesvencimiento = request.POST.get('mesvencimiento')
        aniovencimiento = request.POST.get('aniovencimiento')
        
        monto = float(tipo_acceso.precio)
        
        if not acceso_disponible:
            context = {
                'tipo_acceso': tipo_acceso,
                'barra_principal': barra_principal,
                'data_contact': data_contact,
                'urls_info': urls_info,
                'ultima_descripcion': ultima_descripcion,
                'urls_interes': urls_interes,
                'error_message': 'No hay accesos disponibles.',
            }
            return render(request, 'transaccion/pago_fallido.html', context)
        
        try:
            with transaction.atomic():
                # Crear la transacción 3DS
                transaccion_data = crear_transaccion_3ds(
                    acceso_id=acceso_disponible.id,
                    numeroTarjeta=str(numtarjeta),
                    cvv=str(cvv),
                    mesVencimiento=mesvencimiento,
                    anioVencimiento=aniovencimiento,
                    monto=monto,
                    nombre=nombre,
                    apellido=apellido,
                    email=email,
                    ciudad=ciudad,
                    direccion=direccion,
                    telefono=str(telefono),
                    client_id=Client_id,
                    client_secret=Client_secret
                )
                print(transaccion_data)
                
                # Obtiene la última transacción 3DS
                transaccion3ds = Transaccion3DS.objects.latest('fecha_creacion')
                
                # Obtiene la última respuesta de la transacción 3DS
                transaccion3ds_respuesta = Transaccion3DS_Respuesta.objects.filter(transaccion3ds=transaccion3ds).latest('fecha_creacion')
                
                if transaccion_data:
                    cliente = Clientes.objects.create(
                        nombre=nombre,
                        apellido=apellido,
                        direccion=direccion,
                        dui=dui,
                        email=email,
                        telefono=telefono,
                    )
                    
                    transaccion3ds_compra = TransaccionCompra3DS.objects.create(
                        transaccion3ds=transaccion3ds,
                        transaccion3ds_respuesta=transaccion3ds_respuesta,
                        cliente=cliente,
                        acceso=acceso_disponible,
                    )
                    
                    return redirect('transaccion3ds_exitosa', transaccion3ds_id=transaccion3ds.id)
                                
                else:
                    raise Exception("No se pudo realizar la transacción")
        except Exception as e:
            # Manejar errores y revertir la transacción si es necesario
            context = {
                'tipo_acceso': tipo_acceso,
                'barra_principal': barra_principal,
                'data_contact': data_contact,
                'urls_info': urls_info,
                'ultima_descripcion': ultima_descripcion,
                'urls_interes': urls_interes,
                'error_message': str(e),
            }
            return render(request, 'transaccion/pago_fallido.html', context)
    
    else:
        context = {
            'tipo_acceso': tipo_acceso,
            'barra_principal': barra_principal,
            'data_contact': data_contact,
            'urls_info': urls_info,
            'ultima_descripcion': ultima_descripcion,
            'urls_interes': urls_interes,
        }
        return render(request, 'transaccion/comprar3ds_acceso.html', context)



    
# Nueva vista para mostrar el mensaje de éxito
def transaccion3ds_exitosa(request, transaccion3ds_id):
    barra_principal = Barra_Principal.objects.latest('fecha_creacion')
    data_contact = Contacts.objects.latest()
    urls_info = Urls_info.objects.all()
    ultima_descripcion = General_Description.objects.latest('fecha_creacion')
    urls_interes = Urls_interes.objects.all()
    
    transaccion3ds_compra = get_object_or_404(TransaccionCompra3DS, pk=transaccion3ds_id)
    tipo_acceso = transaccion3ds_compra.acceso.acceso_tipo
    acceso = transaccion3ds_compra.acceso
    transaccion3ds_respuesta = transaccion3ds_compra.transaccion3ds_respuesta
    cliente = transaccion3ds_compra.cliente
    acceso_transaccion = acceso
    
    idtransac = transaccion3ds_respuesta.idTransaccion
    consulta_transaccion = consultar_transaccion_3ds(idtransac)

    es_aprobada = consulta_transaccion.get('esAprobada', False)
    
    context = {
        'tipo_acceso': tipo_acceso,
        'transaccion_compra': transaccion3ds_compra,
        'acceso': acceso,
        'cliente': cliente,
        'acceso_transaccion': acceso_transaccion,
        'transaccion3ds_respuesta': transaccion3ds_respuesta,
        'es_aprobada': es_aprobada,
        'consulta_transaccion': consulta_transaccion,
        'barra_principal': barra_principal,
        'data_contact': data_contact,
        'urls_info': urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes': urls_interes,
    }
    
    return render(request, 'transaccion/transaccion_exitosa.html', context)


def transaccion3ds_fallida(request):
    barra_principal = Barra_Principal.objects.latest('fecha_creacion')
    data_contact = Contacts.objects.latest()
    urls_info = Urls_info.objects.all()
    ultima_descripcion = General_Description.objects.latest('fecha_creacion')
    urls_interes = Urls_interes.objects.all()
    
   
    context = {        
        'barra_principal': barra_principal,
        'data_contact': data_contact,
        'urls_info': urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes': urls_interes,
    }
    
    return render(request, 'transaccion/pago_fallido.html', context)


def consultar_transaccion_3ds(id_transaccion):
    # Autenticar con Wompi
    access_token = authenticate_wompi(Client_id, Client_secret)
    
    if not access_token:
        print("Error: 'id_transaccion' not provided.")
        return None
    
    endpoint = f"TransaccionCompra/{id_transaccion}"
    transaccion_info = make_wompi_get_request(endpoint, access_token)
    
    if transaccion_info:
        # Imprimir la información del enlace de pago
        print("Información de la transaccion:")
        print(transaccion_info)
        print("este es el id del enlace", id_transaccion)
        return transaccion_info
    else:
        print("Error: Failed to obtain information for the provided 'id_transaccion'.")
        return None
    
def verificar_pago(request, transaccion_id):
    # Obtén la transacción y verifica su estado
    transaccion = get_object_or_404(Transaccion3DS_Respuesta, idTransaccion=transaccion_id)
    consulta_transaccion = consultar_transaccion_3ds(transaccion.idTransaccion)
    es_aprobada = consulta_transaccion['esAprobada']

    return JsonResponse({'es_aprobada': es_aprobada})


#############################################################################333


def comprar_acceso(request, tipo_acceso_id):
    barra_principal = Barra_Principal.objects.latest('fecha_creacion')
    data_contact = Contacts.objects.latest()
    urls_info = Urls_info.objects.all()
    ultima_descripcion = General_Description.objects.latest('fecha_creacion')
    urls_interes = Urls_interes.objects.all()
    
    tipo_acceso = get_object_or_404(Tipos, pk=tipo_acceso_id)
    
    # Obtener el primer acceso disponible y activo para el tipo de acceso dado
    acceso_disponible = Accesos.objects.filter(acceso_tipo=tipo_acceso, estado=True).first()
    
    enlace_pago_acceso = EnlacePagoAcceso.objects.filter(acceso__acceso_tipo=tipo_acceso).order_by('-fecha_creacion').first()
    
    if acceso_disponible:
              
        
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            direccion = request.POST.get('direccion')
            dui = request.POST.get('dui')
            email = request.POST.get('email')
            telefono = request.POST.get('telefono')

            comercio_id = "volcano_wifi"
            monto = float(tipo_acceso.precio)
            nombre_producto = tipo_acceso.nombre
            descripcion_producto = tipo_acceso.descripcion
            imagen_producto = str(tipo_acceso.url_azure)
            cantidad = 1
            
            # Crear enlace de pago
            enlace_pago = create_payment_link_acceso(
                acceso_disponible.pk,
                Client_id,
                Client_secret,
                comercio_id,
                monto,
                nombre_producto,
                descripcion_producto,
                imagen_producto,
                cantidad
            )
            
            # Obtener el objeto EnlacePagoAcceso relacionado con el acceso
            enlace_pago_acceso = acceso_disponible.enlace_pago_set.last()
            
            if enlace_pago_acceso:
                # Crear cliente
                cliente = Clientes.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    direccion=direccion,
                    dui=dui,
                    email=email,
                    telefono=telefono,
                )
                
                # Crear la transacción de compra
                transaccion_compra = TransaccionCompra.objects.create(
                    enlace_pago=enlace_pago_acceso,
                    cliente=cliente,
                    acceso=acceso_disponible,
                )
                # Desactivar el acceso disponible para que no esté disponible para otras compras
                acceso_disponible.estado = False
                acceso_disponible.save()
                
                #obetner la instancia de transaccion_compra despues de guardarla
                transaccion_compra_instance = get_object_or_404(TransaccionCompra, pk=transaccion_compra.pk)
                transaccion_compra_id = transaccion_compra_instance.pk
                
                context = {
                    'tipo_acceso': tipo_acceso,
                    'acceso': acceso_disponible,
                    'enlace_pago': enlace_pago_acceso,
                    'cliente': cliente,
                    'transaccion_compra': transaccion_compra,
                    'barra_principal': barra_principal,
                    'data_contact': data_contact,
                    'urls_info': urls_info,
                    'ultima_descripcion': ultima_descripcion,
                    'urls_interes': urls_interes,
                }

                return redirect('transaccion_exitosa',transaccion_id=transaccion_compra.id)
            else:
                print("Error: No se pudo crear el enlace de pago") 
                return render(request, 'transaccion/pago_fallido.html', context)
        else:
            context = {
                'tipo_acceso': tipo_acceso,
                'barra_principal': barra_principal,
                'data_contact': data_contact,
                'urls_info': urls_info,
                'ultima_descripcion': ultima_descripcion,
                'urls_interes': urls_interes,
            }
            return render(request, 'transaccion/comprar_acceso.html',context )
    else:
        
        context1 = {
                'barra_principal': barra_principal,
                'data_contact': data_contact,
                'urls_info': urls_info,
                'ultima_descripcion': ultima_descripcion,
                'urls_interes': urls_interes,
                }
        
        print("Error: No hay acceso disponible")
        return render(request, 'transaccion/pago_fallido.html', context1)
    

def transaccion_exitosa(request, transaccion_id):
    # Obtener datos necesarios
    barra_principal = Barra_Principal.objects.latest('fecha_creacion')
    data_contact = Contacts.objects.latest()
    urls_info = Urls_info.objects.all()
    ultima_descripcion = General_Description.objects.latest('fecha_creacion')
    urls_interes = Urls_interes.objects.all()
    
    transaccion_compra = get_object_or_404(TransaccionCompra, pk=transaccion_id)
    tipo_acceso = transaccion_compra.acceso.acceso_tipo
    acceso = Accesos.objects.filter(acceso_tipo=tipo_acceso).first()
    enlace_pago_acceso = transaccion_compra.enlace_pago
    
    cliente_transaccion = transaccion_compra.cliente
    acceso_transaccion = transaccion_compra.enlace_pago.acceso
    
    try:
        # Configuración de la conexión al servicio de correo electrónico de Azure
        connection_string = "endpoint=https://emailvolcanosm.unitedstates.communication.azure.com/;accesskey=SkW7u9s6sgjkska6ncJ8iOQutZdU1f+iIH9rfMto3j+NFLi8bpmcM4PF+4oJ3A+gQkAOXVFvhxaNqa8UTdtcUg=="
        client = EmailClient.from_connection_string(connection_string)
        
        # Renderizar contenido del correo
        correo_html = render_to_string('correo/informacion_acceso.html', {
            'cliente': cliente_transaccion,
            'acceso': acceso_transaccion,
        })
        correo_texto_plano = strip_tags(correo_html)
        
        # Configuración del correo
        message = {
            "senderAddress": settings.EMAIL_HOST_USER,
            "recipients": {
                "to": [{"address": cliente_transaccion.email}],
            },
            "content": {
                "subject": "Información de acceso a su servicio de internet",
                "plainText": correo_texto_plano,
                "html": correo_html,
            }
        }
        
        # Enviar correo
        poller = client.begin_send(message)
        result = poller.result()
        
    except Exception as ex:
        print(ex)
    
    # Imprimir los IDs relacionados
    print("ID de tipo de acceso:", tipo_acceso.pk)
    print("ID de acceso:", acceso.pk)
    print("ID de enlace de pago acceso:", enlace_pago_acceso.pk if enlace_pago_acceso else "No disponible")
    
    # Contexto para la plantilla
    context = {
        'tipo_acceso': tipo_acceso,
        'transaccion_compra': transaccion_compra,
        'enlace_pago': enlace_pago_acceso,
        'acceso': acceso,
        'cliente': cliente_transaccion,
        'acceso_transaccion': acceso_transaccion,
        'barra_principal': barra_principal,
        'data_contact': data_contact,
        'urls_info': urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes': urls_interes,
    }
    
    return render(request, 'transaccion/pago_exitoso.html', context)
    

#VERIFICAR EL PAGO:
def consultar_enlace_pago(id_enlace, client_id, client_secret):
    # Autenticar con Wompi y obtener el token
    access_token = authenticate_wompi(client_id, client_secret)

    if not id_enlace:
        print("Error: 'enlace_pago_id' not provided.")
        return None

    # Utilizar la función make_wompi_get_request para realizar la solicitud GET
    endpoint = f"EnlacePago/{id_enlace}"
    enlace_pago_info = make_wompi_get_request(endpoint, access_token)

    if enlace_pago_info:
        # Imprimir la información del enlace de pago
        print("Información del enlace de pago:")
        print(enlace_pago_info)
        print("este es el id del enlace", id_enlace)
        return enlace_pago_info
    else:
        print("Error: Failed to obtain information for the provided 'id_enlace'.")
        return None
    
def verificar_transaccion_exitosa(request):
    
    if request.method == 'POST':
        # Obtener el idEnlace del cuerpo de la solicitud POST     
        id_enlace = request.POST.get('enlace_pago_id')  # Cambiado de 'enlace_pago_id' a 'id_enlace'
        
        print("Valor de id_enlace:", id_enlace)  # Agregar este registro
        if not id_enlace:
            print("Error: 'id_enlace' not found in request body.")
            return JsonResponse({'success': False, 'message': 'ID de enlace no proporcionado.'})
        
        # Consultar el enlace de pago en Wompi usando el ID de enlace
        client_id = Client_id
        client_secret = Client_secret

        # Consultar enlace de pago usando idEnlace
        enlace_pago_info = consultar_enlace_pago(id_enlace, client_id, client_secret)
        
        if enlace_pago_info:
            # Verificar si la transacción es exitosa
            transaccion_compra = enlace_pago_info.get('transaccionCompra', {})
            if transaccion_compra:
                es_real = transaccion_compra.get('esReal')
                es_aprobada = transaccion_compra.get('esAprobada')
                mensaje = transaccion_compra.get('mensaje')
                
                if es_real and es_aprobada and mensaje == 'AUTORIZADO':
                    # Obtener el ID del enlace de pago
                    id_enlace_pago = enlace_pago_info.get('idEnlace')
                    codigo_autorizacion = transaccion_compra.get('codigoAutorizacion')
                    
                    # Enviar correo electrónico con la información de acceso
                    
                    try:
                        enlace_pago_acceso = EnlacePagoAcceso.objects.get(idEnlace=id_enlace)
                    except:
                        print(f"No se encontró ningún EnlacePagoAcceso para el id_enlace: {id_enlace}")
                        return JsonResponse({'success': False, 'message': 'No se encontró ningún enlace de pago asociado a este ID.'})
                    
                    try:
                        transaccion_compra_actual = TransaccionCompra.objects.get(enlace_pago = enlace_pago_acceso)
                    except TransaccionCompra.DoesNotExist:
                        print(f"No se encontró ninguna TransaccionCompra para el id_enlace: {id_enlace}")
                        return JsonResponse({'success': False, 'message': 'No se encontró ninguna transacción asociada a este ID de enlace.'})  
                    
                    enviar_informacion_acceso_por_correo(transaccion_compra_actual)
                    
                    cliente = transaccion_compra_actual.cliente
                    acceso = transaccion_compra_actual.acceso
                    
                    cliente_dict={
                        'nombre': cliente.nombre,
                        'apellido': cliente.apellido,
                        'email': cliente.email,
                        'telefono': cliente.telefono,
                    }
                    
                    acceso_dict={
                        'usuario': acceso.usuario,
                        'password': acceso.password,
                        'descripcion': acceso.descripcion,
                        'cant_usuarios':acceso.cant_usuarios,
                        'acceso_tipo' : acceso.acceso_tipo.nombre,
                        'fecha_expira': acceso.fecha_expiracion.strftime('%Y-%m-%d'),
                    }
                    
                    cliente_json = json.dumps(cliente_dict)
                    acceso_json = json.dumps(acceso_dict)
                    
                    return JsonResponse({'success': True, 'codigo_autorizacion': codigo_autorizacion, 'id_enlace_pago': id_enlace_pago, 'cliente':cliente_json, 'acceso':acceso_json})
                else:
                    return JsonResponse({'success': False, 'message': 'El pago no se realizó con éxito.'})
            else:
                return JsonResponse({'success': False, 'message': 'No se encontró información de la transacción.'})
        else:
            return JsonResponse({'success': False, 'message': 'No se pudo obtener información del enlace de pago.'})
    else:
        # Manejar el caso en que la solicitud no sea POST
        return JsonResponse({'success': False, 'message': 'Solicitud no válida.'})

def enviar_informacion_acceso_por_correo(transaccion_compra):
    cliente = transaccion_compra.cliente
    acceso = transaccion_compra.acceso

    try:
        # Configuración de la conexión al servicio de correo electrónico de Azure
        connection_string = "endpoint=https://emailvolcanosm.unitedstates.communication.azure.com/;accesskey=SkW7u9s6sgjkska6ncJ8iOQutZdU1f+iIH9rfMto3j+NFLi8bpmcM4PF+4oJ3A+gQkAOXVFvhxaNqa8UTdtcUg=="
        client = EmailClient.from_connection_string(connection_string)

        # Renderizar el template del correo electrónico con la información de acceso
        correo_html = render_to_string('correo/informacion_acceso.html', {
            'cliente': cliente,
            'acceso': acceso,
        })

        # Eliminar etiquetas HTML del cuerpo del correo
        correo_texto_plano = strip_tags(correo_html)

        # Configuración del mensaje
        message = {
            "senderAddress": settings.EMAIL_HOST_USER,
            "recipients": {
                "to": [{"address": cliente.email}],
            },
            "content": {
                "subject": "Información de acceso",
                "html": correo_html,
                "plainText": correo_texto_plano,
            }
        }

        # Envía el correo electrónico utilizando el servicio de correo electrónico de Azure
        poller = client.begin_send(message)
        result = poller.result()

    except Exception as ex:
        print(ex)
        



