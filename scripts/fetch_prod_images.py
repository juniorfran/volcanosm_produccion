# -*- coding: utf-8 -*-
"""Descarga las imágenes reales de producción (Azure, públicas) a media_local/prod/
y las asigna a los registros locales (sitio público). Reescribe los campos URL a
/media/prod/<archivo> para que funcionen offline en desarrollo.

Ejecutar:  python manage.py shell < scripts/fetch_prod_images.py
"""
import os
from urllib.parse import urlparse
import requests
from django.conf import settings

PROD = os.path.join(settings.MEDIA_ROOT, "prod")
os.makedirs(PROD, exist_ok=True)

URLS = {
    "tour": [
        "https://storagevolcanosm.blob.core.windows.net/imagenes/tours/2025/2/4/1_imagen_1000163942.jpg",
        "https://storagevolcanosm.blob.core.windows.net/imagenes/tours/2025/2/4/2_imagen_1000209658.jpg",
        "https://storagevolcanosm.blob.core.windows.net/imagenes/tours/2026/3/2/3_imagen_3_imagen_4_zqItOw9_oAATXww.jpg",
    ],
    "servicio": [
        "https://storagevolcanosm.blob.core.windows.net/imagenes/tours/2024/5/13/1_imagen_5.jpg",
    ],
    "carrusel": [
        "https://storagevolcanosm.blob.core.windows.net/imagenes/configuraciones/carrusel_inicio/3.jpg",
        "https://storagevolcanosm.blob.core.windows.net/imagenes/configuraciones/carrusel_inicio/4.jpg",
    ],
    "servbar": [
        "https://storagevolcanosm.blob.core.windows.net/imagenes/configuraciones/services_bar/service_camping_gif_BQfU8Lu.gif",
        "https://storagevolcanosm.blob.core.windows.net/imagenes/configuraciones/services_bar/service_tours_gif_JN3gmjg.gif",
        "https://storagevolcanosm.blob.core.windows.net/imagenes/configuraciones/services_bar/parque.gif",
        "https://storagevolcanosm.blob.core.windows.net/imagenes/configuraciones/services_bar/carro-nuevo.gif",
        "https://storagevolcanosm.blob.core.windows.net/imagenes/configuraciones/services_bar/wifi.gif",
        "https://storagevolcanosm.blob.core.windows.net/imagenes/configuraciones/services_bar/camara-de-seguridad.gif",
    ],
    "team": [
        "https://storagevolcanosm.blob.core.windows.net/imagenes/configuraciones/team_bar/miguel-.jpg",
        "https://storagevolcanosm.blob.core.windows.net/imagenes/configuraciones/team_bar/jose.jpeg",
        "https://storagevolcanosm.blob.core.windows.net/imagenes/configuraciones/team_bar/danny_wNtltGl.jpeg",
    ],
    "tipo": [
        "https://storagevolcanosm.blob.core.windows.net/imagenes/tipos_accesos/2026/3/4/1_imagen_1_imagen_starlink_rLbguSi.jpg",
        "https://storagevolcanosm.blob.core.windows.net/imagenes/tipos_accesos/2026/3/4/2_imagen_starlink_UtURzqQ.jpg",
    ],
    "nosotros": ["https://storagevolcanosm.blob.core.windows.net/imagenes/nosotros/2024-02-03/dji_fly_20240115_172728_257_1705361803150_photo.jpg"],
    "nosotros_p1": ["https://storagevolcanosm.blob.core.windows.net/imagenes/nosotros/2024-02-03/7.jpg"],
    "nosotros_p2": ["https://storagevolcanosm.blob.core.windows.net/imagenes/nosotros/2024-02-03/5.jpg"],
}


def download(url, prefix, idx):
    base = os.path.basename(urlparse(url).path)
    fname = f"{prefix}_{idx}_{base}"
    dest = os.path.join(PROD, fname)
    if not os.path.exists(dest):
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(dest, "wb") as f:
            f.write(r.content)
    return settings.MEDIA_URL.rstrip("/") + "/prod/" + fname


def fetch_group(key):
    out = []
    for i, u in enumerate(URLS.get(key, [])):
        try:
            out.append(download(u, key, i))
        except Exception as e:
            print("  ERR descarga", u, repr(e)[:80])
    return out


def assign(local_qs, field, urls):
    if not urls:
        return 0
    n = 0
    for i, obj in enumerate(local_qs):
        type(obj).objects.filter(pk=obj.pk).update(**{field: urls[i % len(urls)]})
        n += 1
    return n


from Tours.models import Tour
from Servicios.models import Servicios
from Configuraciones.models import CarruselInicio, Services_Bar, Team_bar
from Internet.models import Tipos
from Nosotros.models import Nosotros

tours = fetch_group("tour")
serv = fetch_group("servicio")
carr = fetch_group("carrusel")
sbar = fetch_group("servbar")
team = fetch_group("team")
tipo = fetch_group("tipo")
nos = fetch_group("nosotros")
nos1 = fetch_group("nosotros_p1")
nos2 = fetch_group("nosotros_p2")

print("Tours:", assign(Tour.objects.all(), "url_azure", tours))
print("Servicios:", assign(Servicios.objects.all(), "url_azure", serv))
print("Carrusel:", assign(CarruselInicio.objects.all(), "imagen_url", carr))
print("Services_Bar:", assign(Services_Bar.objects.all(), "imagen_url", sbar))
print("Team_bar:", assign(Team_bar.objects.all(), "imagen_url", team))
print("Tipos:", assign(Tipos.objects.all(), "url_azure", tipo))
# Nosotros: principal + 2 pequeñas
for nobj in Nosotros.objects.all():
    upd = {}
    if nos: upd["imagen_url"] = nos[0]
    if nos1: upd["imagen_pequena_1_url"] = nos1[0]
    if nos2: upd["imagen_pequena_2_url"] = nos2[0]
    if upd:
        Nosotros.objects.filter(pk=nobj.pk).update(**upd)
print("Nosotros: actualizado")

total = len([f for f in os.listdir(PROD)])
print(f"=== {total} imágenes reales descargadas en {PROD} ===")
