from django.shortcuts import render, redirect, get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from apps.productos.models import Producto, Stock
from apps.clientes.models import Cliente
from apps.creditos.models import Credito
from apps.usuarios.models import Actividad
from apps.creditos.models import PlazoCredito
from apps.productos.models import Categoria
from .models import Impuesto
from .models import DetalleVenta, Venta, MetodoPago
from .forms import VentaForm, DetalleVentaFormSet
from io import BytesIO
import os
from datetime import datetime
from decimal import Decimal
from django.urls import reverse_lazy
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, DeleteView
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, DecimalField, Case, When, IntegerField, Value, Q
from django.db.models.functions import Coalesce
from django.db import transaction
from django.views.decorators.http import require_GET
import json
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@login_required
def crear_venta(request):
    porcentaje_iva = Decimal(Impuesto.objects.get(nombre='IVA').porcentaje) / 100
    porcentaje_interes = Decimal('0.00')
    if request.method == "POST":
        venta_form = VentaForm(request.POST)
        detalle_formset = DetalleVentaFormSet(request.POST)
        subtotal = Decimal(0)
        if venta_form.is_valid() and detalle_formset.is_valid():
            try:
                with transaction.atomic():
                    # 1. Guardar venta sin commit
                    venta = venta_form.save(commit=False)
                    detalles = detalle_formset.save(commit=False)
                    for detalle in detalles:
                        detalle.venta = venta
                        detalle.precio_unitario = Decimal(detalle.precio_unitario)
                        print(detalle.precio_unitario)
                        detalle.calcular_total()
                        subtotal += detalle.precio_unitario * detalle.cantidad
                        producto = detalle.producto
                        stock_actual = producto.stock_actual  
                        if stock_actual < detalle.cantidad:
                            raise ValueError(f'No hay stock suficiente del producto: {detalle.producto.nombre}')
                        # Actualiza unidades vendidas 
                        producto.unidades_vendidas += detalle.cantidad
                        producto.save()
                        # Registrar movimiento de salida en Stock
                        Stock.objects.create(
                            producto=producto,
                            cantidad=detalle.cantidad,
                            tipo='salida',
                            motivo=f'Venta',
                            usuario=request.user
                        )
                    # 2. Calcular totales según tipo de pago
                    if venta.metodo_pago.nombre_metodo == "Credito":
                        interes = subtotal * porcentaje_interes
                        print(interes)
                        venta.subtotal = subtotal + interes
                    else:
                        venta.subtotal = subtotal

                    venta.iva = venta.subtotal * porcentaje_iva
                    venta.total = venta.subtotal + venta.iva

                    print("Metodo de pago")
                    print(venta.metodo_pago.nombre_metodo)
                    # 3. Guardar venta con commit
                    venta.usuario = request.user
                    venta.save()

                    Actividad.objects.create(
                        usuario = request.user,
                        descripcion = f"Se registro una venta de ${venta.total}"
                    )

                    # 4. Guardar detalles de venta
                    for detalle in detalles:
                        detalle.save()

                    # 5. Si es crédito, crear objeto Credito
                    if venta.metodo_pago.nombre_metodo == "Credito":
                        fecha_inicio = request.POST.get('fecha_inicio')
                        fecha_fin = request.POST.get('fecha_fin')
                        forma_pago_credito = request.POST.get('forma_pago_credito')
                        montoInicial = Decimal(request.POST.get('montoInicial') or '0')
                        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

                        credito = Credito(
                            cliente=venta.cliente,
                            usuario=request.user,
                            montoTotal=venta.total,
                            montoInicial = montoInicial,
                            fecha_inicio=fecha_inicio,
                            fecha_fin=fecha_fin,
                            tipo_pago=forma_pago_credito,
                            venta=venta  
                        )

                        if not credito.verificarFechaFinalizacion():
                            raise ValueError("Las fechas asignadas no son válidas")

                        credito.CalcularMontoCuota()
                        credito.save()

                        Actividad.objects.create(
                            usuario = request.user,
                            descripcion = f"Aprobaste un credito a {venta.cliente.nombres} {venta.cliente.apellidos}"
                        )

                    if venta.metodo_pago.nombre_metodo == "Tarjeta de Credito" or venta.metodo_pago.nombre_metodo == "Tarjeta de Debito":
                        print("Entraste a venta por tarjeta")
                        print(venta)
                        return JsonResponse({
                            'status': 'esperando_pago', 
                            'venta_id': venta.pk,
                        })
                    
                    else:
                        print("venta a contado o credito")
                        return JsonResponse({
                            'status': 'ok',
                            'venta_id': venta.pk,
                            'redireccion': f'/ventas/venta/{venta.pk}/'
                        })

            except ValueError as e:
                return JsonResponse({
                    'status': 'error',
                    'mensaje': str(e)
                }, status=400)

            except Exception as e:
                print(f'Error inesperado: {str(e)}')
                return JsonResponse({
                    'status': 'error',
                    'mensaje': f'Error inesperado: {str(e)}'
                }, status=500)

    else:
        venta_form = VentaForm()
        detalle_formset = DetalleVentaFormSet()

    iva = Impuesto.objects.get(nombre='IVA')
    plazos = PlazoCredito.objects.all().order_by('meses')
    contexto = {
        'venta_form': venta_form,
        'detalle_formset': detalle_formset,
        'iva': iva,
        'plazos_credito' : plazos
    }
    return render(request, 'ventas/crear_venta.html', contexto)




