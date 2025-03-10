from django.urls import path
from . import views


urlpatterns = [
    #path('procesar-pago/', views.procesar_pago, name='procesar_pago'),
    path('', views.servicio_inter_index, name='servicio_inter'),
    #path('internet/<int:tipo_acceso_id>/', views.acceso_detail, name='detalle_internet'),
    path('comprar_internet/<int:tipo_acceso_id>/', views.comprar_acceso, name='comprar_acceso'),
    path('verificar_transaccion_exitosa/', views.verificar_transaccion_exitosa, name='verificar_transaccion_exitosa'),
    path('transaccion/<int:transaccion_id>/', views.transaccion_exitosa, name='transaccion_exitosa'),
    path('transaccion_fallo/', views.transaccion3ds_fallida, name='transaccion3ds_fallida'),
    path('compra3rds_internet/<int:tipo_acceso_id>/', views.transaccion3ds_compra_acceso, name='comprar_acceso_3ds'),
    path('transaccion-exitosa/<int:transaccion3ds_id>/', views.transaccion3ds_exitosa, name='transaccion3ds_exitosa'),
    
    path('verificar-pago/<str:transaccion_id>/', views.verificar_pago, name='verificar_pago'),
    

]