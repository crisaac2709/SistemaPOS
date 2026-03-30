from apps.clientes.models import Cliente
from apps.ventas.models import Venta, DetalleVenta
from apps.creditos.models import Credito
from apps.productos.models import Producto
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, ExtractWeekDay, TruncDate
from datetime import datetime

def CantidadClientes():
    return Cliente.objects.count()

def CantidadCreditos():
    return Credito.objects.count()

def CantidadProductos():
    return Producto.objects.count()

def Ventas_Mes_Actual():
    from django.utils import timezone
    hoy = timezone.now()
    ventas_mes_actual = Venta.objects.filter(
        fecha__year=hoy.year,
        fecha__month=hoy.month,
    )
    total = sum(venta.total for venta in ventas_mes_actual)
    return float(total)

def obtener_ventas_por_metodo_pago():
    metodos = Venta.objects.values('metodo_pago__nombre_metodo').annotate(total=Count('id'))
    print(metodos)
    return list(metodos)

def obtener_ingresos_por_dia():
    ingresos = (
        Venta.objects
        .annotate(dia=ExtractWeekDay('fecha'))
        .values('dia')
        .annotate(total=Sum('total'))
        .order_by('dia')
    )
    return [{"dia": i["dia"], "total": float(i["total"])} for i in ingresos]

def obtener_top_clientes():
    top_5 = (
        Venta.objects
        .exclude(cliente_id = 16)
        .values('cliente__nombres', 'cliente__apellidos')
        .annotate(total=Sum('total'))
        .order_by('-total')[:5]
    )
    return [
        {
            "cliente__nombres": i["cliente__nombres"],
            "cliente__apellidos": i["cliente__apellidos"],
            "total": float(i["total"])
        } for i in top_5
    ]

def obtener_estado_creditos():
    estado_creditos = (
        Credito.objects
        .values('estado')
        .annotate(cantidad=Count('id'))
    )
    return list(estado_creditos)

def obtener_ventas_por_mes():
    año_actual = datetime.now().year
    ventas_por_mes = (
        Venta.objects.filter(fecha__year=año_actual)
        .annotate(mes=TruncMonth('fecha'))
        .values('mes')
        .annotate(total_ventas=Sum('total'))
        .order_by('mes')
    )
    return [
        {"mes": v["mes"].strftime("%b"), "total_ventas": float(v["total_ventas"])}
        for v in ventas_por_mes
    ]

def obtener_productos_vendidos_por_categoria():
    datos = (
        DetalleVenta.objects
        .values("producto__categoria__nombre")
        .annotate(total_vendido=Sum("cantidad"))
        .order_by("-total_vendido")
    )
    return [
        {"categoria": d["producto__categoria__nombre"], "total_vendido": int(d["total_vendido"])}
        for d in datos
    ]
