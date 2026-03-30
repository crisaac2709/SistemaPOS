document.addEventListener('DOMContentLoaded', function () {
    const labels = distribucionTipoPago.map(item => item.tipo_pago);
    const data = distribucionTipoPago.map(item => item.total);

    const ctx = document.getElementById('tipoPagoChart').getContext('2d');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['#3B82F6', '#10B981'],
                hoverBackgroundColor: ['#2563EB', '#059669'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.label}: ${context.raw} créditos`;
                        }
                    }
                }
            },
            cutout: '70%'
        }
    });
});
