from django.conf import settings
from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.core.mail import EmailMultiAlternatives
import qrcode
from io import BytesIO
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# imagen para el cuadro de informacion sobre nosotros
def upload_to_nosotros(instance, filename):
    # La función toma la instancia del modelo y el nombre del archivo y construye la ruta de almacenamiento
    return f'nosotros/nosotros/{filename}'

#Modelo de la pagina nosotros
class Nosotros(models.Model):
    titulo = models.CharField("Titulo", max_length=100)
    subtitulo = models.CharField("Subtitulo", max_length=100)
    descripcion = models.TextField("Descripción")
    imagen = models.ImageField(upload_to=upload_to_nosotros, blank=False, null=False)
    imagen_pequena_1 = models.ImageField(upload_to=upload_to_nosotros, blank=False, null=False)
    imagen_pequena_2 = models.ImageField(upload_to=upload_to_nosotros, blank=False, null=False)
    texto_boton = models.CharField(max_length=50)
    url_boton = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Nosotros"
        verbose_name_plural = "Nosotros"
        def __str__(self):
            return self.titulo  # String a mostrar en las vistas
        
#imagen para la parte de servicios
def upload_to_servicios(instance, filename):
    # La función toma la instancia del modelo y el nombre del archivo y construye la ruta de almacenamiento
    return f'nosotros/servicios/{filename}'

#modelo que se encarga de los servicios ofrecidos por la empresa
class Nosotros_Servicios(models.Model):
    servicio_titulo = models.CharField( max_length=50)
    servicio_descripcion = models.TextField()
    Servicio_icono = models.ImageField(upload_to=upload_to_servicios, height_field=None, width_field=None, max_length=None)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    #funcion str
    def __str__(self):
        return self.servicio_titulo

#seccion de oferta
class Nosotros_Oferta(models.Model):
    titulo_oferta = models.CharField(max_length=50)
    porcentaje_descuento = models.CharField(max_length=50)
    servicio_descuento = models.CharField(max_length=50)
    descripcion = models.TextField()
    detalle_1 = models.CharField(max_length=50)
    detalle_2 = models.CharField(max_length=50)
    detalle_3 = models.CharField(max_length=50)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
#detalles para el formulario de solicitud de descuento
class Solicitud_Oferta(models.Model):
    # Relación con la sección de oferta
    oferta_relacionada = models.ForeignKey(Nosotros_Oferta, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField( max_length=150)
    email = models.EmailField(max_length=254)
    telefono = models.CharField(max_length=15)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    #enviar estos datos por correo electronico a solitudes@metrocuadrado.com.sv
    def enviar_solicitud_por_correo(self):
        # Obtener la última oferta registrada
        ultima_oferta = Nosotros_Oferta.objects.latest('fecha_creacion')

        # Construir el mensaje del correo electrónico utilizando una plantilla si es necesario
        subject = 'Nueva Solicitud de Oferta'
        
        # Renderizar el contenido del correo utilizando un template
        context = {
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'fecha_creacion': self.fecha_creacion,
            'oferta_titulo': ultima_oferta.titulo_oferta if ultima_oferta else None,
            'porcentaje_descuento': ultima_oferta.porcentaje_descuento if ultima_oferta else None,
            'servicio_descuento': ultima_oferta.servicio_descuento if ultima_oferta else None,
            'descripcion_oferta': ultima_oferta.descripcion if ultima_oferta else None,
            'detalle_1_oferta': ultima_oferta.detalle_1 if ultima_oferta else None,
            'detalle_2_oferta': ultima_oferta.detalle_2 if ultima_oferta else None,
            'detalle_3_oferta': ultima_oferta.detalle_3 if ultima_oferta else None,
        }

        html_content = render_to_string('email/correo_solicitud_oferta.html', context)
        text_content = strip_tags(html_content)

        # Enviar el correo electrónico
        send_mail(subject, text_content, settings.DEFAULT_FROM_EMAIL, ['juniorfran@hotmail.es'], html_message=html_content)
    
    
    
    
    
    

                             
