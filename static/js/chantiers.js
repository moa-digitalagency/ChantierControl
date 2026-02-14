document.addEventListener('DOMContentLoaded', function() {
    initRepartitionChart();
    initTresorerieChart();
});

function initRepartitionChart() {
    const canvas = document.getElementById('repartitionChart');
    if (canvas) {
        const data = JSON.parse(canvas.dataset.values || '[]');
        new Chart(canvas.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Achats', 'Salaires', 'Transport'],
                datasets: [{
                    data: data,
                    backgroundColor: ['#3B82F6', '#10B981', '#8B5CF6']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } }
            }
        });
    }
}

function initTresorerieChart() {
    const canvas = document.getElementById('tresorerieChart');
    if (canvas) {
        const data = JSON.parse(canvas.dataset.values || '[]');
        new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Budget', 'Avances', 'Dépenses'],
                datasets: [{
                    data: data,
                    backgroundColor: ['#6B7280', '#10B981', '#EF4444']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } }
            }
        });
    }
}
