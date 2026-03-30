document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const urlMovimientos = document.getElementById('url-movimientos-stock').value;

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(form);

        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                Swal.fire({
                    icon: 'success',
                    title: data.message,
                    timer: 2500,
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timerProgressBar: true
                }).then(() => {
                        window.location.href = urlMovimientos;
                });
            } else {
                let errorText = '';

                if (data.errors) {
                    if (Array.isArray(data.errors)) {
                        errorText = data.errors.join('\n');
                    } else {
                        for (const [campo, errores] of Object.entries(data.errors)) {
                            errorText += `${campo}: ${errores.join(', ')}\n`;
                        }
                    }
                }

                Swal.fire({
                    icon: 'error',
                    title: data.message,
                    text: errorText
                });
            }
        })
        .catch(err => {
            Swal.fire('Error', 'Ocurrió un error al procesar la solicitud.', 'error');
            console.error(err);
        });
    });
});