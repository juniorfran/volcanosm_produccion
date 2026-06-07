from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'telefono', 'email', 'estado')
    list_filter = ('estado', 'tipo_documento')
    search_fields = ('nombre', 'apellido', 'numero_documento', 'email')
