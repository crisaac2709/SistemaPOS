from django.db import models
from apps.proveedores.models import Proveedor
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Sum, Case, When, IntegerField, Value
from apps.empresas.models import Empresa
from django.conf import settings

#Validacion de positivos
def validar_positivo(valor):
    if valor < 0:
        raise ValidationError("El valor debe ser positivo")


# Create your models here.
class Categoria(models.Model):
    nombre = models.CharField(max_length=150, unique=True, null=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE) 

    class Meta:
        # La combinación de NOMBRE + EMPRESA es lo que debe ser único
        unique_together = ('nombre', 'empresa')

    def __str__(self):
        return f'{self.nombre}'


class Marca(models.Model):
    nombre = models.CharField(max_length=150, unique=True, null=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE) 

    class Meta:
        unique_together = ('nombre', 'empresa')

    def __str__(self):
        return f'{self.nombre}'

class Producto(models.Model):
    nombre = models.CharField(max_length=250)
    descripcion = models.TextField(null=True)
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True)
    costo = models.DecimalField(null=False, max_digits=12, decimal_places=2, validators=[validar_positivo])
    precio = models.DecimalField(null=True, max_digits=12, decimal_places=2, validators=[validar_positivo])
    imagen = models.ImageField(upload_to='productos/', null=True, default='productos/promocion.png')
    unidades_vendidas = models.IntegerField(default=0, validators=[validar_positivo])
    activo = models.BooleanField(default=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nombre}'
    
    @property
    def utilidad(self):
        return self.precio - self.costo
    
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
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE) 


    def __str__(self):
        return f"{self.tipo} de {self.cantidad} unidades - {self.producto.nombre}"


