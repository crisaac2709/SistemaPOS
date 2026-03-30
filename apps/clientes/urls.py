from django.urls import path
from .views import CrearCliente, ActualizarCliente, ListarClientes, EliminarCliente, VerDetalleCliente, historial_compra_cliente

app_name = "clientes"

urlpatterns = [
    path('crear_cliente/', CrearCliente.as_view(), name="crear_cliente"),
    path('actualizar_cliente/<int:pk>/', ActualizarCliente.as_view(), name="actualizar_cliente"),
    path('listar_clientes/', ListarClientes.as_view(), name="listar_clientes"),
    path('detalle_cliente/<int:pk>/', VerDetalleCliente.as_view(), name="detalle_cliente"),
    path('eliminar_cliente/<int:pk>/', EliminarCliente.as_view(), name="eliminar_cliente"),
    path('cliente/<int:cliente_id>/historial', historial_compra_cliente, name="historial_compra_cliente"),
]