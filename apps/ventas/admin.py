from django.contrib import admin
from .models import Venta, DetalleVenta, MetodoPago, Impuesto

# Register your models here.
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(MetodoPago)
admin.site.register(Impuesto)

