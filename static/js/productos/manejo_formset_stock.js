(function() {
    const addBtn = document.getElementById('agregar-fila');
    const tbody = document.getElementById('tbody-stock');
    const totalForms = document.getElementById('id_form-TOTAL_FORMS');

    addBtn.addEventListener('click', function() {
        const currentCount = parseInt(totalForms.value);
        const firstRow = document.querySelector('.form-row');
        const newRow = firstRow.cloneNode(true);

        newRow.querySelectorAll('select, input, textarea').forEach(input => {
            if(input.tagName.toLowerCase() === 'select'){
                input.selectedIndex = 0;
            } else {
                input.value = '';
            }

            input.name = input.name.replace(/\d+/, currentCount);
            input.id = input.id.replace(/\d+/, currentCount);
        });

        tbody.appendChild(newRow);
        totalForms.value = currentCount + 1;
    });

    tbody.addEventListener('click', function(e) {
        if(e.target.classList.contains('eliminar-fila')) {
            const rows = tbody.querySelectorAll('.form-row');

            if(rows.length > 1) {
                // Si hay más de una fila, eliminar normalmente
                e.target.closest('tr').remove();
                totalForms.value = rows.length - 1;

                // Reindexar formularios restantes
                const rowsRestantes = tbody.querySelectorAll('.form-row');
                rowsRestantes.forEach((row, index) => {
                    row.querySelectorAll('select, input, textarea').forEach(input => {
                        input.name = input.name.replace(/\d+/, index);
                        input.id = input.id.replace(/\d+/, index);
                    });
                });

            } else {
                // Si es la única fila, solo limpiar los campos
                const firstRow = e.target.closest('tr');
                firstRow.querySelectorAll('select, input, textarea').forEach(input => {
                    if(input.tagName.toLowerCase() === 'select'){
                        input.selectedIndex = 0;
                    } else {
                        input.value = '';
                    }
                });
            }
        }
    });
})();
