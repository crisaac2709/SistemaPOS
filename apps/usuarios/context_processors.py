from .models import Perfil

def perfil_contexto(request):
    if request.user.is_authenticated:
        perfil = Perfil.objects.filter(usuario=request.user).first()
        return {'perfil': perfil}
    return {}
