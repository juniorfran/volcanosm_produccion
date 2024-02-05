# En tu archivo views.py
from django.shortcuts import render, redirect
from .models import Mensaje_Contacto

def contacto(request):
    if request.method == 'POST':
        nombre = request.POST.get('name', '')
        email = request.POST.get('email', '')
        asunto = request.POST.get('subject', '')
        mensaje = request.POST.get('message', '')
        Mensaje_Contacto.objects.create(nombre=nombre, email=email, asunto=asunto, mensaje=mensaje)
        return redirect('contacto')  # Redirige a la misma página después de enviar el mensaje

    return render(request, 'contactanos.index.html')  # Cambia 'tu_template.html' al nombre de tu template
