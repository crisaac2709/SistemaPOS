from django.db import models
from apps.productos.models import Producto
from apps.clientes.models import Cliente
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.exceptions import ValidationError

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
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True, blank=True)
    subtotal = models.DecimalField(default=0, decimal_places=2, max_digits=12, validators=[validar_positivo])
    iva = models.DecimalField(default=0, decimal_places=2, max_digits=12, validators=[validar_positivo])
    total = models.DecimalField(default=0, decimal_places=2, max_digits=12, validators=[validar_positivo])
    
    # CAMPOS OPCIONALES SOLO PARA PAGO CON TARJETA (PayPal)
    paypal_order_id = models.CharField(max_length=100, null=True, blank=True)   
    paypal_datos = models.JSONField(null=True, blank=True)        
    
    def __str__(self):
        return f"Venta #{self.id} - {self.cliente}"
    
    

class DetalleVenta(models.Model):   
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
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

    
