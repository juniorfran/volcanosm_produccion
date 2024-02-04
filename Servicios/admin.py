from django.contrib import admin
from .models import TipoServicio, Servicios, ImagenesServicio

@admin.register(TipoServicio)
class TipoServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_creacion')
    search_fields = ['nombre']  # Define los campos que se pueden buscar

@admin.register(Servicios)
class ServiciosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'descripcion', 'imagen', 'url_azure')
    search_fields = ['nombre', 'descripcion']  # Define los campos que se pueden buscar

@admin.register(ImagenesServicio)
class ImagenesServicioAdmin(admin.ModelAdmin):
    list_display = ('servicio', 'imagen1', 'imagen2', 'imagen3', 'imagen4', 'url_azure_1', 'url_azure_2', 'url_azure_3', 'url_azure_4')
    search_fields = ['servicio__nombre']  # Define los campos que se pueden buscar
