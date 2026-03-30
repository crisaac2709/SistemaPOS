from django.apps import AppConfig


class CorreosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.correos'

    """
    def ready(self):
        from .utils import enviar_recordatorios_pago_una_vez_al_dia
        enviar_recordatorios_pago_una_vez_al_dia()
    """
    