@require_GET
def buscar_clientes(request):
    termino = request.GET.get('q', '')
    resultados = Cliente.objects.filter(
        Q(nombres__icontains=termino) |
        Q(apellidos__icontains=termino) |
        Q(correo__icontains=termino) |
        Q(dni__icontains=termino),
        activo=True
    )
    datos = [{
        'id': cliente.id,
        'nombre_completo': f"{cliente.nombres} {cliente.apellidos}",
        'correo': cliente.correo,
        'dni': cliente.dni,
        'telefono': cliente.telefono,
    } for cliente in resultados]
    return JsonResponse(datos, safe=False)




@require_GET
def buscar_productos(request):
    termino = request.GET.get('q', '')
    producto_id = request.GET.get('id', None)

    # 1. Definimos el cálculo del stock usando annotate
    # Coalesce convierte el NULL en 0 para evitar errores matemáticos
    queryset = Producto.objects.annotate(
        stock_calculado=Coalesce(
            Sum(Case(
                When(movimientos_stock__tipo='entrada', then='movimientos_stock__cantidad'),
                default=Value(0),
                output_field=IntegerField()
            )), 0) - 
        Coalesce(
            Sum(Case(
                When(movimientos_stock__tipo='salida', then='movimientos_stock__cantidad'),
                default=Value(0),
                output_field=IntegerField()
            )), 0)
    ).filter(activo=True)

    # 2. Aplicamos los filtros de búsqueda y la condición de stock > 0
    if producto_id:
        resultados = queryset.filter(id=producto_id, stock_calculado__gt=0)
    else:
        resultados = queryset.filter(
            Q(nombre__icontains=termino) | Q(descripcion__icontains=termino),
            stock_calculado__gt=0
        ).distinct()

    # 3. Construimos la respuesta
    datos = [{
        'id': producto.id,
        'nombre': producto.nombre,
        'precio': str(producto.precio),
        'stock_actual': producto.stock_calculado, # Usamos el valor ya calculado
    } for producto in resultados]

    return JsonResponse(datos, safe=False)


class ListarVentas(LoginRequiredMixin, ListView):
    model = Venta
    template_name = 'ventas/listar_ventas.html'
    context_object_name = 'ventas'
    ordering = ['-pk']
    paginate_by = 10

    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'perfil') and user.perfil.rol == 'ADMIN':
            return Venta.objects.all().order_by("-pk")
        else:
            return Venta.objects.filter(usuario=user).order_by("-fecha")


class DetalleVentaView(LoginRequiredMixin, DetailView):
    model = Venta
    template_name = 'ventas/detalle.html'
    context_object_name = "venta"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['detalles'] = DetalleVenta.objects.filter(venta=self.object)
        contexto['cliente'] = Cliente.objects.get(id = self.object.cliente_id)
        return contexto


