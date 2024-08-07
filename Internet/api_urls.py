from django.urls import path
from .api_views import (
    TiposListCreate, TiposRetrieveUpdateDestroy, AccesosListCreate, AccesosRetrieveUpdateDestroy, 
    ClientesListCreate, ClientesRetrieveUpdateDestroy, EnlacePagoAccesoListCreate, 
    EnlacePagoAccesoRetrieveUpdateDestroy, TransaccionCompraListCreate, 
    TransaccionCompraRetrieveUpdateDestroy, Transaccion3DSListCreate, 
    Transaccion3DSRetrieveUpdateDestroy, Transaccion3DS_RespuestaListCreate, 
    Transaccion3DS_RespuestaRetrieveUpdateDestroy, TransaccionCompra3DSListCreate, 
    TransaccionCompra3DSRetrieveUpdateDestroy, MikrotikConfigListCreate, MikrotikConfigRetrieveUpdateDestroy,
    Transaccion3DSCompraAccesoView, transaccion3ds_exitosa, transaccion3ds_fallida, verificar_pago
)

urlpatterns = [
    path('tipos/', TiposListCreate.as_view(), name='tipos-list-create'),
    path('tipos/<int:pk>/', TiposRetrieveUpdateDestroy.as_view(), name='tipos-detail'),
    path('accesos/', AccesosListCreate.as_view(), name='accesos-list-create'),
    path('accesos/<int:pk>/', AccesosRetrieveUpdateDestroy.as_view(), name='accesos-detail'),
    path('clientes/', ClientesListCreate.as_view(), name='clientes-list-create'),
    path('clientes/<int:pk>/', ClientesRetrieveUpdateDestroy.as_view(), name='clientes-detail'),
    path('enlace_pago_acceso/', EnlacePagoAccesoListCreate.as_view(), name='enlace_pago_acceso-list-create'),
    path('enlace_pago_acceso/<int:pk>/', EnlacePagoAccesoRetrieveUpdateDestroy.as_view(), name='enlace_pago_acceso-detail'),
    path('transaccion_compra/', TransaccionCompraListCreate.as_view(), name='transaccion_compra-list-create'),
    path('transaccion_compra/<int:pk>/', TransaccionCompraRetrieveUpdateDestroy.as_view(), name='transaccion_compra-detail'),
    path('transaccion_3ds/', Transaccion3DSListCreate.as_view(), name='transaccion_3ds-list-create'),
    path('transaccion_3ds/<int:pk>/', Transaccion3DSRetrieveUpdateDestroy.as_view(), name='transaccion_3ds-detail'),
    path('transaccion_3ds_respuesta/', Transaccion3DS_RespuestaListCreate.as_view(), name='transaccion_3ds_respuesta-list-create'),
    path('transaccion_3ds_respuesta/<int:pk>/', Transaccion3DS_RespuestaRetrieveUpdateDestroy.as_view(), name='transaccion_3ds_respuesta-detail'),
    path('transaccion_compra_3ds/', TransaccionCompra3DSListCreate.as_view(), name='transaccion_compra_3ds-list-create'),
    path('transaccion_compra_3ds/<int:pk>/', TransaccionCompra3DSRetrieveUpdateDestroy.as_view(), name='transaccion_compra_3ds-detail'),
    path('mikrotik_config/', MikrotikConfigListCreate.as_view(), name='mikrotik_config-list-create'),
    path('mikrotik_config/<int:pk>/', MikrotikConfigRetrieveUpdateDestroy.as_view(), name='mikrotik_config-detail'),
    
    path('api/transaccion3ds/compra/<int:tipo_acceso_id>/', Transaccion3DSCompraAccesoView.as_view(), name='transaccion3ds_compra_acceso'),
    path('transaccion3ds/exitosa/<int:transaccion3ds_id>/', transaccion3ds_exitosa, name='transaccion3ds-exitosa'),
    path('transaccion3ds/fallida/', transaccion3ds_fallida, name='transaccion3ds-fallida'),
    path('transaccion3ds/verificar/<int:transaccion_id>/', verificar_pago, name='verificar-pago'),
]
