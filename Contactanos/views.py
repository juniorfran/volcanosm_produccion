# En tu archivo views.py
from django.shortcuts import render, redirect
import requests

from Configuraciones.models import Barra_Principal, Contacts, Direccionamiento, General_Description, Urls_info, Urls_interes
from Tours.models import Tour
from alpiedelvolcan_ import settings
from .models import Mensaje_Contacto

def verificar_recaptcha(token, accion, ip):
    resp = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={
            "secret": settings.RECAPTCHA_SECRET_KEY,
            "response": token,
            "remoteip": ip,
        },
        timeout=5,
    ).json()
    return (
        resp.get("success")
        and resp.get("action") == accion     # "contact"
        and resp.get("score", 0) >= 0.5      # umbral
    )


def contacto(request):
    tours = Tour.objects.all().order_by('-tipo_tour')
    barra_principal = Barra_Principal.objects.latest('fecha_creacion') #obtener la barra principal
    data_contact = Contacts.objects.latest()#obtener todos los datos de contacto
    urls_info = Urls_info.objects.all() #obtener todas las url de informacion
    ultima_descripcion = General_Description.objects.latest('fecha_creacion') # Obtén la última descripción general
    urls_interes = Urls_interes.objects.all() #urls de interes
    conf_direccionamiento = Direccionamiento.objects.latest('fecha_creacion')
    titulo = "Contactanos"
    direccion_actual = "contactanos"
    
    
    
    if request.method == 'POST':
        nombre = request.POST.get('name', '')
        email = request.POST.get('email', '')
        asunto = request.POST.get('subject', '')
        mensaje = request.POST.get('message', '')
        Mensaje_Contacto.objects.create(nombre=nombre, email=email, asunto=asunto, mensaje=mensaje)
        return redirect('contacto')  # Redirige a la misma página después de enviar el mensaje
    
    context={
        'tours': tours,
        'barra_principal':barra_principal,
        'data_contact':data_contact,
        'urls_info':urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes':urls_interes,
        'titulo':titulo,
        'direccion_actual':direccion_actual,
        'direccionamiento':conf_direccionamiento,
    }

    return render(request, 'contactanos.index.html', context)
