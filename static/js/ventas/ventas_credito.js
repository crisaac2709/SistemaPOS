// 🚀 GLOBAL: para que la puedas usar desde producto_busqueda.js
function actualizarPreciosCredito() {
    const selectPlazo = document.getElementById('plazo_credito');
    const plazoSeleccionado = selectPlazo ? selectPlazo.value : 0;

    document.querySelectorAll('[id^="id_detalles-"][id$="-producto"]').forEach((selectProducto, index) => {
        const producto_id = selectProducto.value;

        if (producto_id) {
            fetch(`/creditos/api/planes_credito/${producto_id}/`)
                .then(response => response.json())
                .then(data => {
                    const plan = data.find(p => p.plazo == plazoSeleccionado);

                    if (plan) {
                        document.getElementById(`id_detalles-${index}-precio_unitario`).value = plan.precio;
                        actualizarTotales();
                    }
                });
        }
    });
}

function restaurarPreciosContado() {
    document.querySelectorAll('[id^="id_detalles-"][id$="-producto"]').forEach((selectProducto, index) => {
        const producto_id = selectProducto.value;

        if (producto_id) {
            fetch(`/ventas/buscar-productos/?q=${encodeURIComponent('')}&id=${producto_id}`)
                .then(response => response.json())
                .then(data => {
                    if (data.length > 0) {
                        const producto = data[0];
                        document.getElementById(`id_detalles-${index}-precio_unitario`).value = producto.precio;
                        actualizarTotales();
                    }
                });
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const metodoPago = document.getElementById('id_metodo_pago');
    const camposCredito = document.getElementById('credito-campos');
    const selectPlazo = document.getElementById('plazo_credito');

    metodoPago.addEventListener('change', () => {
        const metodoSeleccionado = metodoPago.options[metodoPago.selectedIndex].text;
        if (metodoSeleccionado.trim() === 'Credito') {
            camposCredito.classList.remove('hidden');
            actualizarPreciosCredito();
        } else {
            camposCredito.classList.add('hidden');
            restaurarPreciosContado();
        }
    });

    if (selectPlazo) {
        selectPlazo.addEventListener('change', function() {
            const metodoSeleccionado = metodoPago.options[metodoPago.selectedIndex].text;
            if (metodoSeleccionado.trim() === 'Credito') {
                actualizarPreciosCredito();
            }
        });
    }
});


document.addEventListener('DOMContentLoaded', () => {

    const fechaInicio = document.getElementById('fecha_inicio');
    const fechaFin = document.getElementById('fecha_fin');
    const montoInicial = document.getElementById('montoInicial');
    const totalVenta = document.getElementById('total');

    function validarFechasCredito() {
        if (!fechaInicio.value || !fechaFin.value) {
            return; 
        }

        const inicio = new Date(fechaInicio.value + "T00:00:00");
        const fin = new Date(fechaFin.value + "T00:00:00");

        if (isNaN(inicio.getTime()) || isNaN(fin.getTime())) {
            console.error('Fechas inválidas (formato incorrecto)');
            return; 
        }

        if (fin <= inicio) {
            Swal.fire({
                icon: 'error',
                title: 'Fechas inválidas',
                text: 'La fecha de finalización debe ser posterior a la fecha de inicio.'
            });

            fechaFin.value = "";
            fechaFin.focus();
        }
    }

    function validarMontoInicial() {
        if (!montoInicial.value || !totalVenta.textContent) {
            return;
        }

        // Limpiar el símbolo $ y comas
        const total = parseFloat(totalVenta.textContent.replace('$', '').replace(',', '').trim()) || 0;
        const entrada = parseFloat(montoInicial.value) || 0;

        if (entrada > total) {
            Swal.fire({
                icon: 'error',
                title: 'Monto de entrada inválido',
                text: 'El valor de entrada no puede ser mayor al total de la venta.'
            });

            montoInicial.value = "";
            montoInicial.focus();
        }
    }

    fechaInicio.addEventListener('change', validarFechasCredito);
    fechaFin.addEventListener('change', validarFechasCredito);
    montoInicial.addEventListener('change', validarMontoInicial);
});
