# En tu archivo views.py
from django.shortcuts import render, redirect
from django.conf import settings
import requests
from django.contrib import messages 
from Configuraciones.models import Barra_Principal, Contacts, Direccionamiento, General_Description, Urls_info, Urls_interes
from Tours.models import Tour
from .models import Mensaje_Contacto

def verificar_recaptcha(token, accion_esperada, ip):
    """Devuelve True|False según éxito + score + action."""
    if not token:
        return False
    try:
        r = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": settings.RECAPTCHA_SECRET_KEY,
                "response": token,
                "remoteip": ip,
            },
            timeout=5,
        )
        data = r.json()
    except requests.RequestException:
        return False

    return (
        data.get("success", False)              # token válido
        and data.get("action") == accion_esperada   # coincide la acción
        and data.get("score", 0) >= settings.RECAPTCHA_SCORE_THRESHOLD
    )

def contacto(request):
    # ----- contexto que ya tenías ------------------------------------------------
    tours = Tour.objects.all().order_by('-tipo_tour')
    barra_principal = Barra_Principal.objects.latest('fecha_creacion')
    data_contact = Contacts.objects.latest()
    urls_info = Urls_info.objects.all()
    ultima_descripcion = General_Description.objects.latest('fecha_creacion')
    urls_interes = Urls_interes.objects.all()
    conf_direccionamiento = Direccionamiento.objects.latest('fecha_creacion')

    if request.method == "POST":
        # datos del formulario
        nombre  = request.POST.get("name", "")
        email   = request.POST.get("email", "")
        asunto  = request.POST.get("subject", "")
        mensaje = request.POST.get("message", "")

        # token & acción
        token  = request.POST.get("recaptcha_token")
        accion = request.POST.get("recaptcha_action", "")

        # verificación
        if verificar_recaptcha(token, accion, request.META.get("REMOTE_ADDR")):
            Mensaje_Contacto.objects.create(
                nombre=nombre, email=email, asunto=asunto, mensaje=mensaje
            )
            messages.success(request, "¡Tu mensaje se envió correctamente!")
            return redirect("contacto")
        else:
            messages.error(
                request,
                "No pudimos verificar que seas humano. Intenta de nuevo."
            )

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
        "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY,  # envía la key al template
    }
    return render(request, "contactanos.index.html", context)