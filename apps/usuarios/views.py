from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistroFormularioEmpleados, RegistroFormulario
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from apps.usuarios.models import Actividad
from django.core.paginator import Paginator
from .utils import listar_ventas_empleado, listar_creditos_empleado, listar_cobros_realizados
from .forms import MyLoginForm
from django.contrib.auth import get_user_model 
from .models import Rol

# Escojemos el user
User = get_user_model()

# Create your views here.
def es_admin(user):
    return user.rol.nombre == "Administrador"

def Registro_Administrador(request):
    if request.user.rol and request.user.empresa:
        return redirect("home")

    if request.method == "POST":
        formUser = RegistroFormulario(request.POST)

        if formUser.is_valid():
            user = formUser.save(commit=False)
            user.set_password(formUser.cleaned_data["password"])

            try:
                rol_admin = Rol.objects.get(nombre="Administrador")
                user.rol = rol_admin
            except Rol.DoesNotExist:
                messages.error(request, "Error interno: El rol Administrador no existe.")
                return redirect('usuarios:login')

            user.save()

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "¡Cuenta creada! Ahora registra tu empresa para empezar.")

            return redirect("empresas:crear_empresa")
    else:
        formUser = RegistroFormulario()

    return render(request, "auth/registro_administrador.html", {'form': formUser})

@login_required
@user_passes_test(es_admin)
def Registrar_Empleados(request):
    if request.method == 'POST':
        form_user = RegistroFormularioEmpleados(request.POST)

        if form_user.is_valid():
            user = form_user.save(commit=False)
            user.set_password(form_user.cleaned_data['password'])

            if request.user.rol.nombre == "Administrador" and request.user.empresa:
                user.empresa = request.user.empresa
                user.save()
                messages.success(request, "Usuario registrado correctamente.")
                
                Actividad.objects.create(
                    usuario = request.user,
                    descripcion = f'Creaste a un nuevo usuario: {user.username}',
                    empresa= request.user.empresa
                )
                return redirect('usuarios:panel_actividades')
            else:
                return redirect("usuarios:login")
        else:
            messages.error(request, "Verifique los campos del formulario.")
    else:
        form_user = RegistroFormularioEmpleados()

    contexto = {
        'form_user': form_user,
    }
    return render(request, 'auth/registro.html', contexto)


class MyLoginView(LoginView):
    template_name = 'auth/login.html'

def iniciar_sesion(request):
    if request.method == "POST":
        user_form = MyLoginForm(request=request, data=request.POST)
        if user_form.is_valid():
            user = user_form.get_user()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            if user.rol:
                if user.rol.nombre == "Administrador":
                    return redirect("usuarios:admin_home")
                elif user.rol.nombre == "Empleado":
                    return redirect("usuarios:empleados_home")
                else:
                    print("Rol no reconocido")
                    messages.error(request, "Rol no reconocido.")
                    return redirect('usuarios:login')
            logout(request)
            return redirect("home")
    else: 
        user_form = MyLoginForm(request=request)
        
    return render(request, "auth/login.html", {"form":user_form})


@login_required
def MyLogoutView(request):
    logout(request)
    return redirect('usuarios:login')


@login_required
def Mi_Perfil(request):
    usuario = request.user
    return render(request, 'auth/mi_perfil.html', {'perfil': usuario})

# Empleado

@login_required
def EmpleadoHome(request):
    ventas = listar_ventas_empleado(request.user)
    creditos = listar_creditos_empleado(request.user)
    cobros = listar_cobros_realizados(request.user)
    actividades = Actividad.objects.filter(usuario=request.user, empresa = request.user.empresa).order_by('-fecha')[:5]

    context = {
        "cantidad_ventas" : ventas.count(),
        "cantidad_creditos" : creditos.count(),
        "cantidad_cobros" : cobros.count(),
        "actividades": actividades,
    }
    return render(request, 'auth/EmpleadoHome.html', context)


#Admin
@login_required
def panel_actividades_admin(request):
    if request.user.rol.nombre != "Administrador":
        return render(request, '403.html') 

    usuarios = User.objects.filter(empresa = request.user.empresa)
    filtro_usuario = request.GET.get('usuario')
    
    actividades = Actividad.objects.filter(empresa = request.user.empresa).order_by('-fecha')
    if filtro_usuario:
        actividades = actividades.filter(usuario__id=filtro_usuario, empresa = request.user.empresa)

    paginator = Paginator(actividades, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'usuarios': usuarios,
        'filtro_usuario': filtro_usuario,
    }
    return render(request, 'actividades/panel_actividades.html', context)



from .services import (
    CantidadClientes,
    CantidadCreditos,
    CantidadProductos,
    Ventas_Mes_Actual,
    obtener_ventas_por_metodo_pago,
    obtener_ingresos_por_dia,
    obtener_top_clientes,
    obtener_estado_creditos,
    obtener_ventas_por_mes,
    obtener_productos_vendidos_por_categoria
)

import json
from django.utils.safestring import mark_safe
from datetime import datetime

@login_required
def Dashboard_Administrador(request):

    if not request.user.empresa:
        return redirect("empresas:crear_empresa")

    if request.user.rol.nombre != "Administrador":
        return redirect("home")
    
    empresa = request.user.empresa
    
    año_actual = datetime.now().year

    datos_json = mark_safe(json.dumps({
        "metodo_pago": obtener_ventas_por_metodo_pago(empresa),
        "ingresos_dia": obtener_ingresos_por_dia(empresa),
        "top_clientes": obtener_top_clientes(empresa),
        "estado_creditos": obtener_estado_creditos(empresa),
        "ventas_mes": obtener_ventas_por_mes(empresa),
        "ventas_categoria": obtener_productos_vendidos_por_categoria(empresa),
    }))

    context = {
        "cantidad_clientes": CantidadClientes(empresa),
        "ventas_mes_actual": Ventas_Mes_Actual(empresa),
        "cantidad_creditos": CantidadCreditos(empresa),
        "cantidad_productos": CantidadProductos(empresa),
        "datos_json": datos_json,
        "año_actual": año_actual,
    }
    

    return render(request, 'auth/HomeAdmin.html', context)



