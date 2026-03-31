document.addEventListener("DOMContentLoaded", function () {

    const urlBuscar = document.getElementById("url-buscar-productos").value;
    const contenedor = document.getElementById("Contenedor-formularios");
    const formTotal = document.getElementById("id_detalles-TOTAL_FORMS");

    new TomSelect("#buscar-producto", {
        valueField: "id",
        labelField: "nombre",
        searchField: "nombre",

        load: function(query, callback) {
            if (!query.length) return callback();

            fetch(`${urlBuscar}?q=${query}`)
                .then(res => res.json())
                .then(data => callback(data))
                .catch(() => callback());
        },

        render: {
            option: function(item, escape) {
                return `
                    <div class="p-2">
                        <div class="font-semibold text-gray-800">
                            ${escape(item.nombre)}
                        </div>
                        <div class="text-sm text-gray-500 flex justify-between">
                            <span>$${item.precio}</span>
                            <span>Stock: ${item.stock_actual}</span>
                        </div>
                    </div>
                `;
            },

            item: function(item, escape) {
                return `
                    <div>
                        ${escape(item.nombre)} - $${item.precio}
                    </div>
                `;
            }
        },

        onChange: function(value) {
            if (!value) return;

            const producto = this.options[value];
            agregarProducto(producto);
            this.clear();
        }
    });

    // ==============================
    // AGREGAR PRODUCTO
    // ==============================
    function agregarProducto(producto) {
        const index = parseInt(formTotal.value);

        // evitar duplicados
        if (productoYaExiste(producto.id)) {
            Swal.fire({
                icon: 'warning',
                title: 'Producto duplicado',
                text: 'Este producto ya está en la lista',
                timer: 2000,
                showConfirmButton: false
            });
            return;
        }

        const row = document.createElement("tr");

        row.innerHTML = `
            <td class="px-4 py-3">
                <input type="hidden" name="detalles-${index}-producto" value="${producto.id}">
                <input type="text" value="${producto.nombre}" 
                    class="w-full p-2 border-gray-300 rounded-md bg-gray-100" readonly>
            </td>

            <td class="px-4 py-3">
                <input type="number" name="detalles-${index}-cantidad" 
                    id="id_detalles-${index}-cantidad"
                    value="1" min="1"
                    data-stock="${producto.stock_actual}"
                    class="w-full p-2 border-gray-300 rounded-md text-center">
            </td>

            <td class="px-4 py-3">
                <input type="number" name="detalles-${index}-precio_unitario" 
                    id="id_detalles-${index}-precio_unitario"
                    value="${producto.precio}" step="any"
                    class="w-full p-2 border-gray-300 rounded-md text-center" readonly>
            </td>

            <td class="px-4 py-3 text-center">
                <span id="subtotal-detalles-${index}">$0.00</span>
            </td>

            <td class="px-4 py-3 text-center">
                <button type="button" class="eliminar-fila text-red-600 hover:text-red-900">
                    ❌
                </button>
            </td>
        `;

        contenedor.appendChild(row);
        formTotal.value = index + 1;

        const cantidad = row.querySelector(`#id_detalles-${index}-cantidad`);
        const precio = row.querySelector(`#id_detalles-${index}-precio_unitario`);
        const subtotal = row.querySelector(`#subtotal-detalles-${index}`);

        const total = parseFloat(precio.value) * parseFloat(cantidad.value);
        subtotal.textContent = `$${total.toFixed(2)}`;

        cantidad.addEventListener("input", () => {
            validarStockInput(cantidad, producto.nombre);
            actualizarTotales();
        });

        actualizarTotales();
    }

    // ==============================
    // ELIMINAR
    // ==============================
    document.addEventListener('click', function(e) {
        if (e.target.closest('.eliminar-fila')) {
            e.target.closest('tr').remove();
            reindexarForms();
            actualizarTotales();
        }
    });

    // ==============================
    // REINDEXAR
    // ==============================
    function reindexarForms() {
        const rows = document.querySelectorAll("#Contenedor-formularios tr");

        rows.forEach((row, index) => {
            row.querySelectorAll("input").forEach(input => {
                if (input.name) input.name = input.name.replace(/detalles-\d+-/, `detalles-${index}-`);
                if (input.id) input.id = input.id.replace(/detalles-\d+-/, `detalles-${index}-`);
            });

            const subtotal = row.querySelector("span");
            if (subtotal) subtotal.id = `subtotal-detalles-${index}`;
        });

        formTotal.value = rows.length;
    }

    // ==============================
    // DUPLICADOS
    // ==============================
    function productoYaExiste(id) {
        const inputs = document.querySelectorAll('input[name$="-producto"]');
        return Array.from(inputs).some(input => input.value == id);
    }

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