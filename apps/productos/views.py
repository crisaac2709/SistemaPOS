from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.db.models import Q, Sum, Case, When, IntegerField, Value, F
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import modelformset_factory
from apps.usuarios.models import Actividad
from .models import Producto, Stock
from .forms import CrearProducto, StockForm
from django.core.paginator import Paginator
from decimal import Decimal
from django.http import JsonResponse
from django.db.models import F
# Create your views here.

class CrearProductoView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = CrearProducto
    template_name = 'productos/crear.html'
    
    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('productos:detalle_producto', args=[self.object.id])


class ListarProductos(LoginRequiredMixin, ListView):
    model = Producto
    template_name = 'productos/listar.html'
    context_object_name = 'productos'
    ordering = ['-marca']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')

        if search:
            queryset = queryset.filter(nombre__icontains=search)
        
        return queryset

    

class DetalleProducto(LoginRequiredMixin, DetailView):
    model = Producto
    template_name = 'productos/detalle.html'


class ActualizarProducto(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = CrearProducto
    template_name = 'productos/update.html'

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('productos:detalle_producto', args=[self.object.id])


class EliminarProducto(LoginRequiredMixin, DeleteView):
    model = Producto
    template_name = 'productos/eliminar.html'
    success_url = reverse_lazy('productos:listar_productos')



@login_required
def productos_bajo_stock(request):
    productos = Producto.objects.annotate(
        entradas=Sum(Case(
            When(movimientos_stock__tipo='entrada', then=F('movimientos_stock__cantidad')),
            default=Value(0),
            output_field=IntegerField()
        )),
        salidas=Sum(Case(
            When(movimientos_stock__tipo='salida', then=F('movimientos_stock__cantidad')),
            default=Value(0),
            output_field=IntegerField()
        )),
        stock_total=F('entradas') - F('salidas')
    ).filter(
        stock_total__lte=5,
        activo=True
    ).exclude(
        categoria__nombre__iexact='Promociones'
    )

    data = [{
        'nombre': p.nombre,
        'stock': (p.entradas or 0) - (p.salidas or 0)
    } for p in productos]

    return JsonResponse({'productos': data})



@login_required
def movimientos_stock(request):
    productos = Producto.objects.order_by('nombre')

    producto_input = request.GET.get('producto')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    movimientos = Stock.objects.all().order_by('-fecha')

    if producto_input:
        try:
            producto_id = int(producto_input)
            movimientos = movimientos.filter(producto_id=producto_id)
        except ValueError:
            movimientos = movimientos.filter(producto__nombre__icontains=producto_input)

    if fecha_inicio:
        movimientos = movimientos.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        movimientos = movimientos.filter(fecha__date__lte=fecha_fin)

    paginator = Paginator(movimientos, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'productos/movimientos_stock.html', {
        'productos': productos,
        'page_obj': page_obj,
        'producto_id': producto_input,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    })


@login_required
def ingresar_unidades(request):
    StockFormSet = modelformset_factory(Stock, form=StockForm, extra=1, can_delete=False)

    if request.method == 'POST':
        formset = StockFormSet(request.POST)
        if formset.is_valid():
            movimientos = formset.save(commit=False)
            errores = []

            for movimiento in movimientos:
                if movimiento.cantidad is None or movimiento.cantidad <= 0:
                    errores.append(f"Cantidad inválida para producto {movimiento.producto.nombre}")
                else:
                    movimiento.tipo = 'entrada'
                    movimiento.usuario = request.user
                    movimiento.save()
                    Actividad.objects.create(
                        usuario=request.user,
                        descripcion=f"Ingresaste {movimiento.cantidad} unidades del producto {movimiento.producto.nombre}"
                    )

            if errores:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error en uno o más movimientos.',
                    'errors': errores
                }, status=400)

            return JsonResponse({
                'status': 'success',
                'message': 'Movimientos de stock registrados correctamente.'
            })

        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Errores en el formulario.',
                'errors': formset.errors
            }, status=400)

    else:
        formset = StockFormSet(queryset=Stock.objects.none())

    return render(request, 'productos/ingresar_unidades.html', {'formset': formset})