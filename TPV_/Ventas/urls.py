from django.urls import path
from . import views

urlpatterns = [
    path('punto_de_ventas/', views.punto_ventas, name='punto_de_venta'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('shopping_cart/', views.shopping_cart, name='shopping_cart'),
    path('update_cart_item/<int:cart_item_id>/<int:new_quantity>/', views.update_cart_item, name='update_cart_item'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('process_sale/', views.process_sale, name='process_sale'),
    path('exitosa/<int:venta_id>/', views.venta_exitosa, name='venta_exitosa'),
    
    path('ventas/caja/', views.ventas_por_caja, name='ventas_por_caja'),
    path('ventas/detalle/<int:venta_id>/', views.venta_detalle, name='venta_detalle'),
    
]