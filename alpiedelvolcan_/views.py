from django.shortcuts import render
from Tours.models import Tour
from Configuraciones.models import Barra_Principal, CarruselInicio, Services_Bar, Team_bar, Contacts, Urls_info, Urls_interes, General_Description

#vista para mostrar la pagina principal
def index(request):
    #obtener los tour por orden de popularidad
    tours = Tour.objects.all()
    
    #obtener la barra principal
    barra_principal = Barra_Principal.objects.latest('fecha_creacion')
    
    #obtener todos los carrusel de incio
    carrusel_incio = CarruselInicio.objects.all()
    
    #Obtener todos los services bar
    services = Services_Bar.objects.filter(services_visible=True)  # Filtra los servicios visibles
    
    #obetner todos los teams
    teams_bar = Team_bar.objects.all().order_by("id")
    
    #obtener todos los datos de contacto
    data_contact = Contacts.objects.latest()
    
    #obtener todas las url de informacion
    urls_info = Urls_info.objects.all()
    
    # Obtén la última descripción general
    ultima_descripcion = General_Description.objects.latest('fecha_creacion')

    #urls de interes
    urls_interes = Urls_interes.objects.all()
    
    
    context={
        'tours':tours,
        'barra_principal':barra_principal,
        'carrusel_incio':carrusel_incio,
        'services':services,
        'teams_bar':teams_bar[:4],  #mostrando solo
        #los primeros 4 equipos en la barra de info
        'data_contact':data_contact,
        'urls_info':urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes':urls_interes,
        }
    
    
    return render(request, 'base.html', context)

#vista para mostrar la pagina principal
def footer(request):
    
    
    data_contact = Contacts.objects.latest()#obtener todos los datos de contacto
    urls_info = Urls_info.objects.all() #obtener todas las url de informacion
    ultima_descripcion = General_Description.objects.latest('fecha_creacion') # Obtén la última descripción general
    urls_interes = Urls_interes.objects.all() #urls de interes
    
    context={
        'data_contact':data_contact,
        'urls_info':urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes':urls_interes,
        }
    
    
    return render(request, 'sections/footer.html', context)


