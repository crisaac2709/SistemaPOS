document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(form);

        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest' // ✅ IMPORTANTE
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                Swal.fire({
                    icon: 'success',
                    title: data.message,
                    timer: 3000,
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timerProgressBar: true
                }).then(() => {
                    window.location.href = data.redirect_url;
                });
            } else {
                let errorText = data.message;

                if (data.errors) {
                    errorText = '';

                    if (data.errors.form) {
                        for (const [campo, mensajes] of Object.entries(data.errors.form)) {
                            errorText += `${campo}: ${mensajes.join(', ')}\n`;
                        }
                    }

                    if (data.errors.formset) {
                        for (const [index, subform] of Object.entries(data.errors.formset)) {
                            for (const [campo, mensajes] of Object.entries(subform)) {
                                errorText += `Producto ${parseInt(index) + 1} -> ${campo}: ${mensajes.join(', ')}\n`;
                            }
                        }
                    }
                }

                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: errorText || 'Error desconocido.'
                });
            }
        })
        .catch(error => {
            Swal.fire({
                icon: 'error',
                title: 'Error de red',
                text: 'Ocurrió un problema al enviar la solicitud.'
            });
            console.error(error);
        });
    });
});
