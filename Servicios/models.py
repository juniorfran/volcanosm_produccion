from datetime import datetime
from decimal import Decimal
import os
from django.db import models
from django.core.validators import MinValueValidator
from django.core.mail import EmailMultiAlternatives
import qrcode
from io import BytesIO
from alpiedelvolcan_ import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.conf import settings
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
from ckeditor.fields import RichTextField
# Create your models here.


#modelo para tipos de servicios

class TipoServicio(models.Model):
    nombre = models.CharField("Nombre", max_length=50)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.nombre

class Servicios(models.Model):
    tipo = models.ForeignKey(TipoServicio, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=70)
    descripcion = RichTextField()
    imagen = models.ImageField(upload_to='servicios/{nombre}')
    url_azure = models.CharField(max_length=255, blank=True, null=True)  # Solo una URL para la imagen en Azure
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Conexión al servicio Blob de Azure
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER_NAME)

        if self.imagen:
            # Obtener la fecha actual
            fecha_actual = datetime.now()
            # Generar la ruta para la carpeta basada en la fecha
            ruta_carpeta = f"tours/{fecha_actual.year}/{fecha_actual.month}/{fecha_actual.day}/"
            
            # Generar un nombre único para la imagen en Azure
            blob_name = f"{self.id}_imagen_{os.path.basename(self.imagen.name)}"
            # Concatenar la ruta de la carpeta con el nombre de la imagen
            ruta_imagen = os.path.join(ruta_carpeta, blob_name)

            # Verificar si el blob ya existe antes de subirlo
            blob_client = container_client.get_blob_client(ruta_imagen)
            if not blob_client.exists():
                # Si el blob no existe, subir la imagen
                with open(self.imagen.path, "rb") as data:
                    blob_client.upload_blob(data)
                # Actualizar la URL de la imagen en Azure
                self.url_azure = blob_client.url
    
        # Guardar el objeto una vez finalizado el proceso
        super().save(*args, **kwargs)

    def obtener_imagen_principal(self):
        return self.imagen.url


def imagen_servicio_upload_to(instance, filename):
    today = datetime.now()
    date_folder = today.strftime('%Y/%m/%d')
    filename_base, filname_ext = os.path.splitext(filename)
    new_filname = f'{instance.nombre}_{instance.id}{filname_ext}'
    return os.path.join('servicio', date_folder, new_filname)

def get_upload_path(instance, filename):
    # Obtiene el nombre del modelo y el ID de la instancia
    model_name = instance.__class__.__name__
    model_id = instance.id
    # Construye la ruta de la carpeta con el nombre del modelo y el ID
    folder_path = f"{model_name}/{model_id}/"
    # Combina la ruta de la carpeta con el nombre del archivo
    return os.path.join(folder_path, filename)

class ImagenesServicio(models.Model):
    servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE, related_name='imagenes')
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
        return f"Imágenes del servicio {self.servicio.nombre}"


    
    
    
#####################################################################################
# LA SIGUIENTE LOGICA SE UTILIZARE EN POSTERIOR PROYECTO DE POS
# EN ESTE EL CLINETE SOLO QUIERE PODER MOSTRAR LOS SERVICIOS QUE EL PROPORCIONA
# NO SE QUIERE MODELOS DE RESERVA Y CONTRATACION.
#####################################################################################
    
#####################################################################################
# MODELO PARA CAMPING
#####################################################################################


def imagen_camping_upload_to(instance, filename):
    # Obtener la fecha actual
    today = datetime.now()
    # Carpeta para la fecha de creación
    date_folder = today.strftime('%Y/%m/%d')
    # Nombre del archivo
    filename_base, filename_ext = os.path.splitext(filename)
    # Regenerar el nombre del archivo para evitar colision3es
    new_filename = f"{instance.nombre}_{instance.id}{filename_ext}"
    # Retorna la ruta completa
    return os.path.join('camping', date_folder, new_filename)


class ImagenesCamping(models.Model):
    titulo = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to=imagen_camping_upload_to)

    def __str__(self):
        return f"{self.titulo}"

    class Meta:
        verbose_name_plural = "Imágenes de Cabaña"

