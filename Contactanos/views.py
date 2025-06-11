# En tu archivo views.py
from django.shortcuts import render, redirect
from django.conf import settings
import requests
from django.contrib import messages 
from Configuraciones.models import Barra_Principal, Contacts, Direccionamiento, General_Description, Urls_info, Urls_interes
from Tours.models import Tour
from .models import Mensaje_Contacto

RECAPTCHA_SECRET_KEY = "6LfQS10rAAAAAEaaHqrRXEbFWP69quWZRbdeysJ7"

def contacto(request):
    # --- datos de contexto que ya tenías -----------------------------
    tours               = Tour.objects.all().order_by('-tipo_tour')
    barra_principal     = Barra_Principal.objects.latest('fecha_creacion')
    data_contact        = Contacts.objects.latest()
    urls_info           = Urls_info.objects.all()
    ultima_descripcion  = General_Description.objects.latest('fecha_creacion')
    urls_interes        = Urls_interes.objects.all()
    conf_direccionamiento = Direccionamiento.objects.latest('fecha_creacion')

    if request.method == "POST":
        # ➊  Valores del formulario
        nombre  = request.POST.get("name", "")
        email   = request.POST.get("email", "")
        asunto  = request.POST.get("subject", "")
        mensaje = request.POST.get("message", "")

        # ➋  Token de reCAPTCHA
        recaptcha_token = request.POST.get("g-recaptcha-response")

        # ➌  Verificar con Google
        recaptcha_ok = False
        if recaptcha_token:
            verify_url = "https://www.google.com/recaptcha/api/siteverify"
            payload = {
                "secret":  RECAPTCHA_SECRET_KEY,   # Guárdala en settings.py o variables de entorno
                "response": recaptcha_token,
                "remoteip": request.META.get("REMOTE_ADDR"),
            }
            try:
                r = requests.post(verify_url, data=payload, timeout=5)
                result = r.json()
                recaptcha_ok = result.get("success", False)
            except requests.RequestException:
                recaptcha_ok = False

        # ➍  Procesar según resultado
        if recaptcha_ok:
            Mensaje_Contacto.objects.create(
                nombre=nombre,
                email=email,
                asunto=asunto,
                mensaje=mensaje,
            )
            messages.success(request, "¡Tu mensaje se envió correctamente!")
            return redirect("contacto")
        else:
            messages.error(
                request,
                "Por favor confirma el reCAPTCHA para enviar tu mensaje."
            )

    # --- contexto para renderizar la página --------------------------
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
    }
    return render(request, "contactanos.index.html", context)
