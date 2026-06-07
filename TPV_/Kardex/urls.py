from django.urls import path

from . import views

urlpatterns = [
    path("", views.kardex_list, name="kardex_list"),
    path("entrada/", views.entrada_inventario, name="entrada_inventario"),
]
