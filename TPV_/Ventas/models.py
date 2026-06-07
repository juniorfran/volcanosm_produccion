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
        ('P', 'Pendiente'),
        ('A', 'Anulado'),
    )
    PAGO_CHOICES = (
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('otro', 'Otro'),
    )
    numero = models.CharField(max_length=20, unique=True, null=True, blank=True, editable=False)
    estado = models.CharField('Estado', max_length=1, choices=STATUS_CHOICES, default='F')
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    caja = models.ForeignKey(Cajas, on_delete=models.PROTECT)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    tipo_venta = models.ForeignKey(TipoVenta, on_delete=models.SET_NULL, null=True, blank=True)
    tipo_pago = models.CharField(max_length=20, choices=PAGO_CHOICES, default='efectivo')
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    recibe_caja = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cambio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_hora_venta = models.DateTimeField(default=timezone.now)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    @property
    def calcular_cambio(self):
        return round((self.recibe_caja - self.total), 2)

    def __str__(self):
        return self.numero or f'Venta #{self.pk}'
    

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
    venta = models.ForeignKey(Ventas, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, null=True, blank=True)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cantidad} x {self.producto}"


