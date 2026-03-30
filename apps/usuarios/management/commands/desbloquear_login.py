from django.core.management.base import BaseCommand
from axes.handlers.proxy import AxesProxyHandler

class Command(BaseCommand):
    help = 'Resetea los intentos fallidos de login (bloqueos de django-axes)'

    def handle(self, *args, **kwargs):
        AxesProxyHandler.reset_attempts()
        self.stdout.write(self.style.SUCCESS('✅ Intentos de login reseteados. Puedes probar a iniciar sesión de nuevo.'))
