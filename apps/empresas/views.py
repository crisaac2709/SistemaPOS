from django.shortcuts import render, redirect
from .forms import EmpresaForm
from .utils import encriptar_clave
from django.contrib.auth.decorators import login_required

# Create your views here.
def configurar_empresa(request):
    if request.user.empresa is not None:
        return redirect("usuarios:admin_home")

    if request.method == 'POST':
        # Nota: Si manejas archivos (logo o .p12), DEBES pasar request.FILES
        formEmpresa = EmpresaForm(request.POST, request.FILES)

        if formEmpresa.is_valid():
            # Creamos la instancia sin guardar en la DB todavía
            empresa = formEmpresa.save(commit=False)

            # 2. El FIX: Sacamos la data del FORMULARIO, no del modelo
            clave_p12_sri = formEmpresa.cleaned_data.get("password_p12_encriptada", "")
            clave_correo = formEmpresa.cleaned_data.get("password_correo", "")

            # Encriptamos y asignamos al modelo
            empresa.password_p12_encriptada = encriptar_clave(clave_p12_sri)
            empresa.password_correo = encriptar_clave(clave_correo)

            # Ahora sí guardamos en la base de datos
            empresa.save()

            # 3. Asignamos la empresa al usuario y guardamos el usuario
            request.user.empresa = empresa
            request.user.save() # ¡No olvides guardar el usuario!

            return redirect("empresas:detalle_empresa")
    else:
        formEmpresa = EmpresaForm()
    
    return render(request, 'empresas/crear_empresa.html', {'form': formEmpresa})

@login_required
def detalle_empresa(request):
    user = request.user
    if user.empresa and user.rol.nombre == "Administrador":
        empresa = user.empresa
        return render(request, "empresas/detalle_empresa.html", context= {"empresa":empresa,"user":user})
    return redirect("home")


@login_required
def editar_empresa(request):
    empresa = request.user.empresa

    if not empresa:
        return redirect("empresas:configurar_empresa")

    if request.method == "POST":
        form = EmpresaForm(request.POST, request.FILES, instance=empresa)

        if form.is_valid():
            empresa = form.save(commit=False)

            # 🔐 Manejo de contraseñas SOLO si se cambian
            clave_p12 = form.cleaned_data.get("password_p12_encriptada")
            clave_correo = form.cleaned_data.get("password_correo")
   
            if clave_p12:
                empresa.password_p12_encriptada = encriptar_clave(clave_p12)

            if clave_correo:
                empresa.password_correo = encriptar_clave(clave_correo)

            empresa.save()

            return redirect("empresas:detalle_empresa")

    else:
        form = EmpresaForm(instance=empresa)

    return render(request, "empresas/crear_empresa.html", {
        "form": form
    })