from django.db import models

# Create your models here.
class EstadoEnvioCorreo(models.Model):
    ultima_ejecucion = models.DateField(null=True, blank=True)
    exito = models.BooleanField(default=False)

    def __str__(self):
        return f'Ultima ejecucion: {self.ultima_ejecucion or "Nunca"}'