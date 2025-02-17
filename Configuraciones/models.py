from django.db import models
import os
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from ckeditor.fields import RichTextField
from azure.storage.blob import ContentSettings
from alpiedelvolcan_ import settings
from django.utils import timezone

# Create your models here.

class wompi_config (models.Model):
    cuenta = models.CharField(max_length=800, blank=True, null=True)
    client_id = models.TextField(max_length=800, blank=True, null=True)
    client_secret = models.TextField(max_length=800, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    #funcion str
    def __str__(self):
        return self.cuenta
    
    class Meta:
        verbose_name = "Configuración Wompi"
        verbose_name_plural = "Configuraciones Wompi"

class General_Description(models.Model):
    """
    This model represents the general description of a product. It is used to store information that applies to
    """
    titulo_largo = models.CharField( max_length=50)
    titulo_corto = models.CharField(max_length=30)
    medio_titulo = models.CharField(max_length=30)
    descripcion_larga = models.TextField(max_length=500)
    descripcion_corta = models.CharField(max_length=75)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        get_latest_by = 'fecha_creacion'
        
    #funcion str
    def __str__(self):
        return self.titulo_largo

# Función de carga para el directorio "direccionamiento" con la fecha actual
def upload_to_direccionamiento(instance, filename):
    # Obtener la fecha actual
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    # Devolver la ruta completa del archivo
    return f'direccionamiento/{fecha_actual}/{filename}'
    
class Direccionamiento(models.Model):
    nombre = models.CharField( max_length=50)
    imagen = models.ImageField(upload_to=upload_to_direccionamiento, height_field=None, width_field=None, max_length=None)
    url_azure = models.URLField(max_length=500, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    #la funcion str
    def __str__(self):
        return self.nombre
    
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

class Barra_Principal (models.Model):
    email_contacto = models.CharField(max_length=100)
    numero_contacto = models.CharField(max_length=50)
    url_facebook = models.CharField(max_length=100)
    url_twitter = models.CharField(max_length=100)
    url_linkedin = models.CharField(max_length=100)
    url_instagram = models.CharField(max_length=100)
    url_youtube = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        get_latest_by = 'fecha_creacion'
        
    #la funcion str
    def __str__(self):
        return self.email_contacto + " - " + self.numero_contacto
    
    
    
def upload_to_carrusel_inicio(instance, filename):
    # La función toma la instancia del modelo y el nombre del archivo y construye la ruta de almacenamiento
    return f'configuraciones/carrusel_inicio/{filename}'

class CarruselInicio(models.Model):
    #carrouser imagen
    titulo = models.CharField(max_length=100)
    contenido = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to=upload_to_carrusel_inicio, height_field=None, width_field=None, max_length=None)
    imagen_url = models.URLField(max_length=500, blank=True)  # Campo para guardar la URL de la imagen principal
    url_boton = models.CharField(max_length=100)
    texto_boton = models.CharField(max_length=50)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    #la funcion str
    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Conexión al servicio Blob de Azure
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER_NAME)

        # Variables para almacenar las URLs de las imágenes
        imagen_url = None

        # Subir las imágenes si existen
        for field_name in ['imagen']:
            imagen_field = getattr(self, field_name)
            if imagen_field:
                # Generar la ruta completa de la imagen
                ruta_imagen = upload_to_carrusel_inicio(self, os.path.basename(imagen_field.name))
                # Obtener el blob client
                blob_client = container_client.get_blob_client(ruta_imagen)
                if not blob_client.exists():
                    with open(imagen_field.path, "rb") as data:
                        blob_client.upload_blob(data, content_settings=ContentSettings(content_disposition=None, content_type="image/jpeg"))
                # Obtener y guardar la URL de la imagen
                if field_name == 'imagen':
                    imagen_url = blob_client.url

        # Asignar las URLs al modelo
        self.imagen_url = imagen_url

        # Guardar el modelo una vez que se hayan asignado todas las URLs
        super().save(*args, **kwargs)


def upload_to_services_bar(instance, filename):
    # La función toma la instancia del modelo y el nombre del archivo y construye la ruta de almacenamiento
    return f'configuraciones/services_bar/{filename}'

