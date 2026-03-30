document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('busqueda_producto');
    const lista = document.getElementById('resultados_producto');
    const formTotal = document.getElementById("id_detalles-TOTAL_FORMS");

    input.addEventListener('input', async () => {
        const query = input.value.trim();
        if (query.length >= 2) {
            const response = await fetch(`/ventas/buscar-productos/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            lista.innerHTML = '';
            lista.classList.remove('hidden');

            data.forEach(producto => {
                const li = document.createElement('li');
                li.textContent = `${producto.nombre} - $${producto.precio} - Stock: ${producto.stock_actual} unidades`;
                li.classList.add("cursor-pointer", "px-4", "py-2", "hover:bg-indigo-100");

                li.addEventListener('click', () => {
                    const formIndex = parseInt(formTotal.value) - 1;

                    const select = document.getElementById(`id_detalles-${formIndex}-producto`);
                    const precio = document.getElementById(`id_detalles-${formIndex}-precio_unitario`);
                    const cantidad = document.getElementById(`id_detalles-${formIndex}-cantidad`);
                    const subtotal = document.getElementById(`subtotal-detalles-${formIndex}`)

                    // Asegura que exista <select> y agrega la opción visible
                    if (select) {
                        select.innerHTML = ''; // limpia opciones anteriores
                        const option = document.createElement('option');
                        option.value = producto.id;
                        option.textContent = producto.nombre;
                        select.appendChild(option);
                        select.value = producto.id;
                    }

                    const metodoPago = document.getElementById('id_metodo_pago');
                    const metodoSeleccionado = metodoPago.options[metodoPago.selectedIndex].text;
                    console.log(metodoSeleccionado)
                    if (metodoPago && metodoSeleccionado.trim() === 'Credito') {
                        actualizarPreciosCredito(); 
                    }

                    if (precio) precio.value = producto.precio;
                    if (cantidad) {
                        cantidad.value = 1
                        cantidad.setAttribute('data-stock', producto.stock_actual);
                        validarStockInput(cantidad, producto.nombre);
                    };
                    if (subtotal) {
                        const total = parseFloat(precio.value || 0) * parseFloat(cantidad.value || 0);
                        subtotal.textContent = `$${total.toFixed(2)}`;
                    }
                    console.log(subtotal);

                    actualizarTotales();

                    input.value = '';
                    lista.classList.add('hidden');
                });

                lista.appendChild(li);
            });
        } else {
            lista.innerHTML = '';
            lista.classList.add('hidden');
        }
    });
});



// Función para validar
function validarStockInput(inputCantidad, nombreProducto) {
    const stockDisponible = parseInt(inputCantidad.getAttribute('data-stock') || 0);
    const cantidadIngresada = parseInt(inputCantidad.value || 0);

    if (cantidadIngresada > stockDisponible) {
        Swal.fire({
            icon: 'warning',
            title: 'Stock insuficiente',
            text: `Solo quedan ${stockDisponible} unidades de ${nombreProducto}.`,
            confirmButtonColor: '#3B82F6'
        });
        // Reseteamos al máximo disponible
        inputCantidad.value = stockDisponible;
        actualizarTotales(); // Llamamos a tu función para que el subtotal se arregle
    }
}

// Escuchar cambios en CUALQUIER input de cantidad (incluso los nuevos)
document.addEventListener('input', (e) => {
    if (e.target.id.includes('cantidad')) {
        // Obtenemos el nombre del producto de esa fila para el mensaje
        const index = e.target.id.split('-')[1];
        const selectProducto = document.getElementById(`id_detalles-${index}-producto`);
        const nombreProd = selectProducto.options[selectProducto.selectedIndex]?.textContent || "este producto";
        
        validarStockInput(e.target, nombreProd);
    }
});