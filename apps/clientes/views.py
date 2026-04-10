from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, UpdateView, TemplateView, DeleteView, DetailView, CreateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from .forms import RegistrarClienteForm
from .models import Cliente
from apps.ventas.models import Venta
from django.db.models import Q
from django.http import JsonResponse
from .models import Provincia, Ciudad

def cargar_provincias(request):
    pais_id = request.GET.get('pais_id')
    provincias = Provincia.objects.filter(pais_id=pais_id).order_by('nombre_provincia')
    return JsonResponse(list(provincias.values('id', 'nombre_provincia')), safe=False)

def cargar_ciudades(request):
    provincia_id = request.GET.get("provincia_id")
    ciudades = Ciudad.objects.filter(provincia_id=provincia_id).order_by('nombre_ciudad')
    return JsonResponse(list(ciudades.values('id', 'nombre_ciudad')), safe=False)

# Create your views here.
class CrearCliente(LoginRequiredMixin, CreateView):
    model = Cliente
    template_name = 'clientes/crear_cliente.html'
    form_class = RegistrarClienteForm

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('clientes:detalle_cliente', args=[self.object.id])

class ListarClientes(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'clientes/listar.html'
    context_object_name = "clientes"
    paginate_by = 10 
    
    def get_queryset(self):
        # Usamos select_related para que el listado sea rápido
        queryset = Cliente.objects.filter(
            empresa=self.request.user.empresa
        ).select_related('ciudad__provincia__pais')

        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(nombres__icontains=search) | 
                Q(apellidos__icontains=search) |
                Q(dni__icontains=search)
            )
        return queryset.order_by("apellidos")

class VerDetalleCliente(LoginRequiredMixin, DetailView): # El Mixin va PRIMERO
    model = Cliente
    template_name = "clientes/detalle_cliente.html"
    context_object_name = "cliente"

    def get_queryset(self):
        # CORREGIDO: Se debe especificar el campo 'empresa='
        return Cliente.objects.filter(empresa=self.request.user.empresa)

class ActualizarCliente(LoginRequiredMixin, UpdateView):
    model = Cliente
    template_name = 'clientes/crear_cliente.html' # Reutiliza el mismo template si quieres
    form_class = RegistrarClienteForm

    def get_queryset(self):
        return Cliente.objects.filter(empresa=self.request.user.empresa)
    
    def get_success_url(self):
        return reverse('clientes:detalle_cliente', args=[self.object.id])

class EliminarCliente(LoginRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'clientes/eliminar.html'
    success_url = reverse_lazy('clientes:listar_clientes')

    def get_queryset(self):
        return Cliente.objects.filter(empresa=self.request.user.empresa)


def historial_compra_cliente(request, cliente_id): 
    cliente = get_object_or_404(Cliente, id=cliente_id, empresa=request.user.empresa)

    # Traer todas las ventas de ese cliente, ordenadas por fecha descendente
    ventas = Venta.objects.filter(cliente=cliente, empresa = request.user.empresa).prefetch_related('detalles__producto').order_by('-fecha', '-hora')
    total_cliente = ventas.aggregate(total=Sum('total'))['total'] or 0

    return render(request, 'clientes/historial_compras.html', {
        'cliente': cliente,
        'ventas': ventas,
        'total_cliente': total_cliente
    })
