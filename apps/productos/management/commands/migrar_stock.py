from django.core.management.base import BaseCommand
from django.db import transaction
from apps.productos.models import Producto, Stock
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Migra el stock existente de productos a la tabla Stock"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.WARNING("No se encontró usuario admin. El campo usuario será None."))
        
        productos = Producto.objects.all()
        for producto in productos:
            Stock.objects.create(
                producto=producto,
                cantidad=producto.stock,
                tipo='entrada',
                motivo='Migración inicial',
                usuario=admin_user
            )
        self.stdout.write(self.style.SUCCESS('Stock migrado correctamente.'))
