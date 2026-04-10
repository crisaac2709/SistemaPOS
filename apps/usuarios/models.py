# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from apps.empresas.models import Empresa
from django.conf import settings
from django.utils.timesince import timesince


class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True, null=False)

    def __str__(self):
        return f'{self.nombre}'
    
    
class CustomUser(AbstractUser):
    cedula = models.CharField(max_length=10, unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=10, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="usuarios", null=True, blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.username} - {self.empresa}'



class Actividad(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    descripcion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    
    def tiempo_relativo(self):
        return timesince(self.fecha).split(',')[0]  
    
    def __str__(self):
        return f"{self.descripcion} ({self.usuario})"

