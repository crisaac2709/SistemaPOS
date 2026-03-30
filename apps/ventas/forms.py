from django import forms
from .models import Venta, DetalleVenta
from django.forms.models import inlineformset_factory

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente', 'metodo_pago']

DetalleVentaFormSet = inlineformset_factory(Venta, DetalleVenta, fields = ['producto', 'cantidad', 'precio_unitario'], extra=1, can_delete=True)
