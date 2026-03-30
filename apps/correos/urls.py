from django.urls import path
from .views import enviar_recordatorio_pago, confirmacion_envio_recordatorios

app_name = "correos"

urlpatterns = [
    path('enviar-recordatorio-pago/', enviar_recordatorio_pago, name="enviar-recordatorio-pago"),
    path('confirmar_envio_recordatorio', confirmacion_envio_recordatorios, name="confirmar_envio_recordatorio"),
]