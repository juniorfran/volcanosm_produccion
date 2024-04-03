from django.contrib import admin
from .models import Ventas, TipoVenta, DetalleVenta, Cart

#registrar tipo de venta al admin
class TiposDeVentasAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_creacion')  # Ejemplo de campos a mostrar en la lista
admin.site.register(TipoVenta, TiposDeVentasAdmin)

class VentasAdmin(admin.ModelAdmin):
    list_display = ('caja', 'tipo_venta', 'subtotal')
admin.site.register(Ventas, VentasAdmin)

#detalle ventas
@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'ticket_factura', 'cantidad', 'precio_unitario', 'iva', 'subtotal', 'fecha_creacion')
    list_filter = ('fecha_creacion',)
    search_fields = ('venta__id', 'ticket_factura', 'producto__nombre')
    
    
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at', 'total_quantity', 'total_price')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'created_at')
