from django.urls import path
from .views import (
    crear_venta,
    ListarVentas, 
    DetalleVentaView, 
    EliminarVentaView,
    generar_factura_pdf, 
    analisis_productos, 
    buscar_clientes, 
    buscar_productos,
)

app_name = 'ventas'

urlpatterns = [
    path('crear/', crear_venta, name='crear_venta'),
    path('listar/', ListarVentas.as_view(), name="listar_ventas"),
    path('venta/<int:pk>/', DetalleVentaView.as_view(), name="detalle_venta"),
    path('venta/<int:pk>/eliminar', EliminarVentaView.as_view(), name="eliminar_venta"), 
    path('venta/<int:pk>/generar_factura_pdf/', generar_factura_pdf, name="generar_factura_pdf" ),
    path('analisis_productos/', analisis_productos, name="analisis_productos"),
    path('buscar-clientes/', buscar_clientes, name='buscar_clientes'),
    path('buscar-productos/', buscar_productos, name='buscar_productos'),
]