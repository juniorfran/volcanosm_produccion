from django.urls import path
from . import views

app_name = 'utilidades'

urlpatterns = [
        #UTILIDADES URL
    path("", views.index_utilidades, name="utilidades"),
    path('detalle/', views.consultar_detalle, name='detalle'),
    path('upload-data/', views.upload_data, name='upload_data'),
    
    
    path('mikrotik_manager/', views.mikrotik_login, name='mikrotik_manager'),
    path('mikrotik_interfaces/', views.mikrotik_interfaces, name='mikrotik_interfaces'),
    path('mikrotik_status/', views.mikrotik_status, name='mikrotik_status'),
    path('create_mikrotik_config/', views.create_mikrotik_config, name='create_mikrotik_config'),
    
    path('create_hotspot_user/', views.create_hotspot_user, name='create_hotspot_user'),
    path('create_hotspot_user_profile/', views.create_hotspot_user_profile, name='create_hotspot_user_profile'),
    path('list_hotspot_user_profile/', views.list_hotspot_user_profile, name='list_hotspot_user_profile'),
    path('list_hotspot_user/', views.list_hotspot_users, name='list_hotspot_user'),

    # Agrega más URL según sea necesario
]