document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('busqueda_cliente');
    const lista = document.getElementById('resultados_cliente');
    const inputHidden = document.getElementById('cliente_id');
    const infoDiv = document.getElementById('info_cliente');
    const cedula = document.getElementById('cliente_cedula');
    const correo = document.getElementById('cliente_correo');
    const telefono = document.getElementById('cliente_telefono');

    input.addEventListener('input', async () => {
        const query = input.value.trim();
        if (query.length >= 2) {
            const response = await fetch(`/ventas/buscar-clientes/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            lista.innerHTML = '';
            lista.classList.remove('hidden');
            data.forEach(cliente => {
                const li = document.createElement('li');
                li.textContent = `${cliente.nombre_completo} - ${cliente.dni}`;
                li.classList.add("cursor-pointer", "px-4", "py-2", "hover:bg-indigo-100");
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
