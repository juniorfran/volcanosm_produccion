from rest_framework import serializers
from .models import (
    Tipos, Accesos, Clientes, EnlacePagoAcceso, 
    TransaccionCompra, Transaccion3DS, 
    Transaccion3DS_Respuesta, TransaccionCompra3DS, MikrotikConfig
)

class TiposSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipos
        fields = '__all__'

class AccesosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accesos
        fields = '__all__'

class ClientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clientes
        fields = '__all__'

class EnlacePagoAccesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnlacePagoAcceso
        fields = '__all__'

class TransaccionCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransaccionCompra
        fields = '__all__'

class Transaccion3DSSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion3DS
        fields = '__all__'

class Transaccion3DS_RespuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion3DS_Respuesta
        fields = '__all__'

class TransaccionCompra3DSSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransaccionCompra3DS
        fields = '__all__'

class MikrotikConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = MikrotikConfig
        fields = '__all__'