class EliminarVentaView(LoginRequiredMixin, DeleteView):
    model = Venta
    template_name = 'ventas/eliminar.html'
    success_url = reverse_lazy('ventas:listar_ventas')



@login_required
def analisis_productos(request):
    # Capturar parámetros GET
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    categoria_id = request.GET.get('categoria')

    # Filtro base para las ventas y detalle de ventas
    filtro_detalle = {}

    if fecha_inicio and fecha_fin:
        filtro_detalle['detalleventa__venta__fecha__range'] = [fecha_inicio, fecha_fin]

    if categoria_id:
        filtro_detalle['categoria_id'] = categoria_id

    # Productos más vendidos
    mas_vendidos = Producto.objects.filter(**filtro_detalle).annotate(
        total_vendido=Coalesce(Sum('detalleventa__cantidad'), 0),
        veces_vendido=Count('detalleventa'),
        ingreso_total=Coalesce(
            Sum(F('detalleventa__cantidad') * F('detalleventa__precio_unitario')),
            Decimal(0),
            output_field=DecimalField()
        ),
        margen_ganancia=Coalesce(
            Sum(F('detalleventa__cantidad') * (F('detalleventa__precio_unitario') - F('costo'))),
            Decimal(0),
            output_field=DecimalField()
        )
    ).order_by('-total_vendido')[:5]

    # Productos menos vendidos (excluyendo los no vendidos)
    menos_vendidos = Producto.objects.filter(**filtro_detalle).annotate(
        total_vendido=Coalesce(Sum('detalleventa__cantidad'), 0),
        veces_vendido=Count('detalleventa'),
        ingreso_total=Coalesce(
            Sum(F('detalleventa__cantidad') * F('detalleventa__precio_unitario')),
            Decimal(0),
            output_field=DecimalField()
        ),
        margen_ganancia=Coalesce(
            Sum(F('detalleventa__cantidad') * (F('detalleventa__precio_unitario') - F('costo'))),
            Decimal(0),
            output_field=DecimalField()
        )
    ).filter(total_vendido__gt=0).order_by('total_vendido')[:5]

    # Productos no vendidos (se filtran por categoría si se selecciona)
    no_vendidos = Producto.objects.all()

    if categoria_id:
        no_vendidos = no_vendidos.filter(categoria_id=categoria_id)

    no_vendidos = no_vendidos.annotate(
        veces_vendido=Count('detalleventa')
    ).filter(veces_vendido=0)

    # Productos con mejor margen de ganancia
    mejor_margen = Producto.objects.filter(**filtro_detalle).annotate(
        margen_ganancia=Coalesce(
            Sum(F('detalleventa__cantidad') * (F('detalleventa__precio_unitario') - F('costo'))),
            Decimal(0),
            output_field=DecimalField()
        ),
        ganancia_unidad=Coalesce(
            (F('precio') - F('costo')),
            Decimal(0),
            output_field=DecimalField()
        )
    ).order_by('-margen_ganancia')[:5]

    # Productos con stock bajo (no necesita filtro por fecha)
    stock_bajo = Producto.objects.annotate(
        entradas=Sum(
            Case(
                When(movimientos_stock__tipo='entrada', then=F('movimientos_stock__cantidad')),
                default=Value(0),
                output_field=IntegerField()
            )
        ),
        salidas=Sum(
            Case(
                When(movimientos_stock__tipo='salida', then=F('movimientos_stock__cantidad')),
                default=Value(0),
                output_field=IntegerField()
            )
        )
    ).exclude(
        categoria__nombre__iexact='promociones'
    ).annotate(
        stock_calculado=F('entradas') - F('salidas')
    ).filter(
        stock_calculado__lte=5
    )

    # Estadísticas adicionales
    total_productos = Producto.objects.count()
    cantidad_productos_venta = Producto.objects.annotate(
        total_vendido=Coalesce(Sum('detalleventa__cantidad'), 0)
    ).filter(total_vendido__gt=0).count()

    categorias = Categoria.objects.all()

    context = {
        'mas_vendidos': mas_vendidos,
        'menos_vendidos': menos_vendidos,
        'no_vendidos': no_vendidos,
        'mejor_margen': mejor_margen,
        'stock_bajo': stock_bajo,
        'total_productos': total_productos,
        'cantidad_productos_venta': cantidad_productos_venta,
        'categorias': categorias
    }

    return render(request, 'productos/analisis_productos.html', context)



