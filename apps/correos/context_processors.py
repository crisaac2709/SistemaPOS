from datetime import date
from .models import EstadoEnvioCorreo


def estado_envio_correo_context(request):
    try:
        estado = EstadoEnvioCorreo.objects.get(id=1)
        return {
            'correo_enviado_hoy': estado.ultima_ejecucion == date.today() and estado.exito
        }
    except EstadoEnvioCorreo.DoesNotExist:
        return {'correo_enviado_hoy': False}
