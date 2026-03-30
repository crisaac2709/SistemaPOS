from django.urls import path
from .views import CrearCreditoView, ListarCreditosView, DetalleCreditoView, RegistrarPagoView, GenerarContrato, calendario, EliminarCreditoView, DashboardCreditosView, obtener_planes_credito, generar_comprobante_pago

app_name = 'creditos'

urlpatterns = [
    path('crear_credito/', CrearCreditoView, name="crear_credito"),
    path('listar/', ListarCreditosView.as_view(), name="listar_creditos"),
    path('detalle/<int:pk>/', DetalleCreditoView.as_view(), name="detalle_credito"),
    path('pago/credito/<int:pk>', RegistrarPagoView, name="registrar_pago"),
    path('eliminar/<int:pk>', EliminarCreditoView.as_view(), name="eliminar_credito"),
    path('credito/<int:pk>/descargar-contrato/', GenerarContrato, name="generar_contrato"),
    path('credito/<int:credito_id>/calendario/', calendario, name='calendario'),
    path('dashboard/', DashboardCreditosView.as_view(), name='dashboard'),
    path('api/planes_credito/<int:producto_id>/', obtener_planes_credito, name='api_planes_credito'),
    path('pagos/comprobante/<int:pk>/', generar_comprobante_pago, name='comprobante_pago'),


]