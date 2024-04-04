from datetime import timedelta
from decimal import Decimal
from django.db import transaction
from django.contrib import messages
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from TPV_.Cajas.models import Cajas
from TPV_.Clientes.models import Cliente
from TPV_.Productos.models import Producto
from django.contrib.auth.models import User

class Cart(models.Model):
    STATUS_CHOICES = (
        ('A', 'Activo'),
        ('I', 'Inactivo')
    )
    status = models.CharField('Estado', max_length=1, choices=STATUS_CHOICES, default='A')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    productos = models.ManyToManyField(Producto, through='CartItem', related_name='productos')

    def total_quantity(self):
        total_quantity = sum(item.quantity for item in self.cartitem_set.all())
        return total_quantity

    def total_price(self):
        total_price = sum(item.price() for item in self.cartitem_set.all())
        return total_price

    def is_new(self):
        return self.created_at >= timezone.now() - timedelta(minutes=30)


    def update_quantity(self, new_quantity, product):
        cart_item = self.cartitem_set.filter(product=product).first()
        if cart_item:
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            raise ValueError("Product not found in the cart")

    def __str__(self):
        return f'Cart for {self.user.username}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Producto, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    
    def price(self):
        total_price = self.product.precio_de_venta * self.quantity
        return total_price
    
    def decrement_quantity(self):
        if self.quantity > 1:
            self.quantity -= 1
            self.save()
        else:
            self.delete()


class TipoVenta(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre}"
    
        
class Ventas(models.Model):
    STATUS_CHOICES = (
        ('F', 'Finalizado'),
        ('P', 'Pendiente')
    )
    estado = models.CharField('Estado',max_length=1,choices=STATUS_CHOICES,default='A')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    caja = models.ForeignKey(Cajas, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    # productos = models.ManyToManyField(Producto, verbose_name=("productos"))
    tipo_venta = models.ForeignKey(TipoVenta, on_delete=models.CASCADE)
    tipo_pago = models.CharField(max_length=100)
    descuento = models.DecimalField(max_digits=10, decimal_places=2)
    recibe_caja = models.DecimalField(max_digits=10, decimal_places=2)
    cambio = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_hora_venta = models.DateTimeField(default=timezone.now)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    #funcion para calcular el cambio del cliente
    @property
    def calcular_cambio(self):          
        return round((self.recibe_caja - self.total), 2)
        
    def __str__(self):
        return f'{id} {self.tipo_venta}'
    

class VentasCredito(models.Model):
    venta = models.ForeignKey(Ventas, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, verbose_name=("productos"))
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    numero_factura = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    tiempo_cantidad = models.IntegerField(validators=[MinValueValidator(0)])
    tipo_tiempo = models.CharField(max_length=100)
    cuota = models.DecimalField(max_digits=10, decimal_places=2)
    total_deuda = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_actual = models.DecimalField(max_digits=10, decimal_places=2)
    porcentaje_interes = models.DecimalField(max_digits=5, decimal_places=2)
    interes_total = models.DecimalField(max_digits=10, decimal_places=2)
    interes_moratorio = models.DecimalField(max_digits=10, decimal_places=2)
    mora_total = models.DecimalField(max_digits=10, decimal_places=2)
    dias_atraso = models.IntegerField(validators=[MinValueValidator(0)])
    fecha_compra = models.DateTimeField(default=timezone.now)
    fecha_finalizacion = models.DateTimeField()
    metodo_pago = models.CharField(max_length=100)

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Ventas, on_delete=models.CASCADE)
    ticket_factura = models.CharField(max_length=100)
    productos = models.ManyToManyField(Producto, verbose_name="productos")
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    #GENERAR UN NUMERO DE TICKET CORRELATIVO QUE TENGA "VL-0000"
    def save(self, *args, **kwargs):
        # Generar número de ticket correlativo
        if not self.ticket_factura:
            last_ticket = DetalleVenta.objects.order_by('-ticket_factura').first()
            last_number = int(last_ticket.ticket_factura.split('-')[-1]) if last_ticket else 0
            new_number = last_number + 1
            self.ticket_factura = f"VL-{new_number:04d}"  # Formato "VL-XXXX"

        super().save(*args, **kwargs)


