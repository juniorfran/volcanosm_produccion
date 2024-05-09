from django.shortcuts import render
from .models import Servicios
from Tours.models import Tour
from Configuraciones.models import Barra_Principal, Contacts, Direccionamiento, General_Description, Urls_info, Urls_interes

# Create your views here.
def index_servicios(request):
    servicio = Servicios.objects.first()
    # Obtener los servicios ordenados por fecha de creación de forma descendente
    servicios = Servicios.objects.all().order_by('-fecha_creacion')
    tours = Tour.objects.all().order_by('-tipo_tour')
    barra_principal = Barra_Principal.objects.latest('fecha_creacion') #obtener la barra principal
    data_contact = Contacts.objects.latest()#obtener todos los datos de contacto
    urls_info = Urls_info.objects.all() #obtener todas las url de informacion
    ultima_descripcion = General_Description.objects.latest('fecha_creacion') # Obtén la última descripción general
    urls_interes = Urls_interes.objects.all() #urls de interes
    
    titulo = "Nuestros Servicios"
    direccion_actual = "servicios"
    conf_direccionamiento = Direccionamiento.objects.latest('fecha_creacion')
    
    
    context = {
        'servicio': servicio,
        'servicios': servicios,
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
    
    
    return render(request, 'servicios_list.html', context)