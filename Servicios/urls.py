from django.urls import path
from . import views

urlpatterns = [
    path('servicios/', views.index_servicios, name='servicios'),  # Define la URL para tus servicios
]