class Services_Bar(models.Model):
    #barra de servicios
    services_visible = models.BooleanField()
    services_ico = models.ImageField( upload_to=upload_to_services_bar, height_field=None, width_field=None, max_length=None)
    imagen_url = models.URLField(max_length=500, blank=True)  # Campo para guardar la URL de la imagen principal
    services_ico_tag = models.CharField(max_length=150, null=True)
    services_name = models.CharField(max_length=50)
    services_description = models.CharField(max_length=250)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    #funcion str
    def __str__(self):
        return self.services_name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Conexión al servicio Blob de Azure
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER_NAME)

        # Variables para almacenar las URLs de las imágenes
        imagen_url = None

        # Subir las imágenes si existen
        for field_name in ['services_ico']:
            imagen_field = getattr(self, field_name)
            if imagen_field:
                # Generar la ruta completa de la imagen
                ruta_imagen = upload_to_services_bar(self, os.path.basename(imagen_field.name))
                # Obtener el blob client
                blob_client = container_client.get_blob_client(ruta_imagen)
                if not blob_client.exists():
                    with open(imagen_field.path, "rb") as data:
                        blob_client.upload_blob(data, content_settings=ContentSettings(content_disposition=None, content_type="image/jpeg"))
                # Obtener y guardar la URL de la imagen
                if field_name == 'services_ico':
                    imagen_url = blob_client.url

        # Asignar las URLs al modelo
        self.imagen_url = imagen_url

        # Guardar el modelo una vez que se hayan asignado todas las URLs
        super().save(*args, **kwargs)


def upload_to_team_bar(instance, filename):
    # La función toma la instancia del modelo y el nombre del archivo y construye la ruta de almacenamiento
    return f'configuraciones/team_bar/{filename}'
    
class Team_bar(models.Model):
    #barra de equipos
    team_image = models.ImageField(upload_to=upload_to_team_bar, blank=False, null=False)
    imagen_url = models.URLField(max_length=500, blank=True)  # Campo para guardar la URL de la imagen principal
    team_nombre = models.CharField(max_length=40)
    team_job =  models.CharField(max_length=130)
    # email_contacto = models.CharField(max_length=100)
    # numero_contacto = models.CharField(max_length=50)
    url_facebook = models.CharField(max_length=100)
    url_twitter = models.CharField(max_length=100)
    url_linkedin = models.CharField(max_length=100)
    url_instagram = models.CharField(max_length=100)
    # url_youtube = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    
    #funcion str
    def __str__(self):
        return self.team_nombre+"-"+self.team_job
    #Se agrega un metodo a la clase Team_bar para que se
    #pongan las imagenes en orden inverso
    @property
    def is_last(self):
        """Return True if the team member is last."""
        return not Team_bar.objects.filter(id__gt=self.id).exists
    
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Conexión al servicio Blob de Azure
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER_NAME)

        # Variables para almacenar las URLs de las imágenes
        imagen_url = None

        # Subir las imágenes si existen
        for field_name in ['team_image']:
            imagen_field = getattr(self, field_name)
            if imagen_field:
                # Generar la ruta completa de la imagen
                ruta_imagen = upload_to_team_bar(self, os.path.basename(imagen_field.name))
                # Obtener el blob client
                blob_client = container_client.get_blob_client(ruta_imagen)
                if not blob_client.exists():
                    with open(imagen_field.path, "rb") as data:
                        blob_client.upload_blob(data, content_settings=ContentSettings(content_disposition=None, content_type="image/jpeg"))
                # Obtener y guardar la URL de la imagen
                if field_name == 'team_image':
                    imagen_url = blob_client.url

        # Asignar las URLs al modelo
        self.imagen_url = imagen_url

        # Guardar el modelo una vez que se hayan asignado todas las URLs
        super().save(*args, **kwargs)

    
    
#contac information
class Contacts(models.Model):
    contact_email = models.EmailField("Correo electronico", max_length=254, help_text="Ingrese su dirección de correo electrónico")
    contact_phone = models.CharField(max_length=50)
    addres = models.CharField(max_length=250)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        get_latest_by = 'fecha_creacion'
    
    #funcion str
    def __str__(self):
        return self.contact_email
    
#urls de Secciones Principales 
class Urls_info(models.Model):
    title = models.CharField(max_length=50)
    url = models.CharField(max_length=200)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    #funcion str
    def __str__(self):
        return self.title

#urls de informacion de interes 
class Urls_interes(models.Model):
    title = models.CharField(max_length=50)
    url = models.URLField(max_length=200)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    #funcion str
    def __str__(self):
        return self.title
    
    
    

    


