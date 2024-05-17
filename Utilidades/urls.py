from django.urls import path
from . import views

app_name = 'utilidades'

urlpatterns = [
        #UTILIDADES URL
    path("", views.index_utilidades, name="utilidades"),
    path('detalle/', views.consultar_detalle, name='detalle'),
    path('upload-data/', views.upload_data, name='upload_data'),
    path('mikrotik_manager/', views.view_mikrotik_manager, name='mikrotik_manager'),

    # Agrega más URL según sea necesario
]