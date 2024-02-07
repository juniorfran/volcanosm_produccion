from django.contrib import admin
from .models import Barra_Principal, CarruselInicio, Services_Bar, Team_bar, Contacts, Urls_info, Urls_interes, Direccionamiento
from .models import General_Description

@admin.register(Barra_Principal)
class BarraPrincipalAdmin(admin.ModelAdmin):
    icon_name = 'dehaze'
    list_display = ('email_contacto', 'fecha_creacion', 'numero_contacto', 'url_facebook', 'url_twitter', 'url_linkedin', 'url_instagram', 'url_youtube')

@admin.register(CarruselInicio)
class CarruselInicioAdmin(admin.ModelAdmin):
    icon_name = 'collections'
    list_display = ('titulo', 'contenido', 'url_boton', 'texto_boton')

@admin.register(Services_Bar)
class ServicesBarAdmin(admin.ModelAdmin):
    icon_name = 'free_breakfast'
    list_display = ('services_name', 'services_visible', 'services_ico', 'services_ico_tag', 'services_description')

@admin.register(Team_bar)
class TeamBarAdmin(admin.ModelAdmin):
    icon_name = 'group_add'
    list_display = ('team_nombre', 'team_job', 'team_image',  'url_facebook', 'url_twitter', 'url_linkedin', 'url_instagram', 'is_last')

@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    icon_name = 'folder_shared'
    list_display = ('contact_email', 'contact_phone', 'addres', 'fecha_creacion')

@admin.register(Urls_info)
class UrlsInfoAdmin(admin.ModelAdmin):
    icon_name = 'info_outline'
    list_display = ('title', 'url', 'fecha_creacion')
    
@admin.register(Urls_interes)
class UrlsInfoAdmin(admin.ModelAdmin):
    icon_name = 'insert_link'
    list_display = ('title', 'url', 'fecha_creacion')
    
@admin.register(Direccionamiento)
class UrlsInfoAdmin(admin.ModelAdmin):
    icon_name = 'insert_link'
    list_display = ('nombre', 'imagen', 'url_azure')

@admin.register(General_Description)
class GeneralDescriptionAdmin(admin.ModelAdmin):
    icon_name = 'panorama_horizontal'
    list_display = ('titulo_largo', 'titulo_corto', 'medio_titulo', 'fecha_creacion')
    search_fields = ('titulo_largo', 'titulo_corto', 'medio_titulo')
    ordering = ('-fecha_creacion',)
