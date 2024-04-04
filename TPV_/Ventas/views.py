from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from TPV_.Cajas.models import Cajas, MovimientoCaja
from TPV_.Clientes.models import Cliente
from TPV_.Productos.models import Categoria, Producto
from .models import Cart, CartItem, DetalleVenta, TipoVenta, Ventas, VentasCredito
from django.views.generic import View
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from decimal import Decimal
from collections import defaultdict
from django import template
import pdb


# VISTA PARA REALIZAR UNA VENTA CREANDO DE FORMA AUTOMATICA EL CARRITO DE COMPRAS



def get_caja_abierta():
    """Return the open cash register"""
    return Cajas.objects.filter(estado='abierto').first()

@login_required
def process_sale(request):
    try:
        cart = Cart.objects.filter(user=request.user, status='A').first()
        if not cart:
            return HttpResponse("El carrito está vacío")

        if request.method == 'POST':
            recibe_caja_str = request.POST.get('recibe_caja')
            recibe_caja_str = recibe_caja_str.replace(',', '.') 
            recibe_caja = Decimal(recibe_caja_str) if recibe_caja_str else Decimal(0.0)
            
            total_venta_str = request.POST.get('total_venta')
            total_venta_str = total_venta_str.replace(',', '.')  
            total_venta = Decimal(total_venta_str)

            venta_total = Decimal(0)  # Variable para almacenar el total de la venta

            # Calcular el total de la venta sumando el precio de venta de cada producto en el carrito
            for cart_item in cart.cartitem_set.all():
                producto = cart_item.product
                cantidad = cart_item.quantity
                venta_total += producto.precio_de_venta * cantidad

            # Calcular el total de la venta incluyendo el impuesto
            total = venta_total + (venta_total * Decimal(0.13))

            # Crear una única venta en la base de datos
            venta = Ventas.objects.create(
                cart=cart,
                caja=Cajas.objects.get(estado='abierto'),
                tipo_venta=TipoVenta.objects.get(nombre='Venta al público'),
                tipo_pago='Efectivo',
                descuento=0,
                recibe_caja=recibe_caja,
                cambio=recibe_caja - total_venta,
                subtotal=venta_total,
                iva=Decimal(0.13),
                total=total,
                fecha_hora_venta=timezone.now(),
                estado="F"
            )

            # Para cada producto en el carrito, crear un detalle de venta asociado a la venta creada
            for cart_item in cart.cartitem_set.all():
                producto = cart_item.product
                cantidad = cart_item.quantity
                subtotal = producto.precio_de_venta * cantidad

                detalle_venta = DetalleVenta.objects.create(
                    venta=venta,
                    cantidad=cantidad,
                    precio_unitario=producto.precio_de_venta,
                    iva=Decimal(0.13),
                    subtotal=subtotal
                )

                detalle_venta.productos.add(producto)

                # Actualizar el stock del producto
                producto.stock -= cantidad
                producto.save()
            
            
            # Registrar movimiento en caja
            caja = Cajas.objects.get(estado='abierto')
            caja.monto_ventas += total
            caja.monto_total_efectivo += venta_total
            caja.efectivo_cierre = caja.efectivo_cierre or Decimal(0)
            caja.efectivo_cierre += total
            caja.save()

            # Marcar el carrito como inactivo
            cart.status = 'I'
            cart.save()

            # Redirigir a la vista de venta exitosa con el ID de la venta recién creada
            return redirect("venta_exitosa", venta_id=venta.id)
        
        else:
            return HttpResponse("Método no permitido")
    except Exception as e:
        return HttpResponse(f"Error al procesar la venta: {str(e)}")


@login_required
def punto_ventas(request):
    productos = Producto.objects.filter(status='A')
    caja_abierta = Cajas.objects.filter(estado='abierto').first()
    caja_usuario = Cajas.objects.get(usuario_responsable=request.user)

    current_date = timezone.now().date()
    
    caja_nombre = caja_usuario.nombre_caja
    
    context = {
        'productos': productos, 
        'caja_abierta': caja_abierta,
        'current_date': current_date,
        'caja_nombre': caja_nombre,
    }
    
    return render(request, 'tpv/punto_ventas.html', context)


def calcular_impuesto(cart):
    # Supongamos que el impuesto es el 10% del subtotal
    impuesto_porcentaje = Decimal('0.13')
    impuesto = cart.total_price() * impuesto_porcentaje
    return impuesto

