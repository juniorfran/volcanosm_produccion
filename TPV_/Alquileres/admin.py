from django.contrib import admin

from .models import ArticuloAlquiler, Alquiler, AlquilerDetalle


@admin.register(ArticuloAlquiler)
class ArticuloAlquilerAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "cantidad_total", "cantidad_disponible", "tarifa", "activo")
    list_filter = ("categoria", "activo")
    search_fields = ("nombre",)


class AlquilerDetalleInline(admin.TabularInline):
    model = AlquilerDetalle
    extra = 0


@admin.register(Alquiler)
class AlquilerAdmin(admin.ModelAdmin):
    list_display = ("numero", "cliente", "estado", "total_tarifa", "deposito", "fecha_salida")
    list_filter = ("estado",)
    inlines = [AlquilerDetalleInline]
