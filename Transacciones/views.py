from django.conf import settings
from django.shortcuts import render
import requests
from .wompi_connect import authenticate_wompi
from .wompi_consulta import make_wompi_get_request
from .wompi_envio import make_wompi_post_request, create_payment_link
from datetime import datetime, timedelta
# Create your views here.

# Cliente ID y Secret para autenticación con Wompi
Client_id = settings.CLIENT_ID
Client_secret = settings.CLIENT_SECRET

# Autenticarse y obtener el token
access_token = authenticate_wompi(Client_id, Client_secret)

if access_token:
    # Hacer una consulta utilizando el token
    consulta_result = make_wompi_get_request("EnlacePago", access_token)

    if consulta_result:
        print("Consulta exitosa:")
        #imprimir el resultado de la consulta como diccionario ordenado
        #print("\n".join([f"{k}: {v}" for k, v in sorted(consulta_result.items())]))
        #print(consulta_result)


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

# ID del enlace de pago que deseas consultar
enlace_pago_id = "1072404"

# Llamar a la función para realizar la consulta del enlace de pago
consultar_enlace_pago(enlace_pago_id, Client_id, Client_secret)
