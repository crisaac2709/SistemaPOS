from django.db import models
from apps.proveedores.models import Proveedor
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Sum, Case, When, IntegerField, Value

#Validacion de positivos
def validar_positivo(valor):
    if valor < 0:
        raise ValidationError("El valor debe ser positivo")


# Create your models here.
class Categoria(models.Model):
    nombre = models.CharField(max_length=150, unique=True, null=False)
    porcentaje_ganancia = models.DecimalField(max_digits=5, decimal_places=2, validators=[validar_positivo], default=0.0, null=True)


    def __str__(self):
        return f'{self.nombre}'

class Marca(models.Model):
    nombre = models.CharField(max_length=150, unique=True, null=False)

    def __str__(self):
        return f'{self.nombre}'

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(null=True)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True)
    costo = models.DecimalField(null=False, max_digits=12, decimal_places=2, validators=[validar_positivo])
    precio = models.DecimalField(null=True, max_digits=12, decimal_places=2, validators=[validar_positivo])
    imagen = models.ImageField(upload_to='productos/', null=True, default='productos/promocion.png')
    unidades_vendidas = models.IntegerField(default=0, validators=[validar_positivo])
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.nombre}'
    
    # En Producto
    @property
    def stock_actual(self):
        movimientos = self.movimientos_stock.aggregate(
            entradas=Sum(Case(When(tipo='entrada', then='cantidad'), default=Value(0), output_field=IntegerField())),
            salidas=Sum(Case(When(tipo='salida', then='cantidad'), default=Value(0), output_field=IntegerField())),
        )
        entradas = movimientos['entradas'] or 0
        salidas = movimientos['salidas'] or 0
        return entradas - salidas


class Stock(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos_stock' )
    fecha = models.DateTimeField(auto_now_add=True)
    cantidad = models.IntegerField(validators=[validar_positivo])
    tipo = models.CharField(max_length=10, choices=[('entrada', 'Entrada'), ('salida', 'Salida')])
    motivo = models.CharField(max_length=100, null=True, blank=True)  
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.tipo} de {self.cantidad} unidades - {self.producto.nombre}"


