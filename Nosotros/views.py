from django.http import Http404, JsonResponse
from django.shortcuts import render
from Configuraciones.models import Barra_Principal, Contacts, General_Description, Services_Bar, Team_bar, Urls_info, Urls_interes
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Nosotros, Nosotros_Servicios, Solicitud_Oferta, Nosotros_Oferta



# Create your views here.
def nosotros_index(request):
    
    #Obtener todos los services bar
    services = Services_Bar.objects.filter(services_visible=True)  # Filtra los servicios visibles
    
    #obetner todos los teams
    teams_bar = Team_bar.objects.all().order_by("id")
    
    # Obtén la última descripción general
    ultima_descripcion = General_Description.objects.latest('fecha_creacion')
    #obtener la barra principal
    barra_principal = Barra_Principal.objects.latest('fecha_creacion')
    
    #obtener todos los datos de contacto
    data_contact = Contacts.objects.latest()
    
    #obtener todas las url de informacion
    urls_info = Urls_info.objects.all()
    
    #urls de interes
    urls_interes = Urls_interes.objects.all()
    
    #formulario de solicitud de oferta
    if request.method == 'POST':
        # Procesar el formulario enviado
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')

        # Crear una nueva solicitud de oferta
        solicitud = Solicitud_Oferta.objects.create(nombre=nombre, email=email, telefono=telefono)

        # Obtener la última oferta registrada
        ultima_oferta = Nosotros_Oferta.objects.latest('fecha_creacion')

        # Relacionar la solicitud con la última oferta
        solicitud.oferta_relacionada = ultima_oferta
        solicitud.save()

        # Enviar la solicitud por correo electrónico
        solicitud.enviar_solicitud_por_correo()

        # Mostrar un mensaje de éxito
        messages.success(request, 'Solicitud de oferta enviada con éxito.')

        # Redireccionar a la misma página o a cualquier otra deseada
        return JsonResponse({'success': True})  # 
    
    nosotros = Nosotros.objects.first()
    
    # Obtener los últimos 4 servicios
    servicios = Nosotros_Servicios.objects.all().order_by('-fecha_creacion')[:4]
    
    # Obtener la última oferta registrada
    #ultima_oferta = Nosotros_Oferta.objects.latest('fecha_creacion')
    try:
        # Intenta obtener la última oferta registrada
        ultima_oferta = Nosotros_Oferta.objects.latest('fecha_creacion')
    except Nosotros_Oferta.DoesNotExist:
        # Maneja la excepción si no hay ninguna oferta registrada
        raise Http404("No hay ofertas registradas en este momento.")
    
    
    context={
        'services':services,
        'teams_bar':teams_bar[:4],  #mostrando solo
        #los primeros 4 equipos en la barra de info
        'data_contact':data_contact,
        'urls_info':urls_info,
        'ultima_descripcion': ultima_descripcion,
        'barra_principal':barra_principal,
        'urls_interes':urls_interes,
        'ultima_oferta': ultima_oferta,
        'nosotros': nosotros,
        'servicios': servicios,
        'ultima_oferta': ultima_oferta,
        }

    # Renderizar la plantilla 'index.html' con la lista de tours
    return render(request, 'nosotros.index.html', context )


