from django.shortcuts import render, redirect
from .forms import RegistroFormulario, FormularioPerfil
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Perfil
from apps.usuarios.models import Actividad
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .utils import listar_ventas_empleado, listar_creditos_empleado, listar_cobros_realizados

# Create your views here.
def es_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(es_admin)
def Registrar(request):
    if request.method == 'POST':
        form_user = RegistroFormulario(request.POST)
        form_perfil = FormularioPerfil(request.POST, request.FILES)

        if form_user.is_valid() and form_perfil.is_valid():
            user = form_user.save(commit=False)
            user.set_password(form_user.cleaned_data['password'])
            user.save()

            perfil = form_perfil.save(commit=False)
            perfil.usuario = user
            perfil.save()

            messages.success(request, "Usuario registrado correctamente.")
            Actividad.objects.create(
                usuario = request.user,
                descripcion = f'Creaste a un nuevo usuario: {user.username}'
            )
            return redirect('usuarios:panel_actividades')
        else:
            messages.error(request, "Verifique los campos del formulario.")
    else:
        form_user = RegistroFormulario()
        form_perfil = FormularioPerfil()

    contexto = {
        'form_user': form_user,
        'form_perfil': form_perfil,
    }
    return render(request, 'auth/registro.html', contexto)


class MyLoginView(LoginView):
    template_name = 'auth/login.html'


@login_required
def MyLogoutView(request):
    logout(request)
    return redirect('usuarios:login')


@login_required
def Configurar_Perfil(request):
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == "POST":
        form = FormularioPerfil(request.POST, request.FILES, instance=perfil)
        form.fields.pop('rol', None)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Perfil actualizado correctamente!")
            return redirect("usuarios:perfil")
        else:
            messages.error(request, "Formulario inválido")
    else:
        form = FormularioPerfil(instance=perfil)
        form.fields.pop('rol', None)

    return render(request, "auth/personalizar_perfil.html", {"form": form})



@login_required
def Mi_Perfil(request):
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
    if es_admin(request.user):
        perfil.rol = "ADMIN"
        perfil.save()
    return render(request, 'auth/mi_perfil.html', {'perfil': perfil})

    

@login_required
def redireccion_post_login(request):

    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)

    print(f'El perfil es: {perfil}')
    if es_admin(request.user):
        perfil.rol = 'ADMIN'
        perfil.save()


    if request.user.perfil.rol == 'ADMIN':
        return redirect('home') 
    elif request.user.perfil.rol == 'EMPLEADO':
        return redirect('usuarios:empleado_home')
    else:
        messages.error(request, "Rol no reconocido.")
        return redirect('usuarios:login')
    

# Empleado

@login_required
def EmpleadoHome(request):
    ventas = listar_ventas_empleado(request.user)
    creditos = listar_creditos_empleado(request.user)
    cobros = listar_cobros_realizados(request.user)
    actividades = Actividad.objects.filter(usuario=request.user).order_by('-fecha')[:5]

    context = {
        "cantidad_ventas" : len(ventas),
        "cantidad_creditos" : len(creditos),
        "cantidad_cobros" : len(cobros),
        "actividades": actividades,
    }
    return render(request, 'auth/EmpleadoHome.html', context)


#Admin
@login_required
def panel_actividades_admin(request):
    if not hasattr(request.user, 'perfil') or request.user.perfil.rol != 'ADMIN':
        return render(request, '403.html') 

    usuarios = User.objects.all()
    filtro_usuario = request.GET.get('usuario')
    
    actividades = Actividad.objects.all().order_by('-fecha')
    if filtro_usuario:
        actividades = actividades.filter(usuario__id=filtro_usuario)

    paginator = Paginator(actividades, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'usuarios': usuarios,
        'filtro_usuario': filtro_usuario,
    }
    return render(request, 'actividades/panel_actividades.html', context)