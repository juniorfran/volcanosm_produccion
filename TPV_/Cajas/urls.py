from django.urls import path
from . import views

urlpatterns = [
    
    # URL PARA CAJAS
    path('caja/', views.cajas_list, name='cajas_list'),
    path('create/', views.cajas_create, name='cajas_create'),
    path('update/<int:pk>/', views.cajas_update, name='cajas_update'),
    path('delete/<int:pk>/', views.cajas_delete, name='cajas_delete'),
    path('open/<int:pk>/', views.caja_open, name='caja_open'),
    path('close/<int:pk>/', views.caja_close, name='caja_close'),
    path('count/<int:pk>/', views.caja_count, name='caja_count'),
    
    # REPORTE DE APERTURAS
    path('reporte_apertura/', views.generar_reporte, name='reporte_aperturas'),
]