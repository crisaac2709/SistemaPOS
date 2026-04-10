from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model 
from django.core.exceptions import ValidationError
import re

# Obtenemos tu modelo CustomUser automáticamente
User = get_user_model()

def validar_password_fuerte(password):
    if len(password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Debe contener al menos 1 letra mayúscula.")
    if not re.search(r'[a-z]', password):
        raise ValidationError("Debe contener al menos 1 letra minúscula.")
    if not re.search(r'\d', password):
        raise ValidationError("Debe contener al menos 1 número.")
    if not re.search(r'[@$!%*?&]', password):
        raise ValidationError("Debe contener al menos 1 carácter especial (@$!%*?&).")
    

class RegistroFormularioEmpleados(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, validators=[validar_password_fuerte])
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'cedula', 'telefono', 'rol']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con este email.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ya existe un usuario con ese username.")
        return username
    

class RegistroFormulario(forms.ModelForm):
    # 1. Definir campos manuales PRIMERO
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': '********'}),
        validators=[validar_password_fuerte]
    )
    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': '********'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'cedula', 'telefono']

    # 2. El constructor al FINAL
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        clases_tailwind = (
            "mt-1 block w-full px-4 py-3 border border-slate-300 rounded-lg "
            "shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition-colors"
        )
        
        # Ahora sí, este bucle atrapará 'password' y 'password2' también
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': clases_tailwind})

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con este email.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ya existe un usuario con ese username.")
        return username
    


class MyLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))