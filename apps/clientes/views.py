from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, UpdateView, TemplateView, DeleteView, DetailView, CreateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from .forms import RegistrarClienteForm
from .models import Cliente
from apps.ventas.models import Venta
from django.db.models import Q


# Create your views here.
class CrearCliente(LoginRequiredMixin, CreateView):
    model = Cliente
    template_name = 'clientes/crear_cliente.html'
    form_class = RegistrarClienteForm

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('clientes:detalle_cliente', args=[self.object.id])

class VerDetalleCliente(DetailView, LoginRequiredMixin):
    model = Cliente
    template_name = "clientes/detalle_cliente.html"

class ListarClientes(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'clientes/listar.html'
    context_object_name = "clientes"
    ordering = ['apellidos']
    paginate_by = 10 
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')

        if search:
            # Filtrar por nombres o apellidos
            queryset = queryset.filter(
                Q(nombres__icontains=search) | Q(apellidos__icontains=search)
            )
        
        return queryset

class ActualizarCliente(LoginRequiredMixin, UpdateView):
    model = Cliente
    template_name = 'clientes/update.html'
    form_class = RegistrarClienteForm
    
    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('clientes:detalle_cliente', args=[self.object.id])

class EliminarCliente(LoginRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'clientes/eliminar.html'
    success_url = reverse_lazy('clientes:listar_clientes')


def historial_compra_cliente(request, cliente_id): 
    cliente = get_object_or_404(Cliente, id=cliente_id)

    # Traer todas las ventas de ese cliente, ordenadas por fecha descendente
    ventas = Venta.objects.filter(cliente=cliente).prefetch_related('detalles__producto').order_by('-fecha', '-hora')
    total_cliente = ventas.aggregate(total=Sum('total'))['total'] or 0

    return render(request, 'clientes/historial_compras.html', {
        'cliente': cliente,
        'ventas': ventas,
        'total_cliente': total_cliente
    })
