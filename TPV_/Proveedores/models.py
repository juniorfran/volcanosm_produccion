from django.db import models

# Create your models here.
#MODELO PARA PROVEEDORES
class Proveedor(models.Model):  #Clase que hereda de la clase Model, por lo tanto es un modelo de Django
    nombre = models.CharField(max_length=200)   #Campo para el nombre del proveedor (Caracteres con máximo 200 caracteres)
    dui  = models.CharField("DUI", max_length=10)   #Campo DUI con longitud máxima de 10 caracteres
    nit   = models.IntegerField("NIT")              #Campo NIT de tipo Integer (Entero)
    nombre_comercial  = models.CharField("Nombre Comercial",max_length=50) # Campo Nombre Comercial con una longitud
    direccion = models.TextField()                         #Campo para la dirección del proveedor
    telefono = models.IntegerField()                        #Campo para el teléfono del proveedor
    email = models.EmailField(blank=True)               #Campo opcional para el correo electrónico del proveedor
    def __str__(self):              #Método que devuelve una cadena con el nombre completo del proveedor
        return self.nombre + " ("+ str(self.telefono)+")"
    