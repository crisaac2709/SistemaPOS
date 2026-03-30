document.addEventListener("DOMContentLoaded", function () {
    const selectInicial = document.querySelector("#id_detalles-0-producto");
    const precioInicial = document.querySelector("#id_detalles-0-precio_unitario");

    if (selectInicial) selectInicial.readOnly = true;
    if (precioInicial) precioInicial.readOnly = true;

    const btnAgregar = document.getElementById("add_product");
    const contenedor = document.getElementById("Contenedor-formularios");
    const formTotal = document.getElementById("id_detalles-TOTAL_FORMS");

    
    btnAgregar.addEventListener("click", () => agregarFormulario());

    function agregarFormulario() {
        const index = parseInt(formTotal.value);
        const row = document.createElement("tr");

        // Crear columnas
        const tdProducto = document.createElement("td");
        const tdCantidad = document.createElement("td");
        const tdPrecio = document.createElement("td");
        const tdSubtotal = document.createElement("td");
        const tdAcciones = document.createElement("td");

        tdProducto.classList.add("px-4", "py-3");
        tdCantidad.classList.add("px-4", "py-3");
        tdPrecio.classList.add("px-4", "py-3");
        tdSubtotal.classList.add("px-4", "py-3", "text-center");
        tdAcciones.classList.add("px-4", "py-3", "text-center");

        // PRODUCTO (clonando con opciones)
        const selectReferencia = document.getElementById("id_detalles-0-producto");
        if (!selectReferencia) {
            console.error("Select de referencia no encontrado.");
            return;
        }

        const select = selectReferencia.cloneNode(true); 
        select.name = `detalles-${index}-producto`;
        select.id = `id_detalles-${index}-producto`;
        select.classList.add("w-full", "p-2", "border-gray-300", "rounded-md");
        select.innerHTML = '<option value="">---------</option>';
        tdProducto.appendChild(select);

        // CANTIDAD
        const cantidad = document.createElement("input");
        cantidad.type = "number";
        cantidad.min = "1";
        cantidad.value = "1";
        cantidad.name = `detalles-${index}-cantidad`;
        cantidad.id = `id_detalles-${index}-cantidad`;
        cantidad.classList.add("w-full", "p-2", "border-gray-300", "rounded-md", "text-center");
        tdCantidad.appendChild(cantidad);

        // PRECIO UNITARIO
        const precio = document.createElement("input");
        precio.type = "number";
        precio.step = "any";
        precio.value = "0.00";
        precio.name = `detalles-${index}-precio_unitario`;
        precio.id = `id_detalles-${index}-precio_unitario`;
        precio.readOnly = true;
        precio.classList.add("w-full", "p-2", "border-gray-300", "rounded-md", "text-center");
        tdPrecio.appendChild(precio);

        // SUBTOTAL
        const subtotal = document.createElement("span");
        subtotal.id = `subtotal-detalles-${index}`;
        subtotal.textContent = "$0.00";
        tdSubtotal.classList.add("text-center");
        tdSubtotal.appendChild(subtotal);

        // BOTÓN ELIMINAR
        const eliminar = document.createElement("button");
        eliminar.type = "button";
        eliminar.innerHTML = `
            <svg class="h-5 w-5 text-red-600 hover:text-red-800" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>`;
        eliminar.addEventListener("click", () => {
            row.remove();
            formTotal.value = parseInt(formTotal.value) - 1;
            actualizarTotales();
        });
        tdAcciones.classList.add("text-center");
        tdAcciones.appendChild(eliminar);

        // Agrega fila
        row.appendChild(tdProducto);
        row.appendChild(tdCantidad);
        row.appendChild(tdPrecio);
        row.appendChild(tdSubtotal);
        row.appendChild(tdAcciones);

        contenedor.appendChild(row);

        // Aumentar TOTAL_FORMS del formset
        formTotal.value = index + 1;

        // Recalcular totales si cambia cantidad
        cantidad.addEventListener("input", () => actualizarTotales());
    }


});


function limpiarFila0() {
    document.getElementById("id_detalles-0-producto").value = "";
    document.getElementById("id_detalles-0-cantidad").value = "1";
    document.getElementById("id_detalles-0-precio_unitario").value = "0.00";
    document.getElementById("subtotal-detalles-0").textContent = "$0.00";
    actualizarTotales();
}