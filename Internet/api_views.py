####################################################################################################################
####################################################################################################################
################################################# VISTAS DE LA API #################################################
####################################################################################################################
####################################################################################################################

from django.conf import settings
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from Transacciones.wompi_connect import authenticate_wompi
from Transacciones.wompi_consulta import make_wompi_get_request
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Tipos, Accesos, Transaccion3DS, Transaccion3DS_Respuesta, Clientes, TransaccionCompra3DS
import requests
from .models import (
    Tipos, Accesos, Clientes, EnlacePagoAcceso, 
    TransaccionCompra, Transaccion3DS, 
    Transaccion3DS_Respuesta, TransaccionCompra3DS, MikrotikConfig
)
from .serializers import (
    TiposSerializer, AccesosSerializer, ClientesSerializer, EnlacePagoAccesoSerializer, 
    TransaccionCompraSerializer, Transaccion3DSSerializer, 
    Transaccion3DS_RespuestaSerializer, TransaccionCompra3DSSerializer, MikrotikConfigSerializer
)


from django.core.exceptions import ImproperlyConfigured
def get_wompi_config():
    from Configuraciones.models import wompi_config
    try:
        config = wompi_config.objects.latest('created_ad')
        return config
    except wompi_config.DoesNotExist:
        raise ImproperlyConfigured("No se encontro ninguna configuración de Wompi en la base de datos")
    

class TiposListCreate(generics.ListCreateAPIView):
    queryset = Tipos.objects.all()
    serializer_class = TiposSerializer

class TiposRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tipos.objects.all()
    serializer_class = TiposSerializer

class AccesosListCreate(generics.ListCreateAPIView):
    queryset = Accesos.objects.all()
    serializer_class = AccesosSerializer

class AccesosRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Accesos.objects.all()
    serializer_class = AccesosSerializer

class ClientesListCreate(generics.ListCreateAPIView):
    queryset = Clientes.objects.all()
    serializer_class = ClientesSerializer

class ClientesRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Clientes.objects.all()
    serializer_class = ClientesSerializer

class EnlacePagoAccesoListCreate(generics.ListCreateAPIView):
    queryset = EnlacePagoAcceso.objects.all()
    serializer_class = EnlacePagoAccesoSerializer

class EnlacePagoAccesoRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = EnlacePagoAcceso.objects.all()
    serializer_class = EnlacePagoAccesoSerializer

class TransaccionCompraListCreate(generics.ListCreateAPIView):
    queryset = TransaccionCompra.objects.all()
    serializer_class = TransaccionCompraSerializer

class TransaccionCompraRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = TransaccionCompra.objects.all()
    serializer_class = TransaccionCompraSerializer

class Transaccion3DSListCreate(generics.ListCreateAPIView):
    queryset = Transaccion3DS.objects.all()
    serializer_class = Transaccion3DSSerializer

class Transaccion3DSRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaccion3DS.objects.all()
    serializer_class = Transaccion3DSSerializer

class Transaccion3DS_RespuestaListCreate(generics.ListCreateAPIView):
    queryset = Transaccion3DS_Respuesta.objects.all()
    serializer_class = Transaccion3DS_RespuestaSerializer

class Transaccion3DS_RespuestaRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaccion3DS_Respuesta.objects.all()
    serializer_class = Transaccion3DS_RespuestaSerializer

class TransaccionCompra3DSListCreate(generics.ListCreateAPIView):
    queryset = TransaccionCompra3DS.objects.all()
    serializer_class = TransaccionCompra3DSSerializer

class TransaccionCompra3DSRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = TransaccionCompra3DS.objects.all()
    serializer_class = TransaccionCompra3DSSerializer

class MikrotikConfigListCreate(generics.ListCreateAPIView):
    queryset = MikrotikConfig.objects.all()
    serializer_class = MikrotikConfigSerializer

class MikrotikConfigRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = MikrotikConfig.objects.all()
    serializer_class = MikrotikConfigSerializer
    


@api_view(['POST'])
def get_wompi_headers(access_token):
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

@api_view(['POST'])
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
    
def consultar_transaccion_3ds(id_transaccion):

    # Cargar la configuración de Wompi
    wompi_config = settings.get_wompi_config()
    Client_id = wompi_config.client_id
    Client_secret = wompi_config.client_secret

    # Autenticarse y obtener el token
    access_token = authenticate_wompi(Client_id, Client_secret)
    
    if not access_token:
        print("Error: 'id_transaccion' not provided.")
        return None
    
    endpoint = f"TransaccionCompra/{id_transaccion}"
    transaccion_info = make_wompi_get_request(endpoint, access_token)
    
    if transaccion_info:
        print("Información de la transaccion:")
        print(transaccion_info)
        print("este es el id del enlace", id_transaccion)
        return transaccion_info
    else:
        print("Error: Failed to obtain information for the provided 'id_transaccion'.")
        return None


class Transaccion3DSCompraAccesoView(APIView):

    queryset = Transaccion3DS.objects.all()
    permission_classes = [AllowAny]
    def post(self, request, tipo_acceso_id):

        # Cargar la configuración de Wompi
        wompi_config = settings.get_wompi_config()
        Client_id = wompi_config.client_id
        Client_secret = wompi_config.client_secret

        # Autenticarse y obtener el token
        access_token = authenticate_wompi(Client_id, Client_secret)

        tipo_acceso = get_object_or_404(Tipos, id=tipo_acceso_id)
        acceso_disponible = Accesos.objects.filter(acceso_tipo=tipo_acceso, estado=True).first()
        
        if not acceso_disponible:
            return Response({'error_message': 'No hay accesos disponibles.'}, status=status.HTTP_400_BAD_REQUEST)

        nombre = request.data.get('nombre')
        apellido = request.data.get('apellido')
        direccion = request.data.get('direccion')
        ciudad = request.data.get('ciudad')
        email = request.data.get('email')
        telefono = request.data.get('telefono')
        numtarjeta = request.data.get('numtarjeta')
        cvv = request.data.get('cvv')
        dui = request.data.get('dui')
        mesvencimiento = request.data.get('mesvencimiento')
        aniovencimiento = request.data.get('aniovencimiento')
        monto = float(tipo_acceso.precio)
        
        try:
            with transaction.atomic():
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
                
                if transaccion_data:
                    transaccion3ds = Transaccion3DS.objects.latest('fecha_creacion')
                    transaccion3ds_respuesta = Transaccion3DS_Respuesta.objects.filter(transaccion3ds=transaccion3ds).latest('fecha_creacion')
                    
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
                    
                    return Response({'transaccion3ds_id': transaccion3ds.id}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error_message': 'No se pudo realizar la transacción'}, status=status.HTTP_400_BAD_REQUEST)
                    
        except Exception as e:
            return Response({'error_message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['GET'])
def transaccion3ds_exitosa(request, transaccion3ds_id):
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
    }
    
    return Response(context, status=status.HTTP_200_OK)

@api_view(['GET'])
def transaccion3ds_fallida(request):
    context = {        
        'error_message': 'La transacción ha fallado.'
    }
    
    return Response(context, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def verificar_pago(request, transaccion_id):
    transaccion = get_object_or_404(Transaccion3DS_Respuesta, idTransaccion=transaccion_id)
    consulta_transaccion = consultar_transaccion_3ds(transaccion.idTransaccion)
    es_aprobada = consulta_transaccion['esAprobada']

    return Response({'es_aprobada': es_aprobada}, status=status.HTTP_200_OK)




    
