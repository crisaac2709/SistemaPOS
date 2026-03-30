from django import forms
from .models import Credito, Pago
from django.core.exceptions import ValidationError
from decimal import Decimal

class RegistrarCreditoForm(forms.ModelForm):
    class Meta:
        model = Credito
        fields = ['cliente', 'montoInicial', 'montoTotal', 'fecha_inicio', 'fecha_fin', 'tipo_pago']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'cliente': forms.Select(attrs={'class': 'select2-enable w-full mt-1'})
        }

    def clean(self):
        cleaned_data = super().clean()

        monto_inicial = cleaned_data.get('montoInicial')
        monto_total = cleaned_data.get('montoTotal')
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if monto_inicial is not None and monto_total is not None:
            if monto_inicial > monto_total:
                raise ValidationError("🚫 El valor de entrada no puede ser mayor al monto total de la deuda.")

            if monto_inicial > monto_total * Decimal('0.25'):
                raise ValidationError("🚫 El valor de entrada no puede superar el 25% del monto total de la deuda.")

        if fecha_inicio and fecha_fin:
            if fecha_fin <= fecha_inicio:
                raise ValidationError("⚠️ La fecha de finalización debe ser posterior a la fecha de inicio.")

        return cleaned_data
        

class RegistrarPagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['monto', 'cuota', 'metodo_pago', 'comentarios']

        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'cuota': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        monto = cleaned_data.get('monto')
        metodo_pago = cleaned_data.get('metodo_pago')

        if monto is not None:
            if monto <= 0:
                raise ValidationError("🚫 El monto del pago debe ser mayor a cero.")

        if not metodo_pago:
            raise ValidationError("⚠️ Seleccione un método de pago válido.")

        return cleaned_data
        