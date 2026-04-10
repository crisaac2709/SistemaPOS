from django.db import models
from apps.empresas.models import Empresa
from django.conf import settings

# Create your models here.
class Pais(models.Model):
    nombre_pais = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'{self.nombre_pais}'

class Provincia(models.Model):
    nombre_provincia = models.CharField(max_length=100, unique=True)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nombre_provincia}'

class Ciudad(models.Model):
    nombre_ciudad = models.CharField(max_length=100, unique=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nombre_ciudad}'

class Cliente(models.Model):
    nombres = models.CharField(max_length=200)
    apellidos = models.CharField(max_length=200)
    correo = models.EmailField(null=True, max_length=100, blank=True)
    telefono = models.CharField(max_length=10, unique=True, null=True, blank=True)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True)
    direccion = models.TextField(null=True)
    dni = models.CharField(max_length=10, null=False)
    fecha_nacimiento = models.DateField(null=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['dni', 'empresa'], 
                name='unique_dni_por_empresa'
            ),
            models.UniqueConstraint(
                fields=['correo', 'empresa'], 
                name='unique_correo_por_empresa'
            )
        ]

    def __str__(self):
        return f'{self.nombres} {self.apellidos}'
    
