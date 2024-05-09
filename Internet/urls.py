from django.urls import path
from . import views

urlpatterns = [
    #path('procesar-pago/', views.procesar_pago, name='procesar_pago'),
    path('', views.servicio_inter_index, name='servicio_inter'),
    #path('internet/<int:tipo_acceso_id>/', views.acceso_detail, name='detalle_internet'),
    path('comprar_internet/<int:tipo_acceso_id>/', views.comprar_acceso, name='comprar_acceso'),
    path('verificar_transaccion_exitosa/', views.verificar_transaccion_exitosa, name='verificar_transaccion_exitosa'),
    path('transaccion/<int:transaccion_id>/', views.transaccion_exitosa, name='transaccion_exitosa')
]