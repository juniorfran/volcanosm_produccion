from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
#from Transacciones.views import crear_enlace_pago
from Configuraciones.models import Barra_Principal, Contacts, Direccionamiento, General_Description, Urls_info, Urls_interes
from Transacciones.wompi_connect import authenticate_wompi
from Transacciones.wompi_consulta import make_wompi_get_request
from Transacciones.wompi_envio import create_payment_link
from django.conf import settings
from .models import ImagenTour, Resena, Tour, Reserva
from .forms import ResenaForm, ReservaForm
from django.utils import timezone
from Transacciones.models import EnlacePago

Client_id = settings.CLIENT_ID
Client_secret = settings.CLIENT_SECRET


def tours_index(request):
    # Obtener la fecha actual
    fecha_actual = timezone.now()

    # Obtener todos los tours desde la base de datos
    tours = Tour.objects.all()

    # Verificar la disponibilidad de cada tour
    for tour in tours:
        if tour.fecha_inicio <= fecha_actual <= tour.fecha_fin:
            tour.disponible = True
        else:
            tour.disponible = False
            
    titulo = "Nuestros Tours"
    direccion_actual = "tours"

    barra_principal = Barra_Principal.objects.latest('fecha_creacion') # Obtener la barra principal
    data_contact = Contacts.objects.latest() # Obtener todos los datos de contacto
    urls_info = Urls_info.objects.all() # Obtener todas las URL de información
    ultima_descripcion = General_Description.objects.latest('fecha_creacion') # Obtener la última descripción general
    urls_interes = Urls_interes.objects.all() # URLs de interés
    conf_direccionamiento = Direccionamiento.objects.latest('fecha_creacion')

    # Renderizar la plantilla 'show_tours.html' con la lista de tours y otros datos
    context = {
        'titulo':titulo,
        'direccion_actual':direccion_actual,
        'tours': tours,
        'barra_principal': barra_principal,
        'data_contact': data_contact,
        'urls_info': urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes': urls_interes,
        'direccionamiento':conf_direccionamiento,
    }
    return render(request, 'show_tours.html', context)

def tour_detail(request, tour_id):
    tour = Tour.objects.get(pk=tour_id)
    barra_principal = Barra_Principal.objects.latest('fecha_creacion')
    resenas = Resena.objects.filter(tour=tour)
    data_contact = Contacts.objects.latest()
    urls_info = Urls_info.objects.all()
    ultima_descripcion = General_Description.objects.latest('fecha_creacion')
    urls_interes = Urls_interes.objects.all()
    conf_direccionamiento = Direccionamiento.objects.latest('fecha_creacion')

    # Crear una lista con todas las imágenes relacionadas, incluida la principal
    imagenes = [tour.url_azure] + [getattr(imagen_tour, f'url_azure_{i}') for i in range(1, 5) for imagen_tour in ImagenTour.objects.filter(tour=tour)]

    if request.method == 'POST':
        estrellas = int(request.POST.get('rating'))
        comentario = request.POST.get('comentario')

        if estrellas < 1 or estrellas > 5:
            return redirect('tour_detail', tour_id=tour_id)

        resena = Resena.objects.create(tour=tour, estrellas=estrellas, comentario=comentario)
        return redirect('tour_detail', tour_id=tour_id)
    
    context = {
        'tour': tour,
        'imagenes': imagenes,
        'resenas': resenas,
        'barra_principal': barra_principal,
        'data_contact': data_contact,
        'urls_info': urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes': urls_interes,
        'direccionamiento':conf_direccionamiento,
    }

    return render(request, 'detail_tours.html', context)

