from django.urls import path
from . import views

urlpatterns = [
    path('', views.nosotros_index, name='nosotros'),
    path('terminos&condiciones/', views.mostrar_ultimos_terminos, name='terminos_condiciones'),
    path('politicas&vision&mision/', views.politicas_mision_vision, name='politicas_vision_mision'),
    
]