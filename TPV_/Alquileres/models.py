from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from TPV_.Clientes.models import Cliente
from TPV_.Cajas.models import Cajas


class ArticuloAlquiler(models.Model):
    """Artículo que se alquila (tienda, colchoneta, hamaca, etc.)."""

    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(
        max_length=60, blank=True, help_text="Ej. Tienda, Colchoneta, Hamaca"
    )
    cantidad_total = models.PositiveIntegerField(default=0)
    cantidad_disponible = models.PositiveIntegerField(default=0)
    tarifa = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Tarifa por unidad (IVA incluido)"
    )
    deposito_sugerido = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to="alquileres", blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Artículo de alquiler"
        verbose_name_plural = "Artículos de alquiler"

    def __str__(self):
        return self.nombre

    @property
    def cantidad_alquilada(self):
        return (self.cantidad_total or 0) - (self.cantidad_disponible or 0)


class Alquiler(models.Model):
    """Transacción de alquiler: entrega de uno o más artículos a un cliente."""

    ESTADOS = [
        ("activo", "Activo (equipo fuera)"),
        ("parcial", "Devuelto parcial"),
        ("devuelto", "Devuelto"),
    ]

    numero = models.CharField(max_length=20, unique=True, null=True, blank=True, editable=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    caja = models.ForeignKey(Cajas, on_delete=models.PROTECT, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="activo")
    tipo_pago = models.CharField(max_length=20, default="efectivo")
    deposito = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_tarifa = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(blank=True)
    fecha_salida = models.DateTimeField(default=timezone.now)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.numero or f"Alquiler #{self.pk}"


class AlquilerDetalle(models.Model):
    alquiler = models.ForeignKey(Alquiler, on_delete=models.CASCADE, related_name="detalles")
    articulo = models.ForeignKey(ArticuloAlquiler, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    cantidad_devuelta = models.PositiveIntegerField(default=0)
    tarifa_unitaria = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def pendiente(self):
        return self.cantidad - self.cantidad_devuelta

    @property
    def subtotal(self):
        return self.tarifa_unitaria * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.articulo}"
