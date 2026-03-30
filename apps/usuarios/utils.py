from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

def crear_roles():
    # Crear grupos si no existen
    nombres_grupos = ['Administrador', 'Vendedor']
    for nombre in nombres_grupos:
        Group.objects.get_or_create(name=nombre)

    # Asignar permisos a Administrador
    administrador_group = Group.objects.get(name='Administrador')
    permisos = Permission.objects.all()  # Todos los permisos
    administrador_group.permissions.set(permisos)  # Le das todos

    # Asignar permisos a Vendedor (solo ventas y clientes)
    vendedor_group = Group.objects.get(name='Vendedor')
    modelos = ['venta', 'cliente']
    for modelo in modelos:
        content_type = ContentType.objects.get(model=modelo)
        permisos = Permission.objects.filter(content_type=content_type)
        vendedor_group.permissions.add(*permisos)

    print("Grupos y permisos creados correctamente.")


from apps.ventas.models import Venta
from apps.creditos.models import Pago, Credito

def listar_ventas_empleado(usuario):
    ventas = Venta.objects.filter(usuario = usuario)
    return ventas

def listar_creditos_empleado(usuario):
    creditos = Credito.objects.filter(usuario = usuario)
    return creditos

def listar_cobros_realizados(usuario):
    pagos = Pago.objects.filter(usuario = usuario)
    return pagos
