from django.contrib import admin

from .models import MovimientoInventario


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ("fecha_creacion", "producto", "tipo", "cantidad", "stock_anterior", "stock_nuevo", "usuario")
    list_filter = ("tipo", "fecha_creacion")
    search_fields = ("producto__nombre", "referencia")
