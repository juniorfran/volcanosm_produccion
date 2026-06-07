from django.urls import path

from . import views

urlpatterns = [
    path("", views.producto_list, name="producto_list"),
    path("create/", views.producto_create, name="producto_create"),
    path("<int:pk>/update/", views.producto_update, name="producto_update"),
    path("<int:pk>/delete/", views.producto_delete, name="producto_delete"),
    path("categorias/create/", views.categoria_create, name="categoria_create"),
]
