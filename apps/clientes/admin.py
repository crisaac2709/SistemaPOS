from django.contrib import admin
from .models import Cliente, Pais, Provincia, Ciudad

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Pais)
admin.site.register(Provincia)
admin.site.register(Ciudad)

