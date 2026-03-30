from django import forms    
from .models import Proveedor

class RegistrarProveedor(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'correo', 'direccion', 'telefono', 'ruc', 'ciudad', 'imagen']