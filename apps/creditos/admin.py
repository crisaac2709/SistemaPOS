from django.contrib import admin
from .models import Credito, Pago, PlanCredito, PlazoCredito

# Registro simple de Credito y Pago
admin.site.register(Credito)
admin.site.register(Pago)

# PlazoCredito admin
@admin.register(PlazoCredito)
class PlazoCreditoAdmin(admin.ModelAdmin):
    list_display = ('meses',)
    ordering = ('meses',)

# PlanCredito admin
@admin.register(PlanCredito)
class PlanCreditoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'plazo', 'precio')
    list_filter = ('producto', 'plazo')
    search_fields = ('producto__nombre',)
