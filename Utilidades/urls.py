from django.urls import path
from . import views

app_name = 'utilidades'

urlpatterns = [
        #UTILIDADES URL
    path("", views.index_utilidades, name="utilidades"),
    path('detalle/', views.consultar_detalle, name='detalle'),

    # Agrega más URL según sea necesario
]