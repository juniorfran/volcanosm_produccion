from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic

from TPV_.Proveedores.models import Proveedor
from .models import Categoria, Producto
from .forms import ProductoForm

def producto_list(request):
    productos = Producto.objects.all()
    return render(request, 'productos/producto_list.html', {'productos': productos})

# def producto_detail(request, pk):
#     producto = get_object_or_404(Producto, pk=pk)
#     return render(request, 'productos/producto_detail.html', {'producto': producto})

def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('producto_list')
    else:
        form = ProductoForm()
    return render(request, 'productos/producto_form.html', {'form': form})

def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('producto_list')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/producto_form.html', {'form': form})

def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('producto_list')
    return render(request, 'productos/producto_confirm_delete.html', {'producto': producto})