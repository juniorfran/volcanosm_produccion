# En tu archivo urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Otra rutas aquí
    path('contact/', views.contacto, name='contacto'),
]
