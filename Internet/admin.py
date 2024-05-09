from django.contrib import admin
from .models import Tipos, Accesos, EnlacePagoAcceso, Clientes, TransaccionCompra

import csv
import openpyxl
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from django.contrib.admin.models import LogEntry
from django.utils import timezone
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html


# Register your models here.

@admin.register(Tipos)
class TiposAccesos(admin.ModelAdmin):
    list_display = ('nombre', 'velocidad_mb', 'precio', 'tiempo_conexion', 'mostrar_imagen_azure')
    search_fields = ('nombre', 'velocidad_mb', 'precio', 'tiempo_conexion',)
    list_filter = ('nombre', 'velocidad_mb', 'precio', 'tiempo_conexion',)
    ordering = ('nombre', 'velocidad_mb', 'precio', 'tiempo_conexion',)
    list_per_page = 10
    list_max_show_all = 100
    #list_select_related = ('nombre', 'velocidad_mb', 'precio', 'tiempo_conexion',)
    list_filter = ('nombre', 'velocidad_mb', 'precio', 'tiempo_conexion',)
    
    def mostrar_imagen_azure(self, obj):
        if obj.url_azure:
            return format_html('<img src="{}" width="100" />', obj.url_azure)
        else:
            return 'No disponible'
        
    mostrar_imagen_azure.short_description = 'Imagen Azure'

@admin.register(Accesos)
class Accesos(admin.ModelAdmin):
    list_display = ('acceso_tipo', 'usuario', 'fecha_creacion')
    search_fields = ( 'acceso_tipo', 'usuario', 'fecha_creacion')
    list_filter = ('acceso_tipo', 'usuario', 'fecha_creacion')
    ordering = ('acceso_tipo', 'usuario', 'fecha_creacion')
    list_per_page = 10
    list_max_show_all = 100

@admin.register(EnlacePagoAcceso)
class EnlacePago(admin.ModelAdmin):
    list_display = ('acceso', 'comercio_id', 'nombre_producto')
    search_fields = ('acceso', 'comercio_id', 'nombre_producto')
    list_filter = ('acceso', 'comercio_id', 'nombre_producto')
    ordering = ('acceso', 'comercio_id', 'nombre_producto')
    list_per_page = 10
    list_max_show_all = 100

@admin.register(Clientes)
class Clientes(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'telefono', 'fecha_creacion')
    search_fields = ('nombre', 'apellido', 'email', 'telefono')
    list_filter = ('nombre', 'apellido', 'email', 'telefono')
    ordering = ('nombre', 'apellido', 'email', 'telefono')
    list_per_page = 10
    list_max_show_all = 100
    
@admin.register(TransaccionCompra)
class TransaccionCompra(admin.ModelAdmin):
    list_display = ('cliente', 'acceso', 'fecha_creacion')
    search_fields = ('cliente', 'acceso', 'fecha_creacion')
    list_filter = ('cliente', 'acceso', 'fecha_creacion')
    ordering = ('cliente', 'acceso', 'fecha_creacion')
    list_per_page = 10
    list_max_show_all = 100