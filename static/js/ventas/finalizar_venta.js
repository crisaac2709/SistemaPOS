document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.querySelector('form'); // Capturamos el formulario de venta

    if (formulario) {
        formulario.addEventListener("submit", async (e) => {
            e.preventDefault(); // 1. Evitamos que la página se recargue

            // 2. Opcional: Validaciones extra antes de enviar
            // (Aquí podrías verificar si el stock es correcto o si el pago alcanza)

            // 3. Obtenemos la URL del action del form o la actual
            const url = formulario.action || window.location.href;
            
            // 4. Creamos los datos para enviar (FormData maneja archivos e inputs)
            const formData = new FormData(formulario);

            try {
                // 5. Enviamos los datos por POST (Django espera POST para guardar)
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest', // Indica que es una petición AJAX
                    }
                });

                const data = await response.json();
                
                // 6. Llamamos a nuestra lógica de éxito/error
                gestionarRespuesta(data);

            } catch (error) {
                console.error("Error en la petición:", error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error de Red',
                    text: 'No se pudo conectar con el servidor.',
                });
            }
        });
    }
});

const gestionarRespuesta = (data) => {
    if (data.status === "ok") {
        Swal.fire({
            icon: 'success',
            title: '¡Venta Guardada!',
            text: data.message || 'La venta se registró correctamente.',
            timer: 2000,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timerProgressBar: true
        }).then(() => {
            // Redireccionamos después de que el mensaje se muestre
            window.location.href = data.redireccion;
        });
    } else {
        Swal.fire({
            icon: 'warning',
            title: 'Venta No Efectuada',
            text: data.message || 'Ocurrió un error al guardar la venta.',
            confirmButtonColor: '#3B82F6'
        });
    }
}