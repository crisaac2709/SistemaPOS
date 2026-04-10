from django import forms
from .models import Cliente, Provincia, Ciudad, Pais
from datetime import date

class RegistrarClienteForm(forms.ModelForm):
    pais = forms.ModelChoiceField(
        queryset=Pais.objects.all(), 
        required=False, 
        label="País"
    )
    provincia = forms.ModelChoiceField(
        queryset=Provincia.objects.none(), 
        required=False, 
        label="Provincia"
    )
    class Meta:
        model = Cliente
        fields = ['nombres', 'apellidos', 'correo', 'telefono', 'pais', 'provincia', 'ciudad', 'direccion', 'dni', 'fecha_nacimiento', 'activo']
        widgets = {
            'fecha_nacimiento': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d' 
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ciudad'].required = False
        self.fields['direccion'].required = False
        self.fields['activo'].initial = True 
        self.fields['fecha_nacimiento'].input_formats = ['%Y-%m-%d']

        # Si estamos editando o hay datos en POST
        if 'pais' in self.data:
            try:
                pais_id = int(self.data.get('pais'))
                self.fields['provincia'].queryset = Provincia.objects.filter(pais_id=pais_id)
            except (ValueError, TypeError):
                self.fields['provincia'].queryset = Provincia.objects.none()
        
        if 'provincia' in self.data:
            try:
                prov_id = int(self.data.get('provincia'))
                self.fields['ciudad'].queryset = Ciudad.objects.filter(provincia_id=prov_id)
            except (ValueError, TypeError):
                self.fields['ciudad'].queryset = Ciudad.objects.none()

        elif self.instance.pk and self.instance.ciudad:
            self.fields['provincia'].queryset = Provincia.objects.filter(pais=self.instance.ciudad.provincia.pais)
            self.fields['ciudad'].queryset = Ciudad.objects.filter(provincia=self.instance.ciudad.provincia)
            # Pre-seleccionar los valores en los campos manuales
            self.initial['pais'] = self.instance.ciudad.provincia.pais.id
            self.initial['provincia'] = self.instance.ciudad.provincia.id


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
