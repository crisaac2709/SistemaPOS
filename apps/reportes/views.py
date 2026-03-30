from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from apps.ventas.models import Venta  
from apps.creditos.models import Credito
from apps.productos.models import Producto, Categoria, Marca
from django.core.paginator import Paginator

@login_required
def ReportesIndexView(request):
    return render(request, 'reportes/index.html')


@login_required
def ReporteVentasView(request):
    hoy = datetime.today()

    # Filtros de fecha
    fecha_desde_raw = request.GET.get('fecha_desde')
    fecha_hasta_raw = request.GET.get('fecha_hasta')

    if fecha_desde_raw:
        fecha_desde = datetime.strptime(fecha_desde_raw, "%Y-%m-%d")
    else:
        fecha_desde = hoy.replace(day=1)

    if fecha_hasta_raw:
        fecha_hasta = datetime.strptime(fecha_hasta_raw, "%Y-%m-%d")
    else:
        fecha_hasta = hoy

    # Queryset filtrado
    ventas_list = Venta.objects.filter(fecha__range=[fecha_desde, fecha_hasta]).order_by('-fecha')
    
    # Cálculo del total (sobre el total filtrado, no solo la página)
    total_ventas = sum(v.total for v in ventas_list)

    # --- LÓGICA DE PAGINACIÓN ---
    paginator = Paginator(ventas_list, 10)  # Muestra 10 ventas por página
    page_number = request.GET.get('page')
    ventas = paginator.get_page(page_number)

    context = {
        'ventas': ventas,  # Ahora 'ventas' es un objeto de página
        'total_ventas': total_ventas,
        'fecha_desde': fecha_desde, 
        'fecha_hasta': fecha_hasta,
        'fecha_desde_str': fecha_desde.strftime('%Y-%m-%d'),  
        'fecha_hasta_str': fecha_hasta.strftime('%Y-%m-%d'), 
    }

    return render(request, 'reportes/ventas.html', context)

@login_required
def ReporteCreditosView(request):
    hoy = datetime.today()

    # Filtros por rango de fechas
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    if fecha_desde:
        fecha_desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
    else:
        fecha_desde = hoy.replace(day=1).date()

    if fecha_hasta:
        fecha_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
    else:
        fecha_hasta = hoy.date()

    # Créditos otorgados en el rango
    creditos = Credito.objects.filter(fecha_inicio__range=[fecha_desde, fecha_hasta]).order_by('-fecha_inicio')

    creditos_activos = creditos.filter(estado='ACTIVO')
    creditos_morosos = creditos.filter(estado='MOROSO')

    total_creditos = creditos.count()
    total_morosos = creditos_morosos.count()

    context = {
        'creditos': creditos,
        'creditos_activos': creditos_activos,
        'creditos_morosos': creditos_morosos,
        'total_creditos': total_creditos,
        'total_morosos': total_morosos,
        'fecha_desde': fecha_desde.strftime("%Y-%m-%d"),
        'fecha_hasta': fecha_hasta.strftime("%Y-%m-%d"),
    }

    return render(request, 'reportes/creditos.html', context)


@login_required
def ReporteInventarioView(request):
    umbral = int(request.GET.get('umbral', 5))
    categoria_id = request.GET.get('categoria')
    marca_id = request.GET.get('marca')

    # Traer todas las categorías y marcas para los filtros
    categorias = Categoria.objects.all()
    marcas = Marca.objects.all()

    # Productos activos
    productos = Producto.objects.filter(activo=True)

    # Filtro por categoría (si seleccionaron)
    if categoria_id and categoria_id != '0':
        productos = productos.filter(categoria_id=categoria_id)

    # Filtro por marca (si seleccionaron)
    if marca_id and marca_id != '0':
        productos = productos.filter(marca_id=marca_id)

    # Calculamos stock_actual para todos
    productos_inventario = []
    for p in productos:
        productos_inventario.append({
            'producto': p,
            'stock_actual': p.stock_actual,
            'estado': 'BAJO' if p.stock_actual <= umbral else 'OK'
        })

    # Ordenar por menor stock
    productos_inventario.sort(key=lambda x: x['stock_actual'])

    productos_bajo = [p for p in productos_inventario if p['estado'] == 'BAJO']
    productos_ok = [p for p in productos_inventario if p['estado'] == 'OK']

    context = {
        'productos_inventario': productos_inventario,
        'productos_bajo': productos_bajo,
        'productos_ok': productos_ok,
        'categorias': categorias,
        'marcas': marcas,
        'umbral': umbral,
        'categoria_id': int(categoria_id) if categoria_id else 0,
        'marca_id': int(marca_id) if marca_id else 0,
    }

    return render(request, 'reportes/inventario.html', context)