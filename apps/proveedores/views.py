from django.shortcuts import render
from django.views.generic import CreateView, DeleteView, DetailView,  UpdateView, ListView
from .forms import RegistrarProveedor
from .models import Proveedor
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class RegistrarProveedorView(LoginRequiredMixin, CreateView):
    model = Proveedor
    form_class = RegistrarProveedor
    template_name = 'proveedores/crear.html'
    success_url = reverse_lazy('proveedores:listar_proveedores')


class ListarProveedores(LoginRequiredMixin, ListView):
    model = Proveedor
    context_object_name = 'proveedores'
    template_name = 'proveedores/listar.html'
    ordering = ['nombre']
    paginate_by = 10


class ActualizarProveedor(LoginRequiredMixin, UpdateView):
    model = Proveedor
    form_class = RegistrarProveedor
    template_name = 'proveedores/update.html'
    success_url = reverse_lazy('proveedores:listar_proveedores')


class VerDetalleProveedor(LoginRequiredMixin, DetailView):
    model = Proveedor
    template_name = 'proveedores/detalle.html'


class EliminarProveedor(LoginRequiredMixin, DetailView):
    model= Proveedor
    template_name = 'proveedores/eliminar.html'
    success_url = reverse_lazy('proveedores:listar_proveedores')