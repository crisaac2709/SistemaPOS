from django.shortcuts import render
from django.views.generic import CreateView, DeleteView, DetailView,  UpdateView, ListView
from .forms import RegistrarProveedor
from .models import Proveedor
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class RegistrarProveedorView(LoginRequiredMixin, CreateView):
    model = Proveedor
    form_class = RegistrarProveedor
    template_name = 'proveedores/crear.html'

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('proveedores:detalle_proveedor', args=[self.object.id])


class ListarProveedores(LoginRequiredMixin, ListView):
    model = Proveedor
    context_object_name = 'proveedores'
    template_name = 'proveedores/listar.html'
    ordering = ['nombre']
    paginate_by = 10

    def get_queryset(self):
        return Proveedor.objects.filter(empresa=self.request.user.empresa)


class ActualizarProveedor(LoginRequiredMixin, UpdateView):
    model = Proveedor
    form_class = RegistrarProveedor
    template_name = 'proveedores/update.html'
    
    def get_queryset(self):
        return Proveedor.objects.filter(empresa=self.request.user.empresa)
    
    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('proveedores:detalle_proveedor', args=[self.object.id])


class VerDetalleProveedor(LoginRequiredMixin, DetailView):
    model = Proveedor
    template_name = 'proveedores/detalle.html'

    def get_queryset(self):
        return Proveedor.objects.filter(empresa=self.request.user.empresa)


class EliminarProveedor(LoginRequiredMixin, DeleteView):
    model= Proveedor
    template_name = 'proveedores/eliminar.html'
    success_url = reverse_lazy('proveedores:listar_proveedores')

    def get_queryset(self):
        return Proveedor.objects.filter(empresa=self.request.user.empresa)