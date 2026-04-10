from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import MyHome

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MyHome, name='home'),
    path('clientes/', include('apps.clientes.urls', namespace="clientes") ),
    path('usuarios/', include('apps.usuarios.urls', namespace="usuarios") ),
    path('proveedores/', include('apps.proveedores.urls', namespace="proveedores") ),
    path('productos/', include('apps.productos.urls', namespace="productos") ),
    path('ventas/', include('apps.ventas.urls', namespace="ventas") ),
    path('creditos/', include('apps.creditos.urls', namespace="creditos") ),
    path("correos/", include("apps.correos.urls", namespace="correos") ),
    path("reportes/", include("apps.reportes.urls", namespace="reportes")),
    path("empresas/", include("apps.empresas.urls", namespace="empresas")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)


