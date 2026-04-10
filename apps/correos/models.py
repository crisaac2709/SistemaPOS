from django.db import models
from apps.empresas.models import Empresa

# Create your models here.
class EstadoEnvioCorreo(models.Model):
    ultima_ejecucion = models.DateField(null=True, blank=True)
    exito = models.BooleanField(default=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return f'Ultima ejecucion: {self.ultima_ejecucion or "Nunca"}'