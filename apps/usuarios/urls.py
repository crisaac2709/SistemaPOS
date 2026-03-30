from django.urls import path, reverse_lazy
from .views import (
    Registrar, MyLoginView, MyLogoutView, Configurar_Perfil, 
    Mi_Perfil, redireccion_post_login, EmpleadoHome, 
    panel_actividades_admin
)
from django.contrib.auth import views as auth_views

app_name = "usuarios"

urlpatterns = [
    path('registro/', Registrar, name="registro"),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView, name='logout'),
    path('configurar_perfil/', Configurar_Perfil, name='configurar_perfil'),
    path("mi_perfil", Mi_Perfil, name="perfil"),
    path('redirigir-rol/', redireccion_post_login, name='redirigir_rol'),
    path('empleado_home/', EmpleadoHome, name='empleado_home'),
    path('panel-actividades/', panel_actividades_admin, name='panel_actividades'),

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
