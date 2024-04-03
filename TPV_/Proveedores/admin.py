from django.contrib import admin

# Register your models here.

#proveedores
from .models import Proveedor

#proveedores admin
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion','telefono')
    
admin.site.register(Proveedor)

#productos