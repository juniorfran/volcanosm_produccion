from django.contrib import admin
from django.utils.html import format_html
from .models import TipoTour, Tour, ImagenTour, Resena, Reserva

@admin.register(TipoTour)
class TipoTourAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

# @admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'descripcion', 'precio_adulto', 'precio_nino', 'duracion', 'iva', 'tipo_tour', 'fecha_inicio', 'fecha_fin')
    search_fields = ('titulo', 'descripcion', 'tipo_tour__nombre',)
    def mostrar_imagen_azure(self, obj):
        if obj.url_azure:
            return format_html('<img src="{}" width="100" />', obj.url_azure)
        else:
            return 'No disponible'

    mostrar_imagen_azure.short_description = 'Imagen Azure'

admin.site.register(Tour, TourAdmin)

@admin.register(ImagenTour)
class ImagenTourAdmin(admin.ModelAdmin):
    list_display = ('tour','imagen1')

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('tour', 'estrellas', 'comentario',)
    search_fields = ('tour__titulo', 'comentario',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('tour', 'codigo_reserva', 'nombre', 'dui', 'correo_electronico', 'direccion', 'cantidad_adultos', 'cantidad_ninos', 'fecha_reserva', 'total_pagar',)
    search_fields = ('tour__titulo', 'codigo_reserva', 'nombre', 'dui', 'correo_electronico',)
    list_filter = ('fecha_reserva',)
