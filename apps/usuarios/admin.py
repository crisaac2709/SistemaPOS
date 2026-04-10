from django.contrib import admin
from .models import Actividad, Rol
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register your models here.
admin.site.register(Actividad)
admin.site.register(Rol)
admin.site.register(CustomUser, UserAdmin)