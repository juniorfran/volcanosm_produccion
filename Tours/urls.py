from django.urls import path
from . import views

urlpatterns = [
    path('', views.tours_index, name='tours'),
    path('tour/<int:tour_id>/', views.tour_detail, name='tour_detail'),
    path('reservar/<int:tour_id>/', views.reservar_tour, name='reservar_tour'),
    path('reservar_exitosa/<int:reserva_id>/', views.reserva_exitosa, name='reserva_exitosa'),
    #path('reservar_exitosa1/<int:reserva_id>/', views.reserva_exitosa1, name='reserva_exitosa1'),
    #path('consulta-enlace-pago/', views.consulta_enlace_pago, name='consulta_enlace_pago'),
    
    #path('actualizar_estado/', views.actualizar_estado_reserva, name='actualizar_estado_reserva'),
    path('actualizar_estado/<int:reserva_id>/', views.actualizar_estado_reserva, name='actualizar_estado_reserva'),

    
    # path('abrir_enlace_pago/', views.abrir_enlace_pago, name='abrir_enlace_pago'),
    # path('espera_confirmacion_pago/', views.espera_confirmacion_pago, name='espera_confirmacion_pago'),


    # Agrega más URL según sea necesario
]