@login_required
def venta_exitosa(request, venta_id):
    try:
        # Obtener los detalles de la venta con el ID proporcionado
        venta = Ventas.objects.get(id=venta_id)

        # Obtener los detalles del carrito relacionado a la venta
        cart = venta.cart

        # Crear una lista de diccionarios con los detalles de los productos
        productos = []
        for cart_item in cart.cartitem_set.all():
            producto = cart_item.product
            cantidad = cart_item.quantity
            subtotal = producto.precio_de_venta * cantidad
            productos.append({
                'nombre': producto.nombre,
                'cantidad': cantidad,
                'precio_de_venta': producto.precio_de_venta,
                'subtotal': subtotal,
            })

        # Calcular los subtotales, el IVA y el total
        subtotal = sum(item['subtotal'] for item in productos)
        impuesto = subtotal * Decimal(0.13)
        total = subtotal + impuesto

        # Pasar los detalles de la venta al contexto de la plantilla
        context = {
            'venta': venta,
            'productos': productos,
            'subtotal': subtotal,
            'impuesto': impuesto,
            'total': total,
        }

        return render(request, 'tpv/venta_exitosa.html', context)
    except Ventas.DoesNotExist:
        return HttpResponse("No se encontró la venta especificada.")



@login_required
def shopping_cart(request):
    cart = Cart.objects.filter(user=request.user, status='A').first()
    productos = Producto.objects.filter(status='A')
    
    if cart:
        cart_items = cart.cartitem_set.all()
        
        # Calcular la cantidad total de cada producto en el carrito
        product_counts = {}
        for item in cart_items:
            product_id = item.product.id
            if product_id in product_counts:
                product_counts[product_id] += item.quantity
            else:
                product_counts[product_id] = item.quantity
        
        subtotal = cart.total_price()
        impuesto = calcular_impuesto(cart)  # Puedes calcular el impuesto aquí
        total = subtotal + impuesto
        
        context = {
            'cart': cart, 
            'productos': productos, 
            'impuesto': impuesto, 
            'total': total, 
            'subtotal': subtotal, 
            'product_counts': product_counts,
        }
        print (total, impuesto, subtotal)
    else:
        # Si el usuario no tiene un carrito activo, puedes manejar este caso como desées
        context = {
            'message': 'No tienes ningún carrito activo',
        }

    return render(request, 'tpv/punto_ventas.html', context)


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Producto, id=product_id)
    cart = Cart.objects.filter(user=request.user, status='A').first()
    
    if not cart:
        # Crear un nuevo carrito activo para el usuario si no existe uno o si el existente está inactivo
        cart = Cart.objects.create(user=request.user, status='A')

    if product in cart.productos.all():
        # El producto ya está en el carrito, actualiza la cantidad
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity += 1
        cart_item.save()
    else:
        # El producto no está en el carrito, agregalo al carrito
        cart_item = CartItem.objects.create(cart=cart, product=product, quantity=1)

    messages.success(request, f'Producto "{product.nombre}" añadido al carrito de compras.')
    return redirect('shopping_cart')

@login_required
def update_cart_item(request, cart_item_id, new_quantity):
    cart_item = get_object_or_404(Cart, id=cart_item_id)
    cart_item.update_quantity(new_quantity)
    return redirect('shopping_cart')

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.decrement_quantity()  # No es necesario pasar el producto aquí
    return redirect('shopping_cart')




@login_required
def ventas_por_caja(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        ventas = Ventas.objects.filter(fecha_hora_venta__range=[start_date, end_date], caja__isnull=False)
    else:
        ventas = Ventas.objects.filter(caja__isnull=False)

    context = {
        'ventas': ventas
    }

    return render(request, 'tpv/general_ventas.html', context)

@login_required
def venta_detalle(request, venta_id):
    try:
        # Obtener los detalles de la venta con el ID proporcionado
        venta = Ventas.objects.get(id=venta_id)

        # Obtener los detalles del carrito relacionado a la venta
        cart = venta.cart

        # Crear una lista de diccionarios con los detalles de los productos
        productos = []
        for cart_item in cart.cartitem_set.all():
            producto = cart_item.product
            cantidad = cart_item.quantity
            subtotal = producto.precio_de_venta * cantidad
            productos.append({
                'nombre': producto.nombre,
                'cantidad': cantidad,
                'precio_de_venta': producto.precio_de_venta,
                'subtotal': subtotal,
            })

        # Calcular los subtotales, el IVA y el total
        subtotal = sum(item['subtotal'] for item in productos)
        impuesto = subtotal * Decimal(0.13)
        total = subtotal + impuesto

        # Pasar los detalles de la venta al contexto de la plantilla
        context = {
            'venta': venta,
            'productos': productos,
            'subtotal': subtotal,
            'impuesto': impuesto,
            'total': total,
        }

        return render(request, 'tpv/detalle_venta.html', context)
    except Ventas.DoesNotExist:
        return HttpResponse("No se encontró la venta especificada.")