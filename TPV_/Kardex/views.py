from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from TPV_.utils import admin_required
from TPV_.Productos.models import Producto
from .models import MovimientoInventario
from .services import registrar_movimiento
from .forms import MovimientoForm


@login_required
def kardex_list(request):
    """Historial de movimientos con filtros por producto y tipo."""
    movimientos = MovimientoInventario.objects.select_related("producto", "usuario")

    producto_id = (request.GET.get("producto") or "").strip()
    tipo = (request.GET.get("tipo") or "").strip()

    if producto_id:
        movimientos = movimientos.filter(producto_id=producto_id)
    if tipo:
        movimientos = movimientos.filter(tipo=tipo)

    paginator = Paginator(movimientos, 25)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "kardex/kardex_list.html",
        {
            "page_obj": page_obj,
            "movimientos": page_obj.object_list,
            "productos": Producto.objects.all().order_by("nombre"),
            "tipos": MovimientoInventario.TIPOS,
            "producto_id": producto_id,
            "tipo": tipo,
        },
    )


@admin_required
def entrada_inventario(request):
    """Registra una entrada de mercadería o un ajuste manual de inventario."""
    if request.method == "POST":
        form = MovimientoForm(request.POST)
        if form.is_valid():
            producto = form.cleaned_data["producto"]
            tipo = form.cleaned_data["tipo"]
            cantidad = form.cleaned_data["cantidad"]
            motivo = form.cleaned_data["motivo"]
            try:
                registrar_movimiento(
                    producto,
                    tipo,
                    cantidad,
                    usuario=request.user,
                    motivo=motivo,
                )
                messages.success(
                    request,
                    f"Movimiento registrado: {dict(form.TIPO_CHOICES).get(tipo, tipo)} "
                    f"de {cantidad} en «{producto.nombre}».",
                )
                return redirect("kardex_list")
            except ValueError as exc:
                messages.error(request, str(exc))
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        initial = {}
        producto_id = request.GET.get("producto")
        if producto_id:
            initial["producto"] = producto_id
        form = MovimientoForm(initial=initial)
    return render(request, "kardex/entrada_inventario.html", {"form": form})
