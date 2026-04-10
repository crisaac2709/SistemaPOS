from django.http import JsonResponse
from .utils import enviar_recordatorios_pago
from django.shortcuts import render
from django.urls import reverse



def confirmacion_envio_recordatorios(request):
    return render(request, 'correos/modal_recordatorio.html')


def enviar_recordatorio_pago(request):
    usuario = request.user
    try:
        enviar_recordatorios_pago(request.user.empresa)

        if usuario.rol.nombre == "Administrador":
            redireccion_url = reverse('home')
        else:
            redireccion_url = reverse('usuarios:empleado_home')
                
        return JsonResponse({
                'success': True, 
                'redirect_url': redireccion_url
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


