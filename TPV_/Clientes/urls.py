from django.urls import path

from . import views

urlpatterns = [
    path('', views.cliente_list, name='cliente_list'),
    path('create/', views.cliente_create, name='cliente_create'),
    path('<int:pk>/update/', views.cliente_update, name='cliente_update'),
    path('<int:pk>/delete/', views.cliente_delete, name='cliente_delete'),
]
