from django.urls import path
from .views import RegistrarProveedorView, ActualizarProveedor, EliminarProveedor, ListarProveedores, VerDetalleProveedor

app_name = 'proveedores'

urlpatterns = [
    path('registrar/', RegistrarProveedorView.as_view(), name="registrar_proveedor"),
    path('listar/', ListarProveedores.as_view(), name="listar_proveedores"),
    path('actualizar/<int:pk>/', ActualizarProveedor.as_view(), name="actualizar_proveedor"),
    path('detalle/<int:pk>/', VerDetalleProveedor.as_view(), name="detalle_proveedor"),
    path('eliminar/<int:pk>/', EliminarProveedor.as_view(), name="eliminar_proveedor"),
]