from django.db import models
from django.utils import timezone

class Cliente(models.Model):
    TIPO_DOCUMENTO_CHOICES = (
        ('DNI', 'Documento Nacional de Identidad'),
        ('CI', 'Cédula de Identidad'),
        ('PASAPORTE', 'Pasaporte'),
        ('OTRO', 'Otro')
    )

    ESTADO_CHOICES = (
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo')
    )

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES)
    numero_documento = models.CharField(max_length=50)
    pais = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')
    direccion = models.TextField()
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
