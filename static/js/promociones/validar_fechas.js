document.addEventListener('DOMContentLoaded', function() {
    const fechaInicioInput = document.querySelector('[name="fecha_inicio"]');
    const fechaFinInput = document.querySelector('[name="fecha_fin"]');

    function obtenerFechaActual() {
        const hoy = new Date();
        hoy.setHours(0, 0, 0, 0); // Poner hora en 00:00:00 para comparar solo fechas
        return hoy;
    }

    function esFechaCompleta(valor) {
        // Valida formato completo: YYYY-MM-DDTHH:MM
        const regex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/;
        return regex.test(valor);
    }

    function validarFechas() {
        if (!esFechaCompleta(fechaInicioInput.value) || !esFechaCompleta(fechaFinInput.value)) {
            // No hacer nada si las fechas no están completas
            return;
        }

        const hoy = obtenerFechaActual();

        // Convertimos la fecha de inicio y fin a objeto Date, luego eliminamos horas
        const fechaInicio = new Date(fechaInicioInput.value);
        const fechaFin = new Date(fechaFinInput.value);

        // Poner horas en 00:00:00 para comparar solo fechas
        fechaInicio.setHours(0, 0, 0, 0);
        fechaFin.setHours(0, 0, 0, 0);

        if (fechaInicio < hoy) {
            Swal.fire({
                icon: 'warning',
                title: 'Fecha inválida',
                text: 'La fecha de inicio no puede ser menor al día actual.'
            });
            fechaInicioInput.value = "";
            return;
        }

        if (fechaFin < fechaInicio) {
            Swal.fire({
                icon: 'warning',
                title: 'Fecha inválida',
                text: 'La fecha de fin debe ser mayor o igual a la fecha de inicio.'
            });
            fechaFinInput.value = "";
            return;
        }
    }

    // Eventos al cambiar las fechas
    fechaInicioInput.addEventListener('blur', validarFechas);
    fechaFinInput.addEventListener('blur', validarFechas);
    fechaInicioInput.addEventListener('change', validarFechas);
    fechaFinInput.addEventListener('change', validarFechas);
});
