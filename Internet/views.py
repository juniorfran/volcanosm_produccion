from django.utils import timezone
import json
from django.shortcuts import get_object_or_404, redirect, render
import requests
from .models import EnlacePagoAcceso, Accesos, Tipos, Clientes, TransaccionCompra
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from Configuraciones.models import Barra_Principal, Contacts, Direccionamiento, General_Description, Urls_info, Urls_interes

from Transacciones.wompi_connect import authenticate_wompi
from Transacciones.wompi_consulta import make_wompi_get_request
from Transacciones.wompi_envio import create_payment_link


from azure.communication.email import EmailClient
from django.conf import settings
import qrcode
from io import BytesIO
from django.template.loader import render_to_string
from django.utils.html import strip_tags

Client_id = settings.CLIENT_ID
Client_secret = settings.CLIENT_SECRET


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
        "content-type": "application/json",
        "authorization": f"Bearer {access_token}"
    }



def servicio_inter_index(request):
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
    }
    
    return render(request, 'list_planes.html', context)


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
                
                #obetner la instancia de transaccion_compra despues de guardarla
                transaccion_compra_instance = get_object_or_404(TransaccionCompra, pk=transaccion_compra.pk)
                transaccion_compra_id = transaccion_compra_instance.pk
                
                # Desactivar el acceso disponible para que no esté disponible para otras compras
                acceso_disponible.estado = True
                acceso_disponible.save()


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
        
    # Imprimir los IDs relacionados
    print("ID de tipo de acceso:", tipo_acceso.pk)
    print("ID de acceso:", acceso.pk)
    print("ID de enlace de pago acceso:", enlace_pago_acceso.pk if enlace_pago_acceso else "No disponible")
    
    context = {
        'tipo_acceso': tipo_acceso,
        'transaccion_compra': transaccion_compra,
        'enlace_pago': enlace_pago_acceso,
        'acceso': acceso,
        'cliente':cliente_transaccion,
        'acceso_transaccion':acceso_transaccion,
        
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