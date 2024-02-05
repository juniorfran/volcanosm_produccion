from django.contrib import admin
from .models import Mensaje_Contacto

class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'asunto', 'email')  # Campos a mostrar en la lista de mensajes
    search_fields = ('nombre', 'asunto', 'email', 'mensaje')  # Campos por los cuales se puede buscar

# Register your models here.
admin.site.register(Mensaje_Contacto, MensajeContactoAdmin)
