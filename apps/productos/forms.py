from django import forms
from .models import Producto, Stock

class CrearProducto(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'marca', 'categoria', 'activo', 'proveedor', 'costo', 'imagen', 'precio', 'activo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['imagen'].required = False
        self.fields['descripcion'].required = False
        self.fields['categoria'].required = False
        self.fields['proveedor'].required = False
        self.fields['marca'].required = False
        self.fields.get('activo').initial = True 

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("El nombre del producto es obligatorio.")
        return nombre

    def clean_costo(self):
        costo = self.cleaned_data.get('costo', 0)
        if costo <= 0:
            raise forms.ValidationError("El costo debe ser mayor a 0.")
        return costo

    def clean_precio(self):
        precio = self.cleaned_data.get('precio', 0)
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0.")
        return precio



class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['producto', 'cantidad', 'motivo']
        widgets = {
            'motivo': forms.TextInput(attrs={'placeholder': 'Motivo (opcional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limitar queryset del campo producto a activos que no sean promociones
        self.fields['producto'].queryset = Producto.objects.filter(activo=True).exclude(categoria__nombre__iexact='Promociones')

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad', 0)
        if cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a 0.")
        return cantidad
