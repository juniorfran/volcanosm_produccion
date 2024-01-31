from django.contrib import admin
from .models import Nosotros, Nosotros_Servicios, Nosotros_Oferta, Solicitud_Oferta

@admin.register(Nosotros)
class NosotrosAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'subtitulo', 'fecha_creacion')
    search_fields = ('titulo', 'subtitulo')

@admin.register(Nosotros_Servicios)
class NosotrosServiciosAdmin(admin.ModelAdmin):
    list_display = ('servicio_titulo', 'fecha_creacion')
    search_fields = ('servicio_titulo',)

@admin.register(Nosotros_Oferta)
class NosotrosOfertaAdmin(admin.ModelAdmin):
    list_display = ('titulo_oferta', 'porcentaje_descuento', 'servicio_descuento', 'fecha_creacion')
    search_fields = ('titulo_oferta', 'porcentaje_descuento', 'servicio_descuento')

@admin.register(Solicitud_Oferta)
class SolicitudOfertaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'fecha_creacion', 'oferta_relacionada')
    search_fields = ('nombre', 'email', 'telefono')
    list_filter = ('oferta_relacionada',)
