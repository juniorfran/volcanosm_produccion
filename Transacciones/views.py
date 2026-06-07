from django.conf import settings
from django.shortcuts import render
import requests
from .wompi_connect import authenticate_wompi
from .wompi_consulta import make_wompi_get_request
from .wompi_envio import make_wompi_post_request, create_payment_link
from datetime import datetime, timedelta
# Create your views here.
from Configuraciones.models import wompi_config

# Credenciales Wompi cargadas de forma segura: NO debe romper el arranque si
# la BD no está disponible o la tabla aún no existe (migraciones / dev local).
try:
    latest_config = wompi_config.objects.latest('created_at')
    Client_id = latest_config.client_id
    Client_secret = latest_config.client_secret
except Exception:
    latest_config = None
    Client_id = None
    Client_secret = None


def consultar_enlace_pago(enlace_pago_id, client_id, client_secret):
    # Autenticar con Wompi y obtener el token
    access_token = authenticate_wompi(client_id, client_secret)

    if not access_token:
        print("Error de autenticación con Wompi.")
        return None

    # Utilizar la función make_wompi_get_request para realizar la solicitud GET
    enlace_pago_info = make_wompi_get_request(f"EnlacePago/{enlace_pago_id}", access_token)

    if enlace_pago_info:
        # Imprimir la información del enlace de pago
        # print("Información del enlace de pago:")
        # print(enlace_pago_info)
        pass
    else:
        print("Error al obtener información del enlace de pago.")

# (Eliminada la llamada de prueba a nivel de módulo que hacía red al importar.)
