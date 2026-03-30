from django.urls import path
from .views import CrearProductoView, ListarProductos, DetalleProducto, ActualizarProducto, EliminarProducto, ingresar_unidades, movimientos_stock, productos_bajo_stock

app_name = 'productos'

urlpatterns = [
    path('crear/', CrearProductoView.as_view(), name="crear_producto" ),
    path('listar/', ListarProductos.as_view(), name="listar_productos" ),
    path('detalle/<int:pk>/', DetalleProducto.as_view(), name="detalle_producto" ),
    path('actualizar/<int:pk>/', ActualizarProducto.as_view(), name="actualizar_producto" ),
    path('eliminar/<int:pk>/', EliminarProducto.as_view(), name="eliminar_producto" ),
    path('stock/movimientos/', movimientos_stock, name='movimientos_stock'),
    path('stock/ingresar-unidades/', ingresar_unidades, name='ingresar_unidades'),
    path('api/bajo-stock/', productos_bajo_stock, name="productos_bajo_stock"),
]

