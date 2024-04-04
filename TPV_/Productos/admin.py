from django.contrib import admin
from .models import Categoria, Producto
# Register your models here.


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('pk', 'nombre')

admin.site.register(Categoria)

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('pk', 'nombre', 'codigo_de_barras', 'precio_de_venta')
admin.site.register(Producto)