from django.db import models
from ckeditor.fields import RichTextField
from django.core.mail import send_mail
from django.conf import settings
from django.db import models

# Create your models here.
class Mensaje_Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    asunto = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    mensaje = RichTextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Llama al método save del modelo padre
        super().save(*args, **kwargs)

        # Prepara el contenido del correo electrónico
        subject = 'Nuevo mensaje de contacto: {}'.format(self.asunto)
        message = 'Nombre: {}\nEmail: {}\nMensaje:\n{}'.format(self.nombre, self.email, self.mensaje)
        from_email = settings.EMAIL_HOST_USER
        to_email = [
            #'juniorfran@hotmail.es'
            'volcanosanmiguel.sv@hotmail.com'
            ]

        # Envía el correo electrónico
        send_mail(subject, message, from_email, to_email)