from django import forms
from .models import Cliente
from datetime import date

class RegistrarClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = ['nombres', 'apellidos', 'correo', 'telefono', 'ciudad', 'direccion', 'dni', 'fecha_nacimiento', 'imagen', 'activo']
        widgets = {
            'fecha_nacimiento': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d' 
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['imagen'].required = False
        self.fields['ciudad'].required = False
        self.fields['direccion'].required = False
        self.fields['activo'].initial = True 
        self.fields['fecha_nacimiento'].input_formats = ['%Y-%m-%d']

    def clean_nombres(self):
        nombres = self.cleaned_data.get('nombres', '').strip()
        if not nombres:
            raise forms.ValidationError("El campo nombres es obligatorio.")
        if any(char.isdigit() for char in nombres):
            raise forms.ValidationError("El nombre no debe contener números.")
        return nombres

    def clean_apellidos(self):
        apellidos = self.cleaned_data.get('apellidos', '').strip()
        if not apellidos:
            raise forms.ValidationError("El campo apellidos es obligatorio.")
        if any(char.isdigit() for char in apellidos):
            raise forms.ValidationError("El apellido no debe contener números.")
        return apellidos

    def clean_correo(self):
        correo = self.cleaned_data.get('correo', '').strip()
        if not correo:
            raise forms.ValidationError("El campo correo es obligatorio.")
        return correo

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')
        if not telefono.isdigit():
            raise forms.ValidationError("El teléfono debe contener solo números.")
        if len(telefono) < 7 or len(telefono) > 10:
            raise forms.ValidationError("El teléfono debe tener entre 7 y 10 dígitos.")
        return telefono

    def clean_dni(self):
        dni = self.cleaned_data.get('dni', '')
        if not dni.isdigit():
            raise forms.ValidationError("El DNI debe contener solo números.")
        if len(dni) < 8 or len(dni) > 10:
            raise forms.ValidationError("El DNI debe tener entre 8 y 10 dígitos.")
        return dni


    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento', None)
        if not fecha_nacimiento:
            raise forms.ValidationError("Debe ingresar la fecha de nacimiento.")
        if fecha_nacimiento > date.today():
            raise forms.ValidationError("La fecha de nacimiento no puede ser en el futuro.")
        return fecha_nacimiento
