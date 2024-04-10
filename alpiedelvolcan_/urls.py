
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from . import views
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from Tours.utils import actualizar_estado_reserva, start_background_thread

urlpatterns = [
    #url para la pagina principal
    path("", views.index,name="index"),
    
    #url para admin
    path('admin/', admin.site.urls),
    
    #url para tours
    path('tours/', include('Tours.urls')),
    
    #url para nosotros
    path('nosotros/', include('Nosotros.urls')),
    
    #url para pagos wompi
    path('pagos/', include('Transacciones.urls')),

    #url para pagos Servicios
    path('servicios/', include('Servicios.urls')),
    
    #url para contactanos
    path('contactanos/', include('Contactanos.urls')),
      #url para TPV
    path('TPV/Cajas/', include('TPV_.Cajas.urls')),
    path('TPV/Productos/', include('TPV_.Productos.urls')),
    path('TPV/Ventas/', include('TPV_.Ventas.urls')),
    
    # Otras URLs de la aplicación
    path('utilidades/', include('Utilidades.urls')),
    
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

start_background_thread()

# Configuración para servir archivos estáticos en entorno de desarrollo
urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)