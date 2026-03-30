# models.py
from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError

ROLES = (
        ('ADMIN', 'Administrador'),
        ('EMPLEADO', 'Empleado'),
    )

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    foto_perfil = models.ImageField(upload_to="perfiles/", blank=True, null=True)
    cedula = models.CharField(max_length=10, unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=10, null=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='EMPLEADO')  


    def __str__(self):
        return f'{self.usuario} -- Cedula: {self.cedula}'
    
    def clean(self):
        if self.pk is not None:
            original = Perfil.objects.get(pk=self.pk)
            if self.rol != original.rol:
                raise ValidationError("No está permitido cambiar el rol del perfil.")
            

class Actividad(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    
    def tiempo_relativo(self):
        from django.utils.timesince import timesince
        return timesince(self.fecha).split(',')[0]  
    
    def __str__(self):
        return f"{self.descripcion} ({self.usuario})"

