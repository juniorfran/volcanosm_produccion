# -*- coding: utf-8 -*-
"""Genera imágenes placeholder (locales) y las asigna a los modelos del seed.

Ejecutar:  python manage.py shell < scripts/seed_images.py
- ImageFields (Producto, ArticuloAlquiler): se setean por .update() a seed/<f>.png
- Campos URL de display (url_azure / imagen_url / imagen_tipo): se setean a /media/seed/<f>.png
Las imágenes se escriben en MEDIA_ROOT/seed/ (servidas por runserver en DEBUG).
"""
import os
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont

SEED_DIR = os.path.join(settings.MEDIA_ROOT, "seed")
os.makedirs(SEED_DIR, exist_ok=True)

# paleta por tema
COLORS = {
    "Bebidas": (37, 99, 235), "Snacks": (217, 119, 6), "Dulces": (219, 39, 119),
    "Galletas": (180, 83, 9), "Abarrotes": (5, 150, 105),
    "tour": (22, 101, 52), "servicio": (13, 110, 253), "alquiler": (124, 58, 237),
    "carrusel": (15, 23, 42), "equipo": (71, 85, 105), "internet": (8, 145, 178),
    "nosotros": (30, 41, 59),
}

try:
    FONT = ImageFont.load_default(size=34)
    FONT_S = ImageFont.load_default(size=22)
except TypeError:
    FONT = ImageFont.load_default()
    FONT_S = FONT


def make(filename, text, color, size=(640, 420), sub=""):
    """Crea un PNG con color de fondo y texto centrado. Devuelve 'seed/<filename>'."""
    img = Image.new("RGB", size, color)
    d = ImageDraw.Draw(img)
    # capa translúcida inferior para legibilidad
    d.rectangle([0, size[1] - 110, size[0], size[1]], fill=(0, 0, 0))
    d.text((24, size[1] - 92), text[:34], fill="white", font=FONT)
    if sub:
        d.text((24, size[1] - 50), sub[:46], fill=(200, 210, 220), font=FONT_S)
    # marca
    d.text((22, 20), "VOLCANO", fill=(255, 193, 7), font=FONT_S)
    img.save(os.path.join(SEED_DIR, filename), "PNG")
    return f"seed/{filename}"


def media_url(rel):
    return settings.MEDIA_URL.rstrip("/") + "/" + rel

count = {"img": 0}


def gen(filename, text, color, **kw):
    rel = make(filename, text, color, **kw)
    count["img"] += 1
    return rel


# -------- Productos (ImageField) --------
from TPV_.Productos.models import Producto
for p in Producto.objects.all():
    cat = p.categoria.nombre if p.categoria else "Abarrotes"
    rel = gen(f"prod_{p.pk}.png", p.nombre, COLORS.get(cat, (5, 150, 105)), size=(400, 400), sub=cat)
    Producto.objects.filter(pk=p.pk).update(imagen=rel)

# -------- Artículos de alquiler (ImageField) --------
from TPV_.Alquileres.models import ArticuloAlquiler
for a in ArticuloAlquiler.objects.all():
    rel = gen(f"alq_{a.pk}.png", a.nombre, COLORS["alquiler"], size=(400, 400), sub=a.categoria)
    ArticuloAlquiler.objects.filter(pk=a.pk).update(imagen=rel)

# -------- Tours (url_azure) --------
from Tours.models import Tour
for t in Tour.objects.all():
    rel = gen(f"tour_{t.pk}.png", t.titulo, COLORS["tour"], sub=f"${t.precio_adulto} adulto")
    Tour.objects.filter(pk=t.pk).update(url_azure=media_url(rel))

# -------- Servicios (url_azure) --------
from Servicios.models import Servicios
for s in Servicios.objects.all():
    rel = gen(f"serv_{s.pk}.png", s.nombre, COLORS["servicio"])
    Servicios.objects.filter(pk=s.pk).update(url_azure=media_url(rel))

# -------- Carrusel (imagen_url) — hero ancho --------
from Configuraciones.models import CarruselInicio, Services_Bar, Team_bar
for c in CarruselInicio.objects.all():
    rel = gen(f"carrusel_{c.pk}.png", c.titulo, COLORS["carrusel"], size=(1600, 600), sub=c.contenido)
    CarruselInicio.objects.filter(pk=c.pk).update(imagen_url=media_url(rel))

# -------- Services bar: ICONOS (FontAwesome/Bootstrap) + imagen --------
ICONOS = ["fa fa-map-signs", "fa fa-fire", "fa fa-suitcase", "fa fa-bed", "fa fa-shopping-basket"]
for i, sb in enumerate(Services_Bar.objects.all()):
    rel = gen(f"sbar_{sb.pk}.png", sb.services_name, COLORS["servicio"], size=(300, 300))
    Services_Bar.objects.filter(pk=sb.pk).update(imagen_url=media_url(rel), services_ico_tag=ICONOS[i % len(ICONOS)])

# -------- Equipo (imagen_url) — avatares --------
for t in Team_bar.objects.all():
    rel = gen(f"team_{t.pk}.png", t.team_nombre, COLORS["equipo"], size=(300, 300), sub=t.team_job)
    Team_bar.objects.filter(pk=t.pk).update(imagen_url=media_url(rel))

# -------- Internet Tipos (url_azure) --------
from Internet.models import Tipos
for tp in Tipos.objects.all():
    rel = gen(f"plan_{tp.pk}.png", tp.nombre, COLORS["internet"], size=(400, 300), sub=tp.tiempo_conexion)
    Tipos.objects.filter(pk=tp.pk).update(url_azure=media_url(rel))

# -------- Nosotros (imagen_url + pequeñas) + servicios íconos --------
from Nosotros.models import Nosotros, Nosotros_Servicios
for n in Nosotros.objects.all():
    big = gen(f"nos_{n.pk}.png", n.titulo, COLORS["nosotros"], size=(800, 600))
    s1 = gen(f"nos_{n.pk}_1.png", "Aventura", COLORS["tour"], size=(400, 400))
    s2 = gen(f"nos_{n.pk}_2.png", "Camping", COLORS["alquiler"], size=(400, 400))
    Nosotros.objects.filter(pk=n.pk).update(imagen_url=media_url(big),
        imagen_pequena_1_url=media_url(s1), imagen_pequena_2_url=media_url(s2))
ICONOS_NS = ["fa fa-mountain", "fa fa-campground", "fa fa-hiking", "fa fa-box"]
for i, ns in enumerate(Nosotros_Servicios.objects.all()):
    rel = gen(f"ns_{ns.pk}.png", ns.servicio_titulo, COLORS["servicio"], size=(200, 200))
    Nosotros_Servicios.objects.filter(pk=ns.pk).update(icono_url=media_url(rel))

print(f"=== {count['img']} imágenes generadas en {SEED_DIR} ===")
