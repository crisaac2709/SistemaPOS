from django.db import models
from django.core.exceptions import ValidationError

from datetime import date, timedelta
import math
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from apps.productos.models import Producto
from apps.clientes.models import Cliente
from apps.ventas.models import Venta

from django.conf import settings
from apps.empresas.models import Empresa


def validar_positivo(valor):
    if valor < 0:
        raise ValidationError("El valor debe ser positivo")

TIPO_PAGO = [
    ('SEMANAL',"Semanal"),
    ('MENSUAL',"Mensual"),
]

ESTADO_CREDITO = [
    ('ACTIVO', 'Activo'),
    ('MOROSO','Moroso'),
    ('FINALIZADO', 'Finalizado'),
]

# Create your models here.
class Credito(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    montoInicial = models.DecimalField(max_digits=10, decimal_places=2, null=False, validators=[validar_positivo], default=0)
    montoTotal = models.DecimalField(max_digits=10, decimal_places=2, null=False, validators=[validar_positivo])
    fecha_inicio = models.DateField(null=False)
    fecha_fin = models.DateField(null=False)
    cuotas = models.IntegerField(null=True, validators=[validar_positivo])
    montoCuota = models.DecimalField(max_digits=10, decimal_places=2, null=True, validators=[validar_positivo])
    tipo_pago = models.CharField(max_length=7, choices=TIPO_PAGO, null=False)
    estado = models.CharField(max_length=10, default="ACTIVO", choices=ESTADO_CREDITO, null=False)
    venta = models.ForeignKey(Venta, on_delete=models.SET_NULL, null=True)
    cuotas_pagadas = models.IntegerField(default=0)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)


    def __str__(self):
         return f'Credito #{self.id} -- Cliente: {self.cliente}'
    

    #Metodos
    def verificarFechaFinalizacion(self):
            return self.fecha_inicio <= self.fecha_fin
    

    def CalcularMontoCuota(self):
        if self.tipo_pago == 'SEMANAL' :
            # Se calcula los dias para luego dividir en semanas
            dias = (self.fecha_fin - self.fecha_inicio).days

            if dias <= 0:
                 return 'Las fechas son iguales o la fecha de fin es anterior a la fecha de inicio.'
            
            self.cuotas = math.ceil(dias/7)
            montoCuota = (self.montoTotal - self.montoInicial) / self.cuotas
            self.montoCuota = montoCuota
        else:
            # Se calcula los meses
            meses = relativedelta(self.fecha_fin, self.fecha_inicio).months + relativedelta(self.fecha_fin, self.fecha_inicio).years * 12
            if meses <= 0:
                meses += 1
            

            self.cuotas = meses
            montoCuota = (self.montoTotal - self.montoInicial) / self.cuotas
            self.montoCuota = montoCuota
            

    def CalcularMontoPagado(self):
        pagos = Pago.objects.filter(credito = self.id)
        total = self.montoInicial + Decimal(sum(pago.monto for pago in pagos))
        return total


    def CompararMontoPagado(self):
        total_pagado = self.CalcularMontoPagado()
        if total_pagado == self.montoTotal:
            return True
        elif total_pagado > self.montoTotal:
            raise ValueError("El monto pagado excede el saldo pendiente.")
        else:
            return False
        
    
    def generar_fechas_pago(self):
        fechas_pago = []
        fecha_actual = self.fecha_inicio

        for cuota in range(1, self.cuotas + 1):
            if self.tipo_pago == 'SEMANAL':
                fecha_actual += timedelta(weeks=1)
            elif self.tipo_pago == 'MENSUAL':
                fecha_actual += relativedelta(months=1)
            
            fechas_pago.append({
                "cuota": cuota,
                "fecha": fecha_actual
            })

        return fechas_pago
    

    def verificar_pago_pendiente(self):
        fechas_programadas = self.generar_fechas_pago()
        hoy = date.today()
        pagos_realizados = Pago.objects.filter(credito=self.id).values_list('cuota', flat=True)

        cuotas_pendientes = []

        for pago in fechas_programadas:
            cuota_num = pago['cuota']
            fecha_pago = pago['fecha']

            if cuota_num not in pagos_realizados:
                if hoy == fecha_pago:
                    cuotas_pendientes.append((cuota_num, 'Hoy debe pagar esta cuota.', fecha_pago))
                elif hoy > fecha_pago:
                    cuotas_pendientes.append((cuota_num, '¡Pago atrasado!', fecha_pago))

        return cuotas_pendientes
    
    
    def verificar_estado(self):
        self.cuotas_pagadas = Pago.objects.filter(credito=self).count()
        deuda = self.deuda_pendiente

        if deuda <= 0:
            self.estado = 'FINALIZADO'
        elif date.today() > self.fecha_fin and deuda > 0:
            self.estado = 'MOROSO'
        else:
            self.estado = 'ACTIVO'

        self.save()

    def contar_cuotas_pagadas(self):
        return Pago.objects.filter(credito=self).count()
    
    @property
    def dias_restantes(self):
        return (self.fecha_fin - date.today()).days

    @property
    def esta_vencido(self):
        return date.today() > self.fecha_fin
    
    @property
    def deuda_pendiente(self):
        total_pagado = self.CalcularMontoPagado()
        monto_total = self.montoTotal
        deuda_pendiente = monto_total - total_pagado
        return deuda_pendiente
    
    @property
    def progreso(self):
        dias_totales = (self.fecha_fin - self.fecha_inicio).days
        dias_transcurridos = (date.today() - self.fecha_inicio).days
        return  min(100, max(0, int((dias_transcurridos / dias_totales) * 100)))
    
    
    
FORMAS_PAGO = [
         ('EFECTIVO', 'Efectivo'),
         ('TRANSFERENCIA', 'Transferencia'),
    ]


class Pago(models.Model):
    credito = models.ForeignKey(Credito, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha = models.DateField(auto_now=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[validar_positivo])
    cuota = models.IntegerField(validators=[validar_positivo])
    metodo_pago = models.CharField(max_length=13, choices=FORMAS_PAGO, default='EFECTIVO')
    comentarios = models.TextField(blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
         return f'Credito #{self.credito.id} -- Cliente: {self.credito.cliente} -- Pago: {self.id}'
    


class PlazoCredito(models.Model):
    meses = models.IntegerField(unique=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.meses} meses"
    
    
class PlanCredito(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='planes_credito')
    plazo = models.ForeignKey(PlazoCredito, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.producto.nombre} - {self.plazo.meses} meses - ${self.precio}"