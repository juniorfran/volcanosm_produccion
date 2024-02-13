from django.http import Http404, JsonResponse
from django.shortcuts import render
from Configuraciones.models import Barra_Principal, Contacts, Direccionamiento, General_Description, Services_Bar, Team_bar, Urls_info, Urls_interes
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Generalidades, Nosotros, Nosotros_Servicios, Solicitud_Oferta, Nosotros_Oferta



# Create your views here.
def nosotros_index(request):
    
    
    services = Services_Bar.objects.filter(services_visible=True)  # Filtra los servicios visibles y Obtener todos los services bar
    teams_bar = Team_bar.objects.all().order_by("id") #obetner todos los teams
    ultima_descripcion = General_Description.objects.latest('fecha_creacion') # Obtén la última descripción general
    barra_principal = Barra_Principal.objects.latest('fecha_creacion') # obtener la barra principal
    data_contact = Contacts.objects.latest() #obtener todos los datos de contacto
    urls_info = Urls_info.objects.all() #obtener todas las url de informacion
    urls_interes = Urls_interes.objects.all() #urls de interes
    
    #formulario de solicitud de oferta
    if request.method == 'POST':
        # Procesar el formulario enviado
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        solicitud = Solicitud_Oferta.objects.create(nombre=nombre, email=email, telefono=telefono) # Crear una nueva solicitud de oferta
        ultima_oferta = Nosotros_Oferta.objects.latest('fecha_creacion') # Obtener la última oferta registrada
        solicitud.oferta_relacionada = ultima_oferta # Relacionar la solicitud con la última oferta
        solicitud.save()

        
        solicitud.enviar_solicitud_por_correo() # Enviar la solicitud por correo electrónico        
        messages.success(request, 'Solicitud de oferta enviada con éxito.') # Mostrar un mensaje de éxito
        return JsonResponse({'success': True})  # Redireccionar a la misma página o a cualquier otra deseada
    
    nosotros = Nosotros.objects.first()
    servicios = Nosotros_Servicios.objects.all().order_by('-fecha_creacion')[:4] # Obtener los últimos 4 servicios
    
    ultima_oferta = Nosotros_Oferta.objects.latest('fecha_creacion') # Obtener la última oferta registrada
    # try:
    #     # Intenta obtener la última oferta registrada
    #     ultima_oferta = Nosotros_Oferta.objects.latest('fecha_creacion')
    # except Nosotros_Oferta.DoesNotExist:
    #     # Maneja la excepción si no hay ninguna oferta registrada
    #     raise Http404("No hay ofertas registradas en este momento.")
    
    #en el caso de que estado_oferta de Nosotros_Oferta este True se veran las ofertas de lo contrarios no se veran
    
    titulo = "Nosotros"
    direccion_actual = "nosotros"
    
    conf_direccionamiento = Direccionamiento.objects.latest('fecha_creacion')
    
    
    context={
        'titulo':titulo,
        'direccion_actual':direccion_actual,
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
        'direccionamiento':conf_direccionamiento,
        }

    # Renderizar la plantilla 'index.html' con la lista de tours
    return render(request, 'nosotros.index.html', context )


def mostrar_ultimos_terminos(request):
     
    ultima_descripcion = General_Description.objects.latest('fecha_creacion') # Obtén la última descripción general
    barra_principal = Barra_Principal.objects.latest('fecha_creacion') # obtener la barra principal
    data_contact = Contacts.objects.latest() #obtener todos los datos de contacto
    urls_info = Urls_info.objects.all() #obtener todas las url de informacion
    urls_interes = Urls_interes.objects.all() #urls de interes
    
    titulo = "Terminos y Condiciones"
    direccion_actual = "Terminos y Condiciones"
    
    conf_direccionamiento = Direccionamiento.objects.latest('fecha_creacion')
    
    
    # Obtenemos el último registro de Generalidades
    ultimo_termino = Generalidades.objects.latest('fecha_creacion')
    
    context={
        'titulo':titulo,
        'direccion_actual':direccion_actual,
        'data_contact':data_contact,
        'urls_info':urls_info,
        'ultima_descripcion': ultima_descripcion,
        'barra_principal':barra_principal,
        'urls_interes':urls_interes,
        'direccionamiento':conf_direccionamiento,
        'generalidades': ultimo_termino
        }
    
    return render(request, 'terminos_condiciones.html', context)

def politicas_mision_vision(request):
     
    ultima_descripcion = General_Description.objects.latest('fecha_creacion') # Obtén la última descripción general
    barra_principal = Barra_Principal.objects.latest('fecha_creacion') # obtener la barra principal
    data_contact = Contacts.objects.latest() #obtener todos los datos de contacto
    urls_info = Urls_info.objects.all() #obtener todas las url de informacion
    urls_interes = Urls_interes.objects.all() #urls de interes
    
    titulo = "Terminos y Condiciones"
    direccion_actual = "Terminos y Condiciones"
    
    conf_direccionamiento = Direccionamiento.objects.latest('fecha_creacion')
    
    
    # Obtenemos el último registro de Generalidades
    generalidades = Generalidades.objects.latest('fecha_creacion')
    
    context={
        'titulo':titulo,
        'direccion_actual':direccion_actual,
        'data_contact':data_contact,
        'urls_info':urls_info,
        'ultima_descripcion': ultima_descripcion,
        'barra_principal':barra_principal,
        'urls_interes':urls_interes,
        'direccionamiento':conf_direccionamiento,
        'generalidades': generalidades
        }
    
    return render(request, 'politicas.html', context)