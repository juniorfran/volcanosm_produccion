from django.contrib import admin
from .models import Barra_Principal, CarruselInicio, Services_Bar, Team_bar, Contacts, Urls_info, Urls_interes
from .models import General_Description

@admin.register(Barra_Principal)
class BarraPrincipalAdmin(admin.ModelAdmin):
    list_display = ('email_contacto', 'fecha_creacion', 'numero_contacto', 'url_facebook', 'url_twitter', 'url_linkedin', 'url_instagram', 'url_youtube')

@admin.register(CarruselInicio)
class CarruselInicioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'contenido', 'url_boton', 'texto_boton')

@admin.register(Services_Bar)
class ServicesBarAdmin(admin.ModelAdmin):
    list_display = ('services_name', 'services_visible', 'services_ico', 'services_ico_tag', 'services_description')

@admin.register(Team_bar)
class TeamBarAdmin(admin.ModelAdmin):
    list_display = ('team_nombre', 'team_job', 'team_image',  'url_facebook', 'url_twitter', 'url_linkedin', 'url_instagram', 'is_last')

@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    list_display = ('contact_email', 'contact_phone', 'addres', 'fecha_creacion')

@admin.register(Urls_info)
class UrlsInfoAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'fecha_creacion')
    
@admin.register(Urls_interes)
class UrlsInfoAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'fecha_creacion')
    


@admin.register(General_Description)
class GeneralDescriptionAdmin(admin.ModelAdmin):
    list_display = ('titulo_largo', 'titulo_corto', 'medio_titulo', 'fecha_creacion')
    search_fields = ('titulo_largo', 'titulo_corto', 'medio_titulo')
    ordering = ('-fecha_creacion',)