from datetime import datetime
@login_required
def generar_factura_pdf(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    detalles = DetalleVenta.objects.filter(venta=venta)
    logo_path = os.path.join(settings.MEDIA_ROOT, 'hogar.png')
    porcentaje_iva = Decimal(Impuesto.objects.get(nombre='IVA').porcentaje) 
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # ========== CONFIGURACIÓN ESTÉTICA ==========
    COLOR_TEXTO = colors.black
    COLOR_GRIS_SUAVE = colors.HexColor('#F2F2F2')
    COLOR_LINEA = colors.black
    FUENTE_BOLD = "Helvetica-Bold"
    FUENTE_REGULAR = "Helvetica"

    # ========== ENCABEZADO (FACTURA + LOGO) ==========
    p.setFont(FUENTE_REGULAR, 40)
    p.drawString(inch, height - 1.2*inch, "FACTURA")
    
    # Logo a la derecha (estilo minimalista)
    try:
        p.drawImage(logo_path, width - 2.5*inch, height - 1.5*inch, 
                   width=1.5*inch, height=1*inch, preserveAspectRatio=True, mask='auto')
    except:
        # Si no hay logo, ponemos la inicial como en la imagen
        p.setFont(FUENTE_BOLD, 30)
        p.drawString(width - 1.5*inch, height - 1.2*inch, "A")

    # Recuadro Número de Factura
    p.setLineWidth(1)
    p.rect(inch, height - 1.6*inch, 2.5*inch, 0.3*inch)
    p.setFont(FUENTE_BOLD, 10)
    p.drawString(inch + 0.1*inch, height - 1.53*inch, f"Nº: 000000000{venta.pk:02d}")

    # ========== LÍNEA DIVISORIA SUPERIOR ==========
    p.setStrokeColor(colors.lightgrey)
    p.line(0.5*inch, height - 1.8*inch, width - 0.5*inch, height - 1.8*inch)

    # ========== DATOS CLIENTE VS EMPRESA (COLUMNAS) ==========
    y_datos = height - 2.2*inch
    
    # Columna Izquierda: Cliente
    p.setFont(FUENTE_BOLD, 10)
    p.drawString(inch, y_datos, "DATOS DEL CLIENTE")
    p.setFont(FUENTE_REGULAR, 9)
    y_cli = y_datos - 0.25*inch
    p.drawString(inch, y_cli, f"{venta.cliente.nombres} {venta.cliente.apellidos}")
    p.drawString(inch, y_cli - 0.15*inch, f"Correo: {venta.cliente.correo}")
    p.drawString(inch, y_cli - 0.30*inch, f"Celular: {venta.cliente.telefono}")
    p.drawString(inch, y_cli - 0.45*inch, f"Direccion: {venta.cliente.direccion}")

    # Línea vertical separadora (estilo imagen)
    p.setStrokeColor(colors.black)
    p.line(width/2, y_datos, width/2, y_datos - 0.8*inch)

    # Columna Derecha: Empresa
    p.setFont(FUENTE_BOLD, 10)
    p.drawRightString(width - inch, y_datos, "DATOS DE LA EMPRESA")
    p.setFont(FUENTE_REGULAR, 9)
    y_emp = y_datos - 0.25*inch
    p.drawRightString(width - inch, y_emp, "Comercial Feria Hogar")
    p.drawRightString(width - inch, y_emp - 0.15*inch, "Correo: crisaac2002@gmail.com")
    p.drawRightString(width - inch, y_emp - 0.30*inch, "Celular: 0990216833")
    p.drawRightString(width - inch, y_emp - 0.45*inch, "Direccion: Av. 9 de Octubre, Naranjito")

    # ========== TABLA DE PRODUCTOS (SIN BORDES VERTICALES) ==========
    y_tabla = y_datos - 1.2*inch
    
    # Encabezado Tabla
    p.setLineWidth(1)
    p.line(inch, y_tabla, width - inch, y_tabla) # Línea superior
    p.line(inch, y_tabla - 0.3*inch, width - inch, y_tabla - 0.3*inch) # Línea inferior encabezado
    
    p.setFont(FUENTE_BOLD, 9)
    p.drawString(inch + 0.1*inch, y_tabla - 0.2*inch, "Detalle")
    p.drawCentredString(width - 3.5*inch, y_tabla - 0.2*inch, "Cantidad")
    p.drawCentredString(width - 2.3*inch, y_tabla - 0.2*inch, "Precio")
    p.drawRightString(width - inch - 0.1*inch, y_tabla - 0.2*inch, "Total")

    y_pos = y_tabla - 0.5*inch
    p.setFont(FUENTE_REGULAR, 9)

    for detalle in detalles:
        p.drawString(inch + 0.1*inch, y_pos, f"{detalle.producto.nombre}")
        p.drawCentredString(width - 3.5*inch, y_pos, f"{detalle.cantidad}")
        p.drawCentredString(width - 2.3*inch, y_pos, f"{detalle.precio_unitario:.2f} $")
        p.drawRightString(width - inch - 0.1*inch, y_pos, f"{detalle.subtotal:.2f} $")
        y_pos -= 0.25*inch
        
        if y_pos < 1.5*inch: # Salto de página simple
            p.showPage()
            y_pos = height - inch

    # ========== TOTALES (ALINEADOS A LA DERECHA) ==========
    # ========== SECCIÓN DE TOTALES ==========
    y_pos -= 0.3*inch
    p.setStrokeColor(colors.lightgrey)
    p.line(inch, y_pos + 0.15*inch, width - inch, y_pos + 0.15*inch)
    
    p.setFont(FUENTE_REGULAR, 10)

    # 1. SUBTOTAL (Nuevo bloque arriba del IVA)
    p.drawString(width - 3.5*inch, y_pos, "Subtotal")
    # Dejamos el espacio central vacío o puedes poner '-'
    p.drawRightString(width - inch - 0.1*inch, y_pos, f"{venta.subtotal:.2f} $")
    
    # Bajamos la posición para el IVA
    y_pos -= 0.25*inch 

    # 2. IVA
    p.drawString(width - 3.5*inch, y_pos, "IVA")
    p.drawCentredString(width - 2.3*inch, y_pos, f"{porcentaje_iva}%")
    p.drawRightString(width - inch - 0.1*inch, y_pos, f"{venta.iva:.2f} $")
    
    # 3. TOTAL FINAL (El cuadro negro)
    y_pos -= 0.4*inch
    p.setLineWidth(1)
    p.setStrokeColor(colors.black) # Asegurar que el borde sea negro
    p.rect(width - 3.8*inch, y_pos - 0.1*inch, 2.8*inch, 0.35*inch) 
    
    p.setFont(FUENTE_BOLD, 11)
    p.drawString(width - 3.7*inch, y_pos, "TOTAL")
    p.drawRightString(width - inch - 0.1*inch, y_pos, f"{venta.total:.2f} $")

    # ========== INFORMACIÓN DE PAGO ==========
    y_pago = y_pos - 1.2*inch
    p.setLineWidth(1)
    p.rect(inch, y_pago - 0.8*inch, 3*inch, 1.1*inch)
    p.setFont(FUENTE_BOLD, 10)
    p.drawString(inch + 0.1*inch, y_pago + 0.1*inch, "INFORMACIÓN DE PAGO")
    p.setFont(FUENTE_REGULAR, 9)
    p.drawString(inch + 0.1*inch, y_pago - 0.1*inch, f"Método: {venta.metodo_pago}")
    p.drawString(inch + 0.1*inch, y_pago - 0.25*inch, f"Vendedor: {venta.usuario}")
    p.drawString(inch + 0.1*inch, y_pago - 0.40*inch, f"Fecha de venta: {venta.fecha}")
    p.drawString(inch + 0.1*inch, y_pago - 0.55*inch, f"Hora: {venta.hora.strftime('%H:%M:%S')}")

    # ========== FOOTER (URL) ==========
    p.setFont(FUENTE_BOLD, 10)
    p.drawCentredString(width/2, 0.5*inch, "¡GRACIAS POR TU COMPRA!")

    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="factura_{venta.pk}.pdf"'
    return response