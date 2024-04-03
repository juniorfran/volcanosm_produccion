from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from ckeditor.fields import RichTextField
from TPV_.Proveedores.models import Proveedor

class Categoria(models.Model):
    nombre = models.CharField("Nombre", max_length=50)
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    STATUS_CHOICES = (
        ('A', 'Activo'),
        ('I', 'Inactivo')
    )
    nombre = models.CharField(max_length=255)
    descripcion = RichTextField()
    codigo_de_barras = models.CharField(max_length=100)
    sku = models.IntegerField()
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    stock_minimo = models.IntegerField(validators=[MinValueValidator(0)])
    presentacion_producto = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_de_compra = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    precio_de_venta = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    precio_al_por_mayor = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    porcentaje_de_descuento = models.DecimalField(max_digits=4, decimal_places=2)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    producto_perecedero = models.BooleanField(default=False)
    fecha_de_expiracion = models.DateTimeField(null=True, blank=True)
    tiempo_de_garantia = models.CharField(max_length=100)
    tiempo_de_garantia_tipo = models.CharField(max_length=100)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='productos')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    status = models.CharField('Estado',max_length=1,choices=STATUS_CHOICES,default='A')
    existencia_en_inventario = models.IntegerField(default=0, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField('Ultima Modificación', auto_now=True)
    imagen = models.ImageField(upload_to='products/')
    
    def clean_sku(self):
        if self.sku < 1:
            raise ValidationError({'sku': 'SKU should be greater than 0'})

    def clean_stock(self):
        if self.stock < 0:
            raise ValidationError({'stock': 'Stock should be 0 or greater'})

    def clean_stock_minimo(self):
        if self.stock_minimo < 0:
            raise ValidationError({'stock_minimo': 'Minimum stock should be 0 or greater'})

    def clean_precio_de_compra(self):
        if self.precio_de_compra < Decimal('0.01'):
            raise ValidationError({'precio_de_compra': 'Purchase price should be greater than 0'})

    def clean_precio_de_venta(self):
        if self.precio_de_venta < Decimal('0.01'):
            raise ValidationError({'precio_de_venta': 'Selling price should be greater than 0'})

    def clean_precio_al_por_mayor(self):
        if self.precio_al_por_mayor < Decimal('0.01'):
            raise ValidationError({'precio_al_por_mayor': 'Wholesale price should be greater than 0'})
        
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def save(self, *args, **kwargs):
        if not self.precio_de_venta:
            self.precio_de_venta = self.precio_de_compra
        super(Producto, self).save(*args,**kwargs)
        
    @property
    def es_activo(self):
        return self.status == 'A'

    def __str__(self):
        return f"{self.nombre} ({self.stock})"