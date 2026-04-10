from django.urls import path
from .views import configurar_empresa, detalle_empresa, editar_empresa

app_name = 'empresas'

urlpatterns = [
    path('configurar/', configurar_empresa, name="configurar_empresa"),
    path('detalle/', detalle_empresa, name="detalle_empresa"),
    path('editar/', editar_empresa, name="editar_empresa"),
]
