# admin.py en tu aplicación de Django
from django.contrib import admin
from .models import EnlacePago  # Asegúrate de ajustar la importación según la ubicación de tu modelo

@admin.register(EnlacePago)
class EnlacePagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'comercio_id', 'reserva', 'monto', 'nombre_producto', 'url_enlace', 'esta_productivo')
    search_fields = ['comercio_id', 'nombre_producto', 'reserva']
    list_filter = ['esta_productivo']
    readonly_fields = ('id', 'comercio_id', 'monto', 'nombre_producto', 'url_qr_code', 'url_enlace', 'esta_productivo')
    exclude = []

    def has_add_permission(self, request):
        return False
