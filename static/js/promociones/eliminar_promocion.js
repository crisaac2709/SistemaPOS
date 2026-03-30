document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-eliminar-promocion').forEach(button => {
        button.addEventListener('click', function() {
            const promoId = this.dataset.id;
            const promoNombre = this.dataset.nombre;

            Swal.fire({
                title: `¿Eliminar "${promoNombre}"?`,
                text: "Se revertirá el stock y se eliminará la promoción.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Sí, eliminar'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/promociones/eliminar-promocion/${promoId}/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            Swal.fire('Eliminado', data.message, 'success');
                            document.getElementById(`promo-row-${promoId}`).remove();
                        } else {
                            Swal.fire('Error', data.message, 'error');
                        }
                    })
                    .catch(err => {
                        Swal.fire('Error', 'Error de red o servidor', 'error');
                        console.error(err);
                    });
                }
            });
        });
    });
});