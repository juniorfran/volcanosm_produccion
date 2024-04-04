from django.contrib import admin
from .models import MovimientoCaja

class MovimientoCajaAdmin(admin.ModelAdmin):
    list_display = ('caja', 'usuario', 'tipo_movimiento', 'efectivo_anterior', 'cantidad_efectivo', 'efectivo_actual', 'motivo', 'fecha_creacion')
    search_fields = ('tipo_movimiento', 'motivo', 'usuario__username')
    list_filter = ('tipo_movimiento', 'fecha_creacion')

admin.site.register(MovimientoCaja, MovimientoCajaAdmin)