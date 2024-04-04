from django.db import models
from django.contrib.auth.models import User

# Create your models here.
## MODELOS PARA CAJAS
class Cajas(models.Model):
    ESTADO_CHOICES = (
        ('abierto', 'Abierto'),
        ('cerrado', 'Cerrado'),
        ('en_proceso', 'En proceso'),
    )
    numero_caja = models.CharField(max_length=50)
    nombre_caja = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    efectivo_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    efectivo_cierre = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_hora_apertura = models.DateTimeField()
    fecha_hora_cierre = models.DateTimeField(null=True, blank=True)
    usuario_responsable = models.ForeignKey(User, on_delete=models.CASCADE)
    monto_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_gastos_devoluciones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_total_efectivo = models.DecimalField(max_digits=10, decimal_places=2)
    informacion_auditoria = models.TextField()
    comentarios_notas = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.nombre_caja
    
class AperturaCaja(models.Model):
    caja = models.ForeignKey(Cajas, on_delete=models.CASCADE, related_name='aperturas')
    efectivo_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_hora_apertura = models.DateTimeField()
    usuario_responsable = models.ForeignKey(User, on_delete=models.CASCADE)
    comentarios_notas = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
class CierreCaja(models.Model):
    caja = models.ForeignKey(Cajas, on_delete=models.CASCADE, related_name='cierres')
    efectivo_cierre = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_hora_cierre = models.DateTimeField()
    usuario_responsable = models.ForeignKey(User, on_delete=models.CASCADE)
    comentarios_notas = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
# HACER ESTO CUANDO YA SE TRABAJE EL APARTADO DE VENTAS
class MovimientoCaja(models.Model):
    caja = models.ForeignKey(Cajas, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    TIPOS_MOVIMIENTOS = (
        ('venta', 'Venta'),
        ('compra', 'Compra'),
        ('cierre', 'Cierre'),
        ('apertura', 'Apertura'),
        ('devuelta', 'Devolución'),
        
    )
    tipo_movimiento = models.CharField(max_length=50, choices=TIPOS_MOVIMIENTOS)
    efectivo_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_efectivo = models.DecimalField(max_digits=10, decimal_places=2)
    efectivo_actual = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.CharField(max_length=100)
    numero_remesa = models.CharField(max_length=100, null=True, blank=True)
    banco_remesa = models.CharField(max_length=100, null=True, blank=True)
    cantidad_remesado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
