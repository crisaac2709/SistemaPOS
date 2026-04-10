from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps



from apps.ventas.models import Venta
from apps.creditos.models import Pago, Credito

def listar_ventas_empleado(usuario):
    ventas = Venta.objects.filter(usuario = usuario, empresa = usuario.empresa)
    return ventas

def listar_creditos_empleado(usuario):
    creditos = Credito.objects.filter(usuario = usuario, empresa = usuario.empresa)
    return creditos

def listar_cobros_realizados(usuario):
    pagos = Pago.objects.filter(usuario = usuario, empresa = usuario.empresa)
    return pagos