def reservar_tour(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    tipo_document = Reserva.DOCUMENTOS_VALIDOS

    barra_principal = Barra_Principal.objects.latest('fecha_creacion') #obtener la barra principal
    data_contact = Contacts.objects.latest()#obtener todos los datos de contacto
    urls_info = Urls_info.objects.all() #obtener todas las url de informacion
    ultima_descripcion = General_Description.objects.latest('fecha_creacion') # Obtén la última descripción general
    urls_interes = Urls_interes.objects.all() #urls de interes  
    
    
    if request.method == 'POST':
        # Obtén los datos del formulario directamente del request.POST
        nombre = request.POST.get('nombre')
        dui = request.POST.get('dui')
        correo_electronico = request.POST.get('correo_electronico')
        direccion = request.POST.get('direccion')
        # Obtén los datos del formulario directamente de request.POST
        cantidad_adultos = int(request.POST.get('cantidad_adultos'))
        #cantidad_ninos = int(request.POST.get('cantidad_ninos'))
        fecha_reserva = request.POST.get('fecha_reserva')
        
        #nuevo campos agregados
        telefono = request.POST.get("telefono")
        pais_residencia = request.POST.get("pais_residencia")
        tipo_documento = request.POST.get("tipo_documento")
        
        # Obtener los precios de adulto y nino del tour
        precio_adulto = tour.precio_adulto
        precio_nino = tour.precio_nino

        reserva = Reserva(
            tour=tour,
            nombre=nombre,
            dui=dui,
            correo_electronico=correo_electronico,
            direccion=direccion,
            cantidad_adultos=cantidad_adultos,
            #cantidad_ninos=cantidad_ninos,
            fecha_reserva=fecha_reserva,
            precio_adulto=precio_adulto,
            precio_nino=precio_nino,
            telefono=telefono,
            pais_residencia=pais_residencia,
            tipo_documento=tipo_documento,
        )
        reserva.save()
        
        # Obtén la instancia de Reserva después de guardarla en la base de datos
        reserva_instance = Reserva.objects.get(pk=reserva.id)
        
        # #obtener la imagen de tour
        # imagen_tour = tour.imagen
        
        # #construir la url de la imagen del tour
        # url_imagen_tour = imagen_tour.url
        # #verificar que la url tenga el formato correcto
        # if url_imagen_tour and not url_imagen_tour.startswith(("http://", "https://")):
        #url_imagen_tour = "https://codigogenesis.com/genesis/2022/04/imagen-placeholder-por-defecto-WooCommerce.png"
        url_imagen_tour = tour.url_azure
        print("Esta es la url que obtengo  en depuracion: ",url_imagen_tour)

        # Asigna el valor de reserva_id después de obtener la instancia
        reserva_id = reserva_instance.id
        
        # Autenticarse y obtener el token
        access_token = authenticate_wompi(Client_id, Client_secret)

        if access_token:
            # Hacer una consulta utilizando el token
            consulta_result = make_wompi_get_request("EnlacePago", access_token)

            if consulta_result:
                print("Consulta exitosa:")
                #print(consulta_result)

        client_id = Client_id
        client_secret = Client_secret
        
        comercio_id = reserva.codigo_reserva
        monto = float(reserva.precio_adulto)
        nombre_producto = tour.titulo
        descripcion_Producto = tour.descripcion
        imagenProducto = str(url_imagen_tour)
        cantidad = reserva.cantidad_adultos

        # Llama a la función para crear el enlace de pago
        enlace_pago = create_payment_link(
            reserva_id,
            client_id,
            client_secret,
            comercio_id,
            monto,
            nombre_producto,
            descripcion_Producto,
            imagenProducto,
            cantidad
            )
    
        # Redirige a la página de éxito y pasa el reserva_id como parámetro
        return redirect('reserva_exitosa', reserva_id=reserva.id)
    # Renderiza el formulario para el método GET
    
    context = {
        'barra_principal':barra_principal,
        'data_contact':data_contact,
        'urls_info':urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes':urls_interes,
        'tour': tour,
        'tipo_document':tipo_document,
        
    }
    
    return render(request, 'reservar_tour.html', context)


def reserva_exitosa(request, reserva_id):
    reserva = Reserva.objects.get(pk=reserva_id)
        #obtener todos los datos de contacto
    data_contact = Contacts.objects.latest()
    barra_principal = Barra_Principal.objects.latest('fecha_creacion') #obtener la barra principal
    data_contact = Contacts.objects.latest()#obtener todos los datos de contacto
    urls_info = Urls_info.objects.all() #obtener todas las url de informacion
    ultima_descripcion = General_Description.objects.latest('fecha_creacion') # Obtén la última descripción general
    urls_interes = Urls_interes.objects.all() #urls de interes
    

    # Obtener todos los enlaces de pago asociados a la reserva
    enlace_pago = EnlacePago.objects.get(reserva=reserva)

    
    #urls de interes
    urls_interes = Urls_interes.objects.all()
    
    context = {
        'barra_principal':barra_principal,
        'data_contact':data_contact,
        'urls_info':urls_info,
        'ultima_descripcion': ultima_descripcion,
        'urls_interes':urls_interes,
        'reserva': reserva,
        'enlace_pago': enlace_pago,
    }

    return render(request, 'reserva_exitosa.html', context)


