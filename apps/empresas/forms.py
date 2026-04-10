from django import forms
from .models import Empresa

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = [
            'razon_social', 'nombre_comercial', 'ruc', 'direccion', 
            'telefono', 'correo', 'password_correo', 'logo',
            'archivo_p12', 'password_p12_encriptada', 'ambiente_sri',
            'cod_establecimiento', 'cod_punto_emision'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Tailwind classes
        clase_input = "mt-1 block w-full px-4 py-2.5 border border-slate-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
        clase_select = "mt-1 block w-full px-4 py-2.5 border border-slate-300 rounded-lg bg-white shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
        clase_file = "mt-1 block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': clase_select})
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': clase_file})
            else:
                field.widget.attrs.update({'class': clase_input})

        # Configuración de campos de contraseña
        password_fields = ['password_correo', 'password_p12_encriptada']
        
        for field_name in password_fields:
            self.fields[field_name].widget = forms.PasswordInput(render_value=False)
            self.fields[field_name].required = False  # Importante para que no obligue a escribirla siempre
            self.fields[field_name].widget.attrs.update({
                'placeholder': 'Dejar vacío para mantener la actual',
                'class': clase_input
            })

    def clean_ruc(self):
        ruc = self.cleaned_data.get('ruc')
        if ruc and (len(ruc) != 13 or not ruc.isdigit()):
            raise forms.ValidationError("El RUC debe tener 13 dígitos numéricos.")
        return ruc

    def clean_archivo_p12(self):
        archivo = self.cleaned_data.get('archivo_p12')
        if archivo and not archivo.name.endswith('.p12'):
            raise forms.ValidationError("El archivo debe tener extensión .p12")
        return archivo