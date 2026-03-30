from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from .models import Perfil

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
    

class RegistroFormulario(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, validators=[validar_password_fuerte])
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

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
    
    
class FormularioPerfil(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["foto_perfil", "cedula", "telefono", "rol"]
