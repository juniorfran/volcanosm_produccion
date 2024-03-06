from datetime import datetime
from django.utils import timezone
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
from django.conf import settings
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
from ckeditor.fields import RichTextField
from azure.storage.blob import ContentSettings
from azure.communication.email import EmailClient
# from Transacciones.models import EnlacePago


#modelos para tours
class TipoTour(models.Model):
    nombre = models.CharField(max_length=20)
    def __str__(self):
        return self.nombre

class Tour(models.Model):
    titulo = models.CharField(max_length=50, unique=True)
    descripcion = RichTextField()  # Cambiado a TextField
    descripcion1 = RichTextField() # Cambiado a TextField
    descripcion2 = RichTextField()  # Cambiado a TextField
    precio_adulto = models.DecimalField(max_digits=10, decimal_places=2)
    precio_nino = models.DecimalField(max_digits=10, decimal_places=2)
    duracion = models.PositiveIntegerField()
    iva = models.BooleanField(default=False)
    incluye_tour = RichTextField()  # Cambiado a TextField
    imagen = models.ImageField(upload_to='tours')  
    url_azure = models.URLField(max_length=400, blank=True, null=True)
    tipo_tour = models.ForeignKey(TipoTour, on_delete=models.SET_NULL, null=True, blank=True)
    
    
    # Nuevo campo para el rango de fechas disponibles
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Conexión al servicio Blob de Azure
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER_NAME)

        if self.imagen:
            fecha_actual = timezone.now()
            ruta_carpeta = f"tours/{fecha_actual.year}/{fecha_actual.month}/{fecha_actual.day}/"
            blob_name = f"{self.id}_imagen_{os.path.basename(self.imagen.name)}"
            ruta_imagen = os.path.join(ruta_carpeta, blob_name)

            blob_client = container_client.get_blob_client(ruta_imagen)
            if not blob_client.exists():
                with open(self.imagen.path, "rb") as data:
                    blob_client.upload_blob(data, content_settings=ContentSettings(content_disposition=None, content_type="image/jpeg"))
                self.url_azure = blob_client.url
    
        super().save(*args, **kwargs)

    def obtener_imagen_principal(self):
        return self.url_azure
    
    def __str__(self):
        return f"{self.titulo} - ${self.precio_adulto:.2f}"

def get_upload_path(instance, filename):
    # Obtiene el nombre del modelo y el ID de la instancia
    model_name = instance.__class__.__name__
    model_id = instance.id

    # Construye la ruta de la carpeta con el nombre del modelo y el ID
    folder_path = f"{model_name}/{model_id}/"

    # Combina la ruta de la carpeta con el nombre del archivo
    return os.path.join(folder_path, filename)

class ImagenTour(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='imagenes')
    imagen1 = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    imagen2 = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    imagen3 = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    imagen4 = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    url_azure_1 = models.CharField(max_length=255, blank=True, null=True)
    url_azure_2 = models.CharField(max_length=255, blank=True, null=True)
    url_azure_3 = models.CharField(max_length=255, blank=True, null=True)
    url_azure_4 = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Conexión al servicio Blob de Azure
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER_NAME)

        # Guardar cada imagen en Azure y obtener sus URLs
        for i in range(1, 5):  # Iterar sobre las 4 imágenes
            field_name = f'imagen{i}'
            url_field_name = f'url_azure_{i}'
            imagen = getattr(self, field_name)
            url_field = getattr(self, url_field_name)

            if imagen:
                # Generar un nombre único para la imagen en Azure
                blob_name = f"{self.id}_{field_name}_{os.path.basename(imagen.name)}"

                # Verificar si el blob ya existe antes de subirlo
                blob_client = container_client.get_blob_client(blob_name)
                if not blob_client.exists():
                    # Si el blob no existe, subir la imagen y obtener la URL
                    blob_client.upload_blob(imagen)
                    setattr(self, url_field_name, blob_client.url)
                else:
                    # Si el blob ya existe, obtener la URL existente
                    setattr(self, url_field_name, blob_client.url)

        # Guardar la instancia del modelo una vez que se han procesado todas las imágenes
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Imágenes del tour {self.tour.titulo}"

    class Meta:
        verbose_name_plural = "Imágenes de Tours"
    
class Resena(models.Model):
    tour = models.ForeignKey(Tour, related_name='resenas', on_delete=models.CASCADE)
    estrellas = models.PositiveIntegerField()
    comentario = RichTextField()

    def __str__(self):
        return f"Reseña para {self.tour.titulo}"
    
class Reserva(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='reservas')
    codigo_reserva = models.CharField(max_length=85, unique=True)
    nombre = models.CharField(max_length=255)
    dui = models.CharField(max_length=10)  # Asumiendo que el DUI tiene 10 dígitos
    correo_electronico = models.EmailField()
    direccion = RichTextField()
    cantidad_adultos = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    cantidad_ninos = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    fecha_reserva = models.DateField(editable=True)
    qr_code_url = models.URLField(blank=True)
    qr_code = models.ImageField(upload_to='qrcodes', blank=True, null=True)
    
    
    #campos extras
    #lista de tipos de documentos
    DOCUMENTOS_VALIDOS = (
        (' ', ' '),
        ('DUI', 'Documento Unico de Identidad'),
        ('CE', 'Cédula de extrangería'),
        ('LIC', 'Licencia Nacional'),
        ('PA', 'Pasaporte'),
        ('Otro', 'Otro'),
        )
    tipo_documento = models.CharField(max_length=50, choices=DOCUMENTOS_VALIDOS)
    telefono = models.CharField(max_length=15)
    pais_residencia = models.CharField(max_length=50, default="El Salvador")
    
     # Nuevos campos para el total a pagar y el iva
    precio_adulto = models.DecimalField(max_digits=10, decimal_places=2)
    precio_nino = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    total_pagar = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    

    def __str__(self):
        return f"{self.nombre} - {self.tour.titulo}"

    def save(self, *args, **kwargs):
        # Calcular el total a pagar antes de guardar la reserva
        
        if self.tour.iva == True:
            total_sin_iva = self.cantidad_adultos * self.precio_adulto
            iva_calculado = total_sin_iva * Decimal('0.13')  # Calcular el valor del IVA
            self.iva = iva_calculado
            self.total_pagar = total_sin_iva + iva_calculado  # Sumar el IVA al total a pagar
        else:
            total_sin_iva = self.cantidad_adultos * self.precio_adulto
            self.total_pagar = total_sin_iva
        
        # Generar código de reserva único antes de guardar
        if not self.codigo_reserva:
            self.codigo_reserva = self.generar_codigo_reserva()
            self.enviar_codigo_por_correo()  # Envía el código por correo al crear la reserva
        
        super().save(*args, **kwargs)

    def generar_codigo_reserva(self):
        import random
        from datetime import datetime

        # Obtén la fecha actual en formato YYYYMMDD
        fecha_actual = datetime.now().strftime("%Y%m")

        # Genera un número correlativo desde 001
        correlativo = str(random.randint(1, 9999)).zfill(4)

        # # Si fecha_reserva es una cadena, conviértela a un objeto datetime
        # if isinstance(self.fecha_reserva, str):
        #     self.fecha_reserva = datetime.strptime(self.fecha_reserva, "%m")

        # Combina los elementos para formar el código de reserva
        codigo = f"re-{fecha_actual}f{self.dui}{correlativo}"

        return codigo
    
    def guardar_qr_code_image(self, qr_io):
        from django.core.files.base import ContentFile

        # Guarda la imagen en el sistema de archivos
        image_name = f"qrcode_{self.codigo_reserva}.png"
        self.qr_code.save(image_name, ContentFile(qr_io.getvalue()), save=False)
        self.save()

        # Obtén la URL de la imagen
        return self.qr_code.url

    def enviar_codigo_por_correo(self):
        try:
            # Configuración de la conexión al servicio de correo electrónico de Azure
            connection_string = "endpoint=https://emailvolcanosm.unitedstates.communication.azure.com/;accesskey=SkW7u9s6sgjkska6ncJ8iOQutZdU1f+iIH9rfMto3j+NFLi8bpmcM4PF+4oJ3A+gQkAOXVFvhxaNqa8UTdtcUg=="
            client = EmailClient.from_connection_string(connection_string)

            # Genera el código QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.codigo_reserva)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Guarda el código QR en un BytesIO
            qr_io = BytesIO()
            img.save(qr_io)
            qr_io.seek(0)

            # Renderiza el contenido del correo utilizando un template
            context = {
                'tour_titulo': self.tour.titulo,
                'codigo_reserva': self.codigo_reserva,
                'nombre': self.nombre,
                'dui': self.dui,
                'tipo_documento': self.tipo_documento,
                'telefono': self.telefono,
                'correo_electronico': self.correo_electronico,
                'pais_residencia': self.pais_residencia,
                'direccion': self.direccion,
                'cantidad_adultos': self.cantidad_adultos,
                'cantidad_ninos': self.cantidad_ninos,
                'fecha_reserva': self.fecha_reserva,
                'total_pagar': self.total_pagar
            }
            html_content = render_to_string('email/correo_reserva.html', context)
            text_content = strip_tags(html_content)

            # Configuración del mensaje
            message = {
                "senderAddress": settings.EMAIL_HOST_USER,  # Reemplaza con el remitente real
                "recipients": {
                    "to": [
                        {"address": self.correo_electronico},
                        {"address": "volcanosanmiguel.sv@gmail.com"}
                        ],
                },
                "content": {
                    "subject": "Código de Reserva para el Tour",
                    "html": html_content,
                    "plainText": text_content,
                }
            }

            # Envía el correo electrónico utilizando el servicio de correo electrónico de Azure
            poller = client.begin_send(message)
            result = poller.result()

        except Exception as ex:
            print(ex)