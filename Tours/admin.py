from django.contrib import admin
from .models import TipoTour, Tour, ImagenTour, Resena, Reserva

@admin.register(TipoTour)
class TipoTourAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'descripcion', 'precio_adulto', 'precio_nino', 'duracion', 'iva', 'tipo_tour',)
    search_fields = ('titulo', 'descripcion', 'tipo_tour__nombre',)

@admin.register(ImagenTour)
class ImagenTourAdmin(admin.ModelAdmin):
    list_display = ('tour','imagen')

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('tour', 'estrellas', 'comentario',)
    search_fields = ('tour__titulo', 'comentario',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('tour', 'codigo_reserva', 'nombre', 'dui', 'correo_electronico', 'direccion', 'cantidad_adultos', 'cantidad_ninos', 'fecha_reserva', 'total_pagar',)
    search_fields = ('tour__titulo', 'codigo_reserva', 'nombre', 'dui', 'correo_electronico',)
    list_filter = ('fecha_reserva',)
