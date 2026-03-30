from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.ReportesIndexView, name='index'),
    path('ventas/', views.ReporteVentasView, name='ventas'),
    path('creditos/', views.ReporteCreditosView, name='creditos'),
    path('inventario/', views.ReporteInventarioView, name='inventario'),
]
