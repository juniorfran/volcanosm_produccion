from django.conf import settings
from django.db import models
from ckeditor.fields import RichTextField
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.storage.blob import ContentSettings
import os
from datetime import datetime, timedelta
from django.utils import timezone


class Tipos (models.Model):
    nombre = models.CharField( max_length=50, null=True)
    tiempo_conexion = models.CharField( max_length=50, null=True)
    velocidad_mb = models.CharField( max_length=50, null=True)
    descripcion = models.CharField( max_length=250, null=True)
    precio = models.DecimalField(max_digits=5, decimal_places=4, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, null=True)
    imagen_tipo = models.ImageField(upload_to='tipos_accesos', null=True)
    url_azure = models.URLField(max_length=400, blank=True, null=True)
    
    # Nuevo campo para el rango de fechas disponibles
    fecha_inicio = models.DateTimeField(default=timezone.now, null=True)
    fecha_fin = models.DateTimeField(default=timezone.now, null=True)
    
    def save (self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Conexión al servicio Blob de Azure
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER_NAME)
        
        if self.imagen_tipo:
            fecha_actual = timezone.now()
            ruta_carpeta = f"tipos_accesos/{fecha_actual.year}/{fecha_actual.month}/{fecha_actual.day}/"
            blob_name = f"{self.id}_imagen_{os.path.basename(self.imagen_tipo.name)}"
            ruta_imagen = os.path.join(ruta_carpeta, blob_name)
            
            blob_client = container_client.get_blob_client(ruta_imagen)
            if not blob_client.exists():
                with open(self.imagen_tipo.path, "rb") as data:
                    blob_client.upload_blob(data, content_settings=ContentSettings(content_disposition=None, content_type="image/jpeg"))
                self.url_azure = blob_client.url
        
        super().save(*args, **kwargs)
        
    def obtener_imagen_principal(self):
        return self.url_azure
    
    def __str__(self):
        return f"{self.nombre} - {self.tiempo_conexion}"


class Accesos (models.Model):
    usuario = models.CharField( max_length=50)
    password = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=250)
    cant_usuarios = models.IntegerField(null=True)
    acceso_tipo = models.ForeignKey(Tipos, on_delete=models.CASCADE)    #CASCADE -> si se elimina el tipo, se eliminan los accesos del tipo
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, null=True)
    fecha_expiracion = models.DateTimeField(null=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario} - {self.password}"
    
    
class Clientes (models.Model):
    nombre = models.CharField( max_length=50)
    apellido = models.CharField( max_length=50)
    direccion = models.TextField()
    dui = models.CharField(max_length=50)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.apellido}"
    

def upload_to_transactions(instance, filename):
    # La función toma la instancia del modelo y el nombre del archivo y construye la ruta de almacenamiento
    return f'Transacciones/ImagenProducto/{filename}'


class EnlacePagoAcceso(models.Model):
    acceso = models.ForeignKey(Accesos, on_delete=models.CASCADE, related_name='enlace_pago_set')
    comercio_id = models.CharField(max_length=500)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    nombre_producto = models.CharField(max_length=500)
    url_qr_code = models.URLField()
    url_enlace = models.URLField()
    esta_productivo = models.BooleanField()
    descripcionProducto = RichTextField()
    cantidad = models.CharField(max_length=5)
    imagenProducto = models.URLField(max_length=250, null=True)
    idEnlace = models.CharField(max_length=150)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"EnlacePago {self.id}: {self.nombre_producto}"
    

class TransaccionCompra(models.Model):
    enlace_pago = models.ForeignKey(EnlacePagoAcceso, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, related_name='transaccion_set')
    acceso = models.ForeignKey(Accesos, on_delete=models.CASCADE, related_name='transaccion_set')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, null=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.cliente} - {self.acceso}"
    
class Transaccion3DS(models.Model):
    acceso = models.ForeignKey(Accesos, on_delete=models.CASCADE, related_name='transaccion3ds_acceso')
    numeroTarjeta = models.CharField(max_length=150)
    mesVencimiento = models.CharField(max_length=50)
    anioVencimiento = models.CharField(max_length=50)
    cvv = models.CharField(max_length=50)
    monto = models.CharField(max_length=50)
    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    ciudad = models.CharField(max_length=50)
    direccion = models.TextField()
    telefono = models.CharField( max_length=50)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, null=True)
    estado = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.apellido}"
    
class Transaccion3DS_Respuesta(models.Model):
    transaccion3ds = models.ForeignKey(Transaccion3DS, on_delete=models.CASCADE, related_name='transaccion3ds_respuesta_set')
    idTransaccion = models.CharField(max_length=150)
    esReal = models.BooleanField(default=True)
    urlCompletarPago3Ds = models.URLField(max_length=500)
    monto = models.CharField(max_length=50)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return f"{self.transaccion3ds} - {self.idTransaccion}"
    
class TransaccionCompra3DS(models.Model):
    transaccion3ds = models.ForeignKey(Transaccion3DS, on_delete=models.CASCADE, related_name='transaccion3ds_set')
    transaccion3ds_respuesta = models.ForeignKey(Transaccion3DS_Respuesta, on_delete=models.CASCADE, related_name='transaccion3ds_respuesta_set')
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, related_name='cliente_transaccion3ds_set')
    acceso = models.ForeignKey(Accesos, on_delete=models.CASCADE, related_name='acceso_transaccion3ds_set')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, null=True)
    estado = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.cliente} - {self.acceso}"