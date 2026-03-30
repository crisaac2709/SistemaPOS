document.addEventListener('DOMContentLoaded', function() {
    fetch('/productos/api/bajo-stock/')
    .then(response => response.json())
    .then(data => {
        if (data.productos.length > 0) {
            let lista = '<ul style="text-align:left;">';
            data.productos.forEach(prod => {
                lista += `<li><b>${prod.nombre}</b>: ${prod.stock} unidades</li>`;
            });
            lista += '</ul>';

            Swal.fire({
                title: 'Aviso de Stock Bajo 🚨',
                html: lista,
                icon: 'warning',
                confirmButtonText: 'Entendido'
            });
        }
    });
});