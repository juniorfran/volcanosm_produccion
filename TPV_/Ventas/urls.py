from django.urls import path

from . import views

urlpatterns = [
    path('punto_de_ventas/', views.punto_de_venta, name='punto_de_venta'),
    path('process_sale/', views.process_sale, name='process_sale'),
    path('ventas/caja/', views.ventas_por_caja, name='ventas_por_caja'),
    path('ventas/detalle/<int:venta_id>/', views.venta_detalle, name='venta_detalle'),
    path('ventas/anular/<int:venta_id>/', views.anular_venta, name='anular_venta'),
]
