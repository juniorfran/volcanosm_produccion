from celery import shared_task
from .models import Reserva

@shared_task
def actualizar_estado_reserva():
    reserva = Reserva.objects.latest('id')
    reserva.actualizar_estado()