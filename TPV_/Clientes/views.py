from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClienteForm
from .models import Cliente


@login_required
def cliente_list(request):
    query = request.GET.get('q', '').strip()
    clientes = Cliente.objects.all().order_by('apellido', 'nombre')
    if query:
        clientes = clientes.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(numero_documento__icontains=query) |
            Q(email__icontains=query) |
            Q(telefono__icontains=query)
        )
    return render(request, 'clientes/cliente_list.html', {
        'clientes': clientes,
        'query': query,
    })


@login_required
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado correctamente.')
            return redirect('cliente_list')
        messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = ClienteForm()
    return render(request, 'clientes/cliente_form.html', {
        'form': form,
        'titulo': 'Nuevo cliente',
    })


@login_required
def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado correctamente.')
            return redirect('cliente_list')
        messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/cliente_form.html', {
        'form': form,
        'cliente': cliente,
        'titulo': 'Editar cliente',
    })


@login_required
def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        try:
            cliente.delete()
            messages.success(request, 'Cliente eliminado correctamente.')
        except ProtectedError:
            messages.error(
                request,
                'No se puede eliminar el cliente porque está asociado a otros registros.'
            )
        except Exception:
            messages.error(request, 'Ocurrió un error al eliminar el cliente.')
        return redirect('cliente_list')
    return render(request, 'clientes/cliente_confirm_delete.html', {
        'cliente': cliente,
    })
