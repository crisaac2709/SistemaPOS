const rawData = JSON.parse(document.getElementById('datos-json').textContent);
console.log(rawData);

const metodoPagoData = rawData.metodo_pago;
new Chart(document.getElementById('metodoPagoChart'), {
    type: 'pie',
    data: {
        labels: metodoPagoData.map(d => d.metodo_pago__nombre_metodo),
        datasets: [{
            data: metodoPagoData.map(d => d.total),
            backgroundColor: ['#3b82f6','#10b981','#f59e0b','#ef4444']
        }]
    }
});

const ingresosDiaData = rawData.ingresos_dia;
const diasSemana = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'];
new Chart(document.getElementById('ingresosDiaChart'), {
    type: 'bar',
    data: {
        labels: ingresosDiaData.map(d => diasSemana[d.dia - 1]),
        datasets: [{
            label: 'Ingresos ($)',
            data: ingresosDiaData.map(d => d.total),
            backgroundColor: '#4f46e5'
        }]
    }
});

const topClientesData = rawData.top_clientes;
new Chart(document.getElementById('ventasClienteChart'), {
    type: 'bar',
    data: {
        labels: topClientesData.map(d => d.cliente__nombres + ' ' + d.cliente__apellidos),
        datasets: [{
            label: 'Total Vendido ($)',
            data: topClientesData.map(d => d.total),
            backgroundColor: '#16a34a'
        }]
    }
});

const estadoCreditoData = rawData.estado_creditos;
new Chart(document.getElementById('estadoCreditoChart'), {
    type: 'doughnut',
    data: {
        labels: estadoCreditoData.map(d => d.estado),
        datasets: [{
            data: estadoCreditoData.map(d => d.cantidad),
            backgroundColor: ['#f59e0b','#10b981','#ef4444']
        }]
    }
});

const ventasMesData = rawData.ventas_mes;
new Chart(document.getElementById('ventasMesChart'), {
    type: 'line',
    data: {
        labels: ventasMesData.map(v => v.mes),
        datasets: [{
            label: 'Total Ventas ($)',
            data: ventasMesData.map(v => v.total_ventas),
            fill: true,
            backgroundColor: 'rgba(59, 130, 246, 0.2)',
            borderColor: '#3b82f6',
            tension: 0.4,
            pointBackgroundColor: '#3b82f6',
            pointRadius: 4
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: { beginAtZero: true }
        }
    }
});

const categoriaData = rawData.ventas_categoria;
new Chart(document.getElementById('categoriaProductoChart'), {
    type: 'bar',
    data: {
        labels: categoriaData.map(d => d.categoria),
        datasets: [{
            label: 'Cantidad Vendida',
            data: categoriaData.map(d => d.total_vendido),
            backgroundColor: '#ec4899'
        }]
    },
    options: {
        indexAxis: 'y',
        responsive: true,
        scales: {
            x: { beginAtZero: true }
        }
    }
});
