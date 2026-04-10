from django.db import models
from apps.productos.models import Producto
from apps.clientes.models import Cliente
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.conf import settings
from apps.empresas.models import Empresa

class MetodoPago(models.Model):
    nombre_metodo = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return f'{self.nombre_metodo}'

def validar_positivo(valor):
    if valor < 0:
        raise ValidationError("El valor debe ser positivo.")



# Create your models here.
class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True, blank=True)
    subtotal = models.DecimalField(default=0, decimal_places=2, max_digits=12, validators=[validar_positivo])
    iva = models.DecimalField(default=0, decimal_places=2, max_digits=12, validators=[validar_positivo])
    total = models.DecimalField(default=0, decimal_places=2, max_digits=12, validators=[validar_positivo])
    
    
    def __str__(self):
        return f"Venta #{self.id} - {self.cliente} - Total: ${self.total}"
    
    

class DetalleVenta(models.Model):   
    venta = models.ForeignKey(Venta, on_delete=models.PROTECT, related_name='detalles')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1, validators=[validar_positivo])
    precio_unitario = models.DecimalField(default=0, decimal_places=2, max_digits=12, validators=[validar_positivo])
    subtotal = models.DecimalField(default=0, decimal_places=2, max_digits=12, validators=[validar_positivo])

    def __str__(self):
        return f"Detalle de Venta #{self.id}"
    
    #Metodos
    def calcular_total(self):
        self.subtotal = Decimal(self.cantidad * self.precio_unitario)


class Impuesto(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.nombre}: {self.porcentaje}%"

    
