"""
URL configuration for alpiedelvolcan_ project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from . import views
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

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
    
    # Otras URLs de la aplicación
    path('utilidades/', include('Utilidades.urls')),
    
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# Configuración para servir archivos estáticos en entorno de desarrollo
urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)