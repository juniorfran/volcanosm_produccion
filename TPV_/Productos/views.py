from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render

from TPV_.utils import admin_required
from TPV_.Kardex.services import registrar_movimiento

from .forms import CategoriaForm, ProductoForm
from .models import Categoria, Producto


@login_required
def producto_list(request):
    """Listado de productos con buscador y alta rápida de categorías."""
    q = (request.GET.get("q") or "").strip()
    productos = Producto.objects.select_related("categoria", "proveedor").all()
    if q:
        productos = productos.filter(
            Q(nombre__icontains=q)
            | Q(codigo_de_barras__icontains=q)
            | Q(marca__icontains=q)
            | Q(categoria__nombre__icontains=q)
        )
    productos = productos.order_by("nombre")
    return render(
        request,
        "productos/producto_list.html",
        {
            "productos": productos,
            "q": q,
            "categoria_form": CategoriaForm(),
            "categorias": Categoria.objects.all().order_by("nombre"),
        },
    )


@admin_required
def producto_create(request):
    """Alta de producto. El stock inicial se registra vía kardex (entrada)."""
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.stock = 0
            producto.save()
            stock_inicial = form.cleaned_data.get("stock_inicial") or 0
            if stock_inicial > 0:
                registrar_movimiento(
                    producto,
                    "entrada",
                    stock_inicial,
                    usuario=request.user,
                    motivo="Stock inicial",
                    referencia="Alta de producto",
                )
            messages.success(request, f"Producto «{producto.nombre}» creado correctamente.")
            return redirect("producto_list")
        messages.error(request, "Corrige los errores del formulario.")
    else:
        form = ProductoForm()
    return render(
        request,
        "productos/producto_form.html",
        {"form": form, "es_creacion": True},
    )


@admin_required
def producto_update(request, pk):
    """Edición de producto. El stock NO se modifica aquí (se ajusta por kardex)."""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f"Producto «{producto.nombre}» actualizado correctamente.")
            return redirect("producto_list")
        messages.error(request, "Corrige los errores del formulario.")
    else:
        form = ProductoForm(instance=producto)
    return render(
        request,
        "productos/producto_form.html",
        {"form": form, "es_creacion": False, "producto": producto},
    )


@admin_required
def producto_delete(request, pk):
    """Eliminación de producto (POST + confirmación)."""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        try:
            producto.delete()
            messages.success(request, f"Producto «{producto.nombre}» eliminado.")
        except ProtectedError:
            messages.error(
                request,
                f"No se puede eliminar «{producto.nombre}» porque tiene movimientos o ventas asociadas.",
            )
        return redirect("producto_list")
    return render(
        request,
        "productos/producto_confirm_delete.html",
        {"producto": producto},
    )


@admin_required
def categoria_create(request):
    """Alta rápida de categoría."""
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f"Categoría «{categoria.nombre}» creada.")
        else:
            messages.error(request, "No se pudo crear la categoría.")
    return redirect("producto_list")
