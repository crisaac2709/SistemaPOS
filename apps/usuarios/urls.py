from django.urls import path, reverse_lazy
from .views import (
    Registrar_Empleados, Registro_Administrador, MyLoginView, MyLogoutView, 
    Mi_Perfil, EmpleadoHome, 
    panel_actividades_admin, iniciar_sesion, 
    Dashboard_Administrador
)
from django.contrib.auth import views as auth_views

app_name = "usuarios"

urlpatterns = [
    path('registro_usuarios/', Registrar_Empleados, name="registro_usuarios"),
    path('registro_administrador/', Registro_Administrador, name="registro_administrador"),
    #path('login/', MyLoginView.as_view(), name='login'),
    path('login/', iniciar_sesion, name='login'),
    path('logout/', MyLogoutView, name='logout'),
    path("mi_perfil", Mi_Perfil, name="perfil"),
    path('empleado_home/', EmpleadoHome, name='empleado_home'),
    path('panel-actividades/', panel_actividades_admin, name='panel_actividades'),
    path("dashboard_admin/", Dashboard_Administrador, name="admin_home"),

    # Recuperación de contraseña
    path(
        'reset_password/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            html_email_template_name='registration/password_reset_email.html', 
            success_url=reverse_lazy('usuarios:password_reset_done')
        ),
        name='reset_password'
    ),
    path(
        'reset_password_sent/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url=reverse_lazy('usuarios:password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset_password_complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
