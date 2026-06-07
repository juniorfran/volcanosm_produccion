"""Rutas del módulo de Alquileres (nombres planos)."""
from django.urls import path

from . import views

urlpatterns = [
    # Artículos (gestión)
    path("articulos/", views.articulo_list, name="articulo_list"),
    path("articulos/nuevo/", views.articulo_create, name="articulo_create"),
    path("articulos/<int:pk>/editar/", views.articulo_update, name="articulo_update"),
    path("articulos/<int:pk>/eliminar/", views.articulo_delete, name="articulo_delete"),

    # Alquileres (operación)
    path("nuevo/", views.alquiler_nuevo, name="alquiler_nuevo"),
    path("", views.alquiler_list, name="alquiler_list"),
    path("<int:pk>/", views.alquiler_detalle, name="alquiler_detalle"),
    path("<int:pk>/devolver/", views.alquiler_devolver, name="alquiler_devolver"),
]
