import json
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import datetime
from apps.usuarios.views import es_admin


from .services import (
    CantidadClientes,
    CantidadCreditos,
    CantidadProductos,
    Ventas_Mes_Actual,
    obtener_ventas_por_metodo_pago,
    obtener_ingresos_por_dia,
    obtener_top_clientes,
    obtener_estado_creditos,
    obtener_ventas_por_mes,
    obtener_productos_vendidos_por_categoria
)


@login_required
def MyHome(request):
    año_actual = datetime.now().year

    datos_json = mark_safe(json.dumps({
        "metodo_pago": obtener_ventas_por_metodo_pago(),
        "ingresos_dia": obtener_ingresos_por_dia(),
        "top_clientes": obtener_top_clientes(),
        "estado_creditos": obtener_estado_creditos(),
        "ventas_mes": obtener_ventas_por_mes(),
        "ventas_categoria": obtener_productos_vendidos_por_categoria(),
    }))

    context = {
        "cantidad_clientes": CantidadClientes(),
        "ventas_mes_actual": Ventas_Mes_Actual(),
        "cantidad_creditos": CantidadCreditos(),
        "cantidad_productos": CantidadProductos(),
        "datos_json": datos_json,
        "año_actual": año_actual,
    }
    

    return render(request, 'auth/HomeAdmin.html', context)



