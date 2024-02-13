import logging
from django.db import models
from ckeditor.fields import RichTextField
from django.core.mail import send_mail
from django.conf import settings
from azure.communication.email import EmailClient
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

class Mensaje_Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    asunto = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        
        try:
            # Configuración de la conexión al servicio de correo electrónico de Azure
            connection_string = "endpoint=https://emailvolcanosm.unitedstates.communication.azure.com/;accesskey=SkW7u9s6sgjkska6ncJ8iOQutZdU1f+iIH9rfMto3j+NFLi8bpmcM4PF+4oJ3A+gQkAOXVFvhxaNqa8UTdtcUg=="
            client = EmailClient.from_connection_string(connection_string)

            # Construye el cuerpo del mensaje de contacto
            mensaje_contacto = f"""
            Nombre: {self.nombre}
            Email: {self.email}
            Asunto: {self.asunto}
            Mensaje:
            {self.mensaje}
            """

            # Configuración del mensaje
            message = {
                "senderAddress": settings.EMAIL_HOST_USER,  # Reemplaza con el remitente real
                "recipients": {
                    "to": [
                        {"address": settings.DEFAULT_FROM_EMAIL}  # Aquí podrías usar otra dirección de correo si lo deseas
                    ],
                },
                "content": {
                    "subject": self.asunto,
                    "plainText": mensaje_contacto,
                }
            }

            # Envía el correo electrónico utilizando el servicio de correo electrónico de Azure
            poller = client.begin_send(message)
            result = poller.result()

        except Exception as ex:
            # Registra el error en el archivo de registro
            logger.error(f"Error al enviar correo electrónico: {ex}")
        
        super().save(*args, **kwargs)