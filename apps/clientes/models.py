from django.db import models

# Create your models here.
class Pais(models.Model):
    nombre_pais = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'{self.nombre_pais}'

class Provincia(models.Model):
    nombre_provincia = models.CharField(max_length=100, unique=True)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nombre_provincia} -- {self.pais}'

class Ciudad(models.Model):
    nombre_ciudad = models.CharField(max_length=100, unique=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nombre_ciudad}'

class Cliente(models.Model):
    nombres = models.CharField(max_length=200)
    apellidos = models.CharField(max_length=200)
    correo = models.EmailField(null=True, unique=True, max_length=100)
    telefono = models.CharField(max_length=10, unique=True, null=False)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, null=True)
    direccion = models.TextField(null=True)
    dni = models.CharField(max_length=10, unique=True, null=False)
    fecha_nacimiento = models.DateField(null=False)
    imagen = models.ImageField(upload_to='clientes/', null=True, blank=True, default='clientes/cliente.png')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.nombres} {self.apellidos}'
    
