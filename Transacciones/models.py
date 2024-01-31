# models.py en tu aplicación de Django
from django.db import models
from Tours.models import Reserva

def upload_to_transactions(instance, filename):
    # La función toma la instancia del modelo y el nombre del archivo y construye la ruta de almacenamiento
    return f'Transacciones/ImagenProducto/{filename}'
    

class EnlacePago(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    comercio_id = models.CharField(max_length=500)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    nombre_producto = models.CharField(max_length=500)
    url_qr_code = models.URLField()
    url_enlace = models.URLField()
    esta_productivo = models.BooleanField()
    descripcionProducto = models.TextField()
    cantidad = models.CharField(max_length=5)
    imagenProducto = models.URLField(max_length=250, null=True)
    idEnlace = models.CharField(max_length=150)

    def __str__(self):
        return f"EnlacePago {self.id}: {self.nombre_producto}"