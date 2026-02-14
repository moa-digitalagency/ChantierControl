document.addEventListener('DOMContentLoaded', function() {
    initFinanceIndexChart();
    initFinanceDetailsChart();
    initFinanceDistributionChart();
    initFinanceDateToggle();
    initFinanceSearch();
    initFinanceExport();
    initFinanceTabs();
});

function initFinanceTabs() {
    const tabs = document.querySelectorAll('[data-tab-target]');
    if (tabs.length === 0) return;

    function activateTab(tabName) {
        // Deactivate all tabs
        tabs.forEach(t => {
            const isSelected = t.dataset.tabTarget === tabName;
            t.classList.toggle('bg-white', isSelected);
            t.classList.toggle('border-b-2', isSelected);
            t.classList.toggle('border-primary-500', isSelected);
            t.classList.toggle('text-primary-700', isSelected);

            t.classList.toggle('text-gray-500', !isSelected);
            t.classList.toggle('hover:text-gray-700', !isSelected);
        });

        // Hide all contents
        document.querySelectorAll('[data-tab-content]').forEach(c => {
            if (c.dataset.tabContent === tabName) {
                c.classList.remove('hidden');
            } else {
                c.classList.add('hidden');
            }
        });
    }

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            activateTab(tab.dataset.tabTarget);
        });
    });

    // Default to first tab or specific one
    activateTab('achats');
}

function initFinanceIndexChart() {
    const canvas = document.getElementById('budgetChart');
    if (canvas) {
        const labels = JSON.parse(canvas.dataset.labels || '[]');
        const budgets = JSON.parse(canvas.dataset.budgets || '[]');
        const spent = JSON.parse(canvas.dataset.spent || '[]');

        new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Budget',
                    data: budgets,
                    backgroundColor: '#e5e7eb',
                    hoverBackgroundColor: '#d1d5db',
                    borderRadius: 4,
                    barPercentage: 0.6
                }, {
                    label: 'Dépenses',
                    data: spent,
                    backgroundColor: '#3b82f6',
                    hoverBackgroundColor: '#2563eb',
                    borderRadius: 4,
                    barPercentage: 0.6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) label += ': ';
                                if (context.parsed.y !== null) {
                                    label += new Intl.NumberFormat('fr-MA', { style: 'currency', currency: 'MAD' }).format(context.parsed.y);
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { beginAtZero: true, grid: { color: '#f3f4f6' } }
                }
            }
        });
    }
}

function initFinanceExport() {
    const btn = document.getElementById('export-btn');
    if (btn) {
        btn.addEventListener('click', function() {
            alert('Export global à venir');
        });
    }
}

function initFinanceDetailsChart() {
    const canvas = document.getElementById('expensesChart');
    if (canvas) {
        const categories = JSON.parse(canvas.dataset.categories || '[]');
        const amounts = JSON.parse(canvas.dataset.amounts || '[]');

        // Colors palette
        const colors = [
            '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#6366f1', '#14b8a6', '#f97316'
        ];

        // Ensure arrays have data
        if (!categories.length) return;

        new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: categories,
                datasets: [{
                    label: 'Montant',
                    data: amounts,
                    backgroundColor: colors.slice(0, categories.length),
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) label += ': ';
                                if (context.parsed.y !== null) {
                                    label += new Intl.NumberFormat('fr-MA', { style: 'currency', currency: 'MAD' }).format(context.parsed.y);
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#f3f4f6' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }
}

function initFinanceDateToggle() {
    const filterSelect = document.getElementById('filterSelect');
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            toggleFinanceCustomDates(this.value);
            if (this.value !== 'custom') {
                this.closest('form').submit();
            }
        });
        // Init
        toggleFinanceCustomDates(filterSelect.value);
    }
}

function toggleFinanceCustomDates(value) {
    const customDates = document.getElementById('customDates');
    if (customDates) {
        if (value === 'custom') {
            customDates.classList.remove('hidden');
        } else {
            customDates.classList.add('hidden');
        }
    }
}

function initFinanceDistributionChart() {
    const canvas = document.getElementById('distributionChart');
    if (canvas) {
        const data = JSON.parse(canvas.dataset.values || '[]');

        new Chart(canvas.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Matériel/Achats', 'Main d\'œuvre', 'Avances'],
                datasets: [{
                    data: data,
                    backgroundColor: ['#8b5cf6', '#3b82f6', '#f59e0b'],
                    hoverBackgroundColor: ['#7c3aed', '#2563eb', '#d97706'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' },
                    tooltip: {
                         callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                let value = context.parsed;
                                let total = context.chart._metasets[context.datasetIndex].total;
                                let percentage = ((value / total) * 100).toFixed(1) + '%';
                                return label + ': ' + new Intl.NumberFormat('fr-MA', { style: 'currency', currency: 'MAD' }).format(value) + ' (' + percentage + ')';
                            }
                        }
                    }
                },
                cutout: '75%'
            }
        });
    }
}

function initFinanceSearch() {
    const searchInput = document.getElementById('tableSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            var input, filter, table, tr, td, i, txtValue;
            input = document.getElementById("tableSearch");
            filter = input.value.toUpperCase();
            table = document.querySelector("table");
            if (table) {
                tr = table.getElementsByTagName("tr");
                for (i = 0; i < tr.length; i++) {
                    td = tr[i].getElementsByTagName("td")[0];
                    if (td) {
                        txtValue = td.textContent || td.innerText;
                        if (txtValue.toUpperCase().indexOf(filter) > -1) {
                            tr[i].style.display = "";
                        } else {
                            tr[i].style.display = "none";
                        }
                    }
                }
            }
        });
    }
}
