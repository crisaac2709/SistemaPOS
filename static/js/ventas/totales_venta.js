document.addEventListener('DOMContentLoaded', () => {
    // Inicialización
    actualizarTotales();
    
    // Listeners para cambios en el formulario
    const metodoPagoSelect = document.querySelector('select[name="metodo_pago"]');
    if (metodoPagoSelect) {
        metodoPagoSelect.addEventListener("change", actualizarTotales);
    }

    const pagoClienteInput = document.getElementById("pago-cliente");
    if (pagoClienteInput) {
        pagoClienteInput.addEventListener("input", actualizarTotales);
        controlarPagoEnTiempoReal(pagoClienteInput);
    }

    // Listener global para cambios en productos (cantidad/precio)
    document.addEventListener("input", (event) => {
        if (event.target.id.includes("cantidad") || event.target.id.includes("precio_unitario")) {
            actualizarTotales();
        }
    });
});

function actualizarTotales() {
    const formTotal = document.getElementById("id_detalles-TOTAL_FORMS");
    const subtotalElement = document.getElementById("subtotal");
    const ivaElement = document.getElementById("iva");
    const totalElement = document.getElementById("total");
    const ivaGlobalInput = document.getElementById('iva_global');

    if (!formTotal || !subtotalElement || !totalElement) return;

    const ivaPorcentaje = parseFloat(ivaGlobalInput?.value || 0) / 100;
    let subtotalAcumulado = 0;

    // Recorrer los formularios de productos
    const totalForms = parseInt(formTotal.value);
    for (let i = 0; i < totalForms; i++) {
        const cantidadInput = document.getElementById(`id_detalles-${i}-cantidad`);
        const precioInput = document.getElementById(`id_detalles-${i}-precio_unitario`);
        const subtotalSpan = document.getElementById(`subtotal-detalles-${i}`);

        const cantidad = parseFloat(cantidadInput?.value || 0);
        const precio = parseFloat(precioInput?.value || 0);
        const subtotalFila = cantidad * precio;

        subtotalAcumulado += subtotalFila;

        if (subtotalSpan) {
            subtotalSpan.textContent = `$${subtotalFila.toFixed(2)}`;
        }
    }

    const valorIva = subtotalAcumulado * ivaPorcentaje;
    const valorTotal = subtotalAcumulado + valorIva;

    // Actualizar vista de totales
    subtotalElement.textContent = `$${subtotalAcumulado.toFixed(2)}`;
    ivaElement.textContent = `$${valorIva.toFixed(2)}`;
    totalElement.textContent = `$${valorTotal.toFixed(2)}`;
    
    // Ejecutar la validación del panel de pago
    validarPanelPago(valorTotal);
}

function validarPanelPago(totalVenta) {
    const metodoPagoSelect = document.querySelector('select[name="metodo_pago"]');
    if (!metodoPagoSelect) return;

    // Extraemos el texto de la opción seleccionada para comparar
    const textoSeleccionado = metodoPagoSelect.options[metodoPagoSelect.selectedIndex].text.trim().toLowerCase();
    
    const seccionPago = document.getElementById("seccion-pago-efectivo");
    const pagoClienteInput = document.getElementById("pago-cliente");
    const cambioElement = document.getElementById("cambio");
    const btnGuardar = document.querySelector('button[type="submit"]');

    // Verificamos si es "Contado" o "Efectivo"
    const esContado = textoSeleccionado.includes("contado") || textoSeleccionado.includes("efectivo");

    if (esContado) {
        seccionPago.classList.remove("hidden");
        pagoClienteInput.disabled = false;

        const montoEntregado = parseFloat(pagoClienteInput.value || 0);
        const cambio = montoEntregado - totalVenta;

        if (cambioElement) {
            cambioElement.textContent = cambio >= 0 ? `$${cambio.toFixed(2)}` : `$0.00`;
            // Cambio de color visual si falta dinero
            cambioElement.className = cambio >= 0 
                ? "text-xl font-bold text-green-600 bg-gray-100 border border-gray-300 rounded-lg p-3 text-right shadow-inner"
                : "text-xl font-bold text-red-600 bg-gray-100 border border-gray-300 rounded-lg p-3 text-right shadow-inner";
        }

        // Bloqueo del botón de guardar si el monto es insuficiente
        if (montoEntregado < totalVenta && montoEntregado > 0) {
            btnGuardar.disabled = true;
            btnGuardar.classList.add('opacity-50', 'cursor-not-allowed');
        } else if (montoEntregado >= totalVenta) {
            btnGuardar.disabled = false;
            btnGuardar.classList.remove('opacity-50', 'cursor-not-allowed');
        } else {
            // Si el input está vacío, depende de tu regla de negocio (aquí lo dejo habilitado o deshabilitado)
            btnGuardar.disabled = true; 
        }

    } else {
        // Si es Crédito o PayPal, ocultamos y reseteamos
        seccionPago.classList.add("hidden");
        pagoClienteInput.value = "";
        pagoClienteInput.disabled = true;
        btnGuardar.disabled = false;
        btnGuardar.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

function controlarPagoEnTiempoReal(pagoInput) {
    pagoInput.addEventListener('blur', () => {
        const totalTexto = document.getElementById("total").textContent.replace('$', '').trim();
        const totalNum = parseFloat(totalTexto);
        const montoIngresado = parseFloat(pagoInput.value || 0);

        if (montoIngresado > 0 && montoIngresado < totalNum) {
            // Asumiendo que usas SweetAlert2 por tu código anterior
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    icon: 'warning',
                    title: 'Monto insuficiente',
                    text: `El cliente debe entregar al menos $${totalNum.toFixed(2)}`,
                    confirmButtonColor: '#3B82F6'
                });
            } else {
                alert(`Monto insuficiente. Total: $${totalNum.toFixed(2)}`);
            }
        }
    });
}