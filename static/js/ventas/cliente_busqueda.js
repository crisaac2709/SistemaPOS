document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('busqueda_cliente');
    const lista = document.getElementById('resultados_cliente');
    const inputHidden = document.getElementById('cliente_id');
    const cedula = document.getElementById('cliente_cedula');
    const correo = document.getElementById('cliente_correo');
    const telefono = document.getElementById('cliente_telefono');
    const urlBusquedaClientes = document.getElementById("url-buscar-clientes").value

    input.addEventListener('input', async () => {
        
        const query = input.value.trim();
        if (query.length >= 2) {
            const response = await fetch(`${urlBusquedaClientes}?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            lista.innerHTML = '';
            lista.classList.remove('hidden');
            data.forEach(cliente => {
    const li = document.createElement('li');

    li.innerHTML = `
        <div class="p-3 hover:bg-indigo-50 transition rounded-lg">
            <div class="font-semibold text-gray-800">
                ${cliente.nombre_completo}
            </div>
            <div class="text-sm text-gray-500 flex justify-between">
                <span>🪪 ${cliente.dni}</span>
                <span>📞 ${cliente.telefono || 'N/A'}</span>
            </div>
            <div class="text-xs text-gray-400">
                ✉️ ${cliente.correo || 'Sin correo'}
            </div>
        </div>
    `;

    li.classList.add("cursor-pointer");

    li.addEventListener('click', () => {
        input.value = cliente.nombre_completo;
        inputHidden.value = cliente.id;
        cedula.value = cliente.dni;
        correo.value = cliente.correo;
        telefono.value = cliente.telefono;
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
