# views.py
import time
import requests
from django.shortcuts import render, redirect
from django.contrib import messages

from Configuraciones.models import (
    Barra_Principal, Contacts, Direccionamiento,
    General_Description, Urls_info, Urls_interes
)
from Tours.models import Tour
from alpiedelvolcan_ import settings
from .models import Mensaje_Contacto


def _get_client_ip(request):
    xfwd = request.META.get("HTTP_X_FORWARDED_FOR")
    if xfwd:
        # toma el primer IP real
        return xfwd.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def verificar_recaptcha(token, accion, ip):
    """Devuelve True si el token es válido y >= umbral."""
    try:
        resp = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": settings.RECAPTCHA_SECRET_KEY,
                  "response": token,
                  "remoteip": ip},
            timeout=6,
        ).json()
    except requests.RequestException:
        return False
    return (
        resp.get("success")
        and resp.get("action") == accion
        and resp.get("score", 0) >= 0.5
    )


def contacto(request):
    # ---- datos comunes para el template
    tours = Tour.objects.all().order_by("-tipo_tour")
    barra_principal = Barra_Principal.objects.latest("fecha_creacion")
    data_contact = Contacts.objects.latest()
    urls_info = Urls_info.objects.all()
    ultima_descripcion = General_Description.objects.latest("fecha_creacion")
    urls_interes = Urls_interes.objects.all()
    conf_direccionamiento = Direccionamiento.objects.latest("fecha_creacion")

    if request.method == "POST":
        # --- anti-spam: honeypot
        if request.POST.get("website"):  # campo invisible para bots
            messages.error(request, "No pudimos verificar el formulario.")
            return redirect("contacto")

        # --- anti-spam: tiempo mínimo en pantalla
        try:
            ts = float(request.POST.get("form_ts", "0"))
        except ValueError:
            ts = 0.0
        if time.time() - ts < 3:
            messages.error(request, "Parece un envío automatizado. Intenta de nuevo.")
            return redirect("contacto")

        # --- anti-spam: bloqueo de doble envío muy seguido
        last = request.session.get("last_contact_submit", 0)
        if time.time() - last < 8:
            messages.warning(request, "Ya recibimos tu mensaje reciente. Gracias.")
            return redirect("contacto")

        # --- campos
        nombre = (request.POST.get("name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        asunto = (request.POST.get("subject") or "").strip()
        mensaje = (request.POST.get("message") or "").strip()

        # --- validaciones mínimas
        if not all([nombre, email, asunto, mensaje]):
            messages.error(request, "Completa todos los campos requeridos.")
            return redirect("contacto")

        # --- reCAPTCHA v3
        ip = _get_client_ip(request)
        token = request.POST.get("recaptcha_token", "")
        if not token or not verificar_recaptcha(token, "contact", ip):
            messages.error(request, "No pudimos verificar que eres humano.")
            return redirect("contacto")

        # --- guardar mensaje
        Mensaje_Contacto.objects.create(
            nombre=nombre, email=email, asunto=asunto, mensaje=mensaje
        )

        # marca el tiempo para evitar doble envío inmediato
        request.session["last_contact_submit"] = time.time()

        messages.success(request, "¡Gracias! Te responderemos muy pronto.")
        return redirect("contacto")

    # GET
    context = {
        "tours": tours,
        "barra_principal": barra_principal,
        "data_contact": data_contact,
        "urls_info": urls_info,
        "ultima_descripcion": ultima_descripcion,
        "urls_interes": urls_interes,
        "titulo": "Contáctanos",
        "direccion_actual": "contactanos",
        "direccionamiento": conf_direccionamiento,
        # pasa la site key al template
        "recaptcha_site_key": getattr(settings, "RECAPTCHA_SITE_KEY", ""),
    }
    return render(request, "contactanos.index.html", context)
