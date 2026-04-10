from django.db import models
from apps.clientes.models import Ciudad
from apps.empresas.models import Empresa

# Create your models here.
class Proveedor(models.Model):
    nombre = models.CharField(max_length=150, null=False)
    correo = models.EmailField(unique=True, null=False)
    direccion = models.CharField(max_length=300, null=False)
    telefono = models.CharField(max_length=10, unique=False)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE)
    ruc = models.CharField(max_length=13, unique=True, null=False)
    imagen = models.ImageField(upload_to='proveedores/')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nombre}'
    
    
    
