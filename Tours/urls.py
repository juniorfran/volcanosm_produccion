from django.urls import path
from . import views

urlpatterns = [
    path('', views.tours_index, name='tours'),
    path('tour/<int:tour_id>/', views.tour_detail, name='tour_detail'),
    path('reservar/<int:tour_id>/', views.reservar_tour, name='reservar_tour'),
    path('reservar_exitosa/<int:reserva_id>/', views.reserva_exitosa, name='reserva_exitosa'),


    # Agrega más URL según sea necesario
]