class Camping(models.Model):
    nombre = models.CharField(max_length=100)
    #relaicon con TIpoServicio
    tipo_servicio = models.ForeignKey(TipoServicio, on_delete=models.SET_NULL, null=True, blank=True)
    capacidad_personas = models.PositiveIntegerField()
    costo_por_persona = models.DecimalField(max_digits=10, decimal_places=2)
    tienda_camping = models.BooleanField()
    derecho_camping = models.DecimalField(max_digits=5, decimal_places=2)
    costo_parqueo = models.DecimalField( max_digits=5, decimal_places=2)
    horas_parqueo = models.DecimalField( max_digits=5, decimal_places=2)

    def __str__(self):
        return self.nombre
    
#modelo reserva
class ReservaCamping (models.Model):
    camping = models.ForeignKey(Camping, on_delete=models.CASCADE)
    codigo_reserva = models.CharField(max_length=85, unique=True)
    nombre = models.CharField(max_length=255)
    dui = models.CharField(max_length=10)  # Asumiendo que el DUI tiene 10 dígitos
    correo_electronico = models.EmailField()
    direccion = RichTextField()
    cantidad_adultos = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    cantidad_ninos = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    qr_code_url = models.URLField(blank=True)
    qr_code = models.ImageField(upload_to='qrcodes', blank=True, null=True)
    fecha_inicio = models.DateField('Fecha Inicio')
    fecha_fin = models.DateField('Fecha Fin')
    
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
        return  f"Reserva del Camping {self.camping} para {self.nombre}"
    
    def save(self, *agrs, **kwargs):
        #calcular el total a pagar antes de aguardar la reserva
        if self.tour.iva == True:
            total_sin_iva = self.cantidad_adultos * self.precio_adulto
            iva_calculado = total_sin_iva * Decimal('0.13')  # Calcular el valor del IVA
            self.iva = iva_calculado
            self.total_pagar = total_sin_iva + iva_calculado  # Sumar el IVA al total a pagar
        else:
            total_sin_iva = self.cantidad_adultos * self.precio_adulto
            self.total_pagar = total_sin_iva
        
        
        #generar codigo de reserva unico antes de guardar
        if not self.codigo_reserva:
            self.codigo_reserva = self.generar_codigo_reserva()
            self.enviar_codigo_por_correo()
        
        super().save(*agrs, **kwargs)
        
    #generar codigo de reserva
    def generar_codigo_reserva(self):
        import random
        from datetime import datetime
        
        #oetner la fecha actual en formato yyymmdd
        fecha_actual = datetime.now().strftime("%Y%m%d")
        
        #genera run numero correlativo desde 0001
        correlativo  = str(random.randint(1, 9999)).zfill(4)
        
        #si la fecha de reserva es una cadena convertirla en datetime objeto
        if isinstance(self.fecha_reserva, str):
            self.fecha_reserva = datetime.strptime(self.fecha_reserva, "%Y-%m-%d")
        
        #combinar los elementos para formar el codigo
        codigo = f"re-fa{fecha_actual}-fr{self.fecha_reserva.strftime('%d%Y%m')}-c{correlativo}"
        
        return codigo
    
    def guardar_qr_code_image(self, qr_io):
        from django.core.files.base import ContentFile
        
        #GUARDAR LA IMAGEN EN EL SISTEMA DE ARCHIVOS
        imagen_name = f"qrcode_{self.codigo_reserva}.png"
        self.qr_code.save(imagen_name, ContentFile(qr_io.getvalue()), save=False)
        self.save
        
        return self.qr_code.url
    
    
    # enviar el codigo qr por correo
    def enviar_codigo_por_correo(self):
        qr = qrcode.QRCode(
            version = 1,
            error_correction = qrcode.constants.ERROR_CORRECT_,
            box_size = 10,
            border = 4,
        )
        
        info_qr={
            'codigo de reserva':self.codigo_reserva,
            'nombre del cliente':self.nombre,
            'email del cliente':self.correo_electronico,
            'telefono del cliente':self.telefono,
            'direccion del cliente':self.direccion,
            'cantidad de adultos':self.cantidad_adultos,
            'iva': self.iva,
            'total a pagar': self.total_pagar,
            
        }
        
        qr.add_data(info_qr)
        qr.make(fit=True)
        img = qr.make_image(fill_color = "blue", back_color="white")
        
        # Guardar el qr en un bytesIO
        qr_io = BytesIO()
        img.save(qr_io)
        qr_io.seek(0)
        
        # guardar el codigo QR en la bse  de datos y obtener su url para enviar por correo electronico
        self.qr_code_url = self.guardar_qr_code_image(qr_io)
        
        # enviar el codigo de reserva y el codigo qr por correo
        subject = "Codigo de reserva para el toru"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email=[self.correo_electronico]
        
        # Renderiza el contenido del correo utilizando un template
        context = {
            'tour_titulo': self.camping.nombre,
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
        html_content = render_to_string('email/correo_reserva_camping.html', context)
        text_content = strip_tags(html_content)

        # Adjunta la imagen del código QR al mensaje
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.attach(f"qrcode_{self.codigo_reserva}.png", qr_io.getvalue(), "image/png")

        # Adjunta la URL del código QR al mensaje
        msg.attach(f"qrcode_url_{self.codigo_reserva}.txt", self.qr_code_url)

        # Envía el correo
        msg.send()
        
        
        
        
       
#####################################################################################
# MODELOS PARA CABAÑIAS
#####################################################################################

def icono_upload_to(instance, filename):
    # Obtener la fecha actual
    today = datetime.now()
    # Carpeta para la fecha de creación
    date_folder = today.strftime('%Y/%m/%d')
    # Nombre del archivo
    filename_base, filename_ext = os.path.splitext(filename)
    # Regenerar el nombre del archivo para evitar colisiones
    new_filename = f"{instance.nombre}_{instance.id}{filename_ext}"
    # Retorna la ruta completa
    return os.path.join('comodidades', date_folder, new_filename)

def imagen_cabania_upload_to(instance, filename):
    # Obtener la fecha actual
    today = datetime.now()
    # Carpeta para la fecha de creación
    date_folder = today.strftime('%Y/%m/%d')
    # Nombre del archivo
    filename_base, filename_ext = os.path.splitext(filename)
    # Regenerar el nombre del archivo para evitar colisiones
    new_filename = f"{instance.nombre}_{instance.id}{filename_ext}"
    # Retorna la ruta completa
    return os.path.join('cabañas', date_folder, new_filename)

class Comodidad(models.Model):
    nombre = models.CharField(max_length=100)
    icono = models.ImageField(upload_to=icono_upload_to)

    def __str__(self):
        return f"Comodidad: {self.nombre}"
    
class ImagenesCabania(models.Model):
    titulo = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to=imagen_cabania_upload_to)

    def __str__(self):
        return f"{self.titulo}"

    class Meta:
        verbose_name_plural = "Imágenes de Cabaña"

class Cabanias(models.Model):
    nombre = models.CharField(max_length=100)
    tipo_servicio = models.ForeignKey(TipoServicio, on_delete=models.SET_NULL, null=True, blank=True)
    ubicacion = models.CharField(max_length=200)
    descripcion = RichTextField()
    descripcion1 = RichTextField()
    capacidad_personas = models.PositiveIntegerField()
    costo_por_noche = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.BooleanField(default=False)
    incluye_cabania = RichTextField()
    comodidades = models.ManyToManyField(Comodidad)
    imagen = models.ImageField(upload_to='cabañas')
    imagenes = models.ManyToManyField(ImagenesCabania)

    def obtener_imagen_principal(self):
        return self.imagen.url

    def __str__(self):
        return f"{self.nombre} - ${self.costo_por_noche}"
        
class Resena_cabanias(models.Model):
    cabania = models.ForeignKey(Cabanias, related_name='resenas', on_delete=models.CASCADE)
    estrellas = models.PositiveIntegerField()
    comentario = RichTextField()

    def __str__(self):
        return f"Reseña para {self.cabania.nombre}"

