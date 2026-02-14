function getMetaContent(name) {
    const meta = document.querySelector(`meta[name="${name}"]`);
    return meta ? meta.content : null;
}

function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');

    function toggleSidebar() {
        if (sidebar) sidebar.classList.toggle('open');
        if (overlay) overlay.classList.toggle('hidden');
    }

    document.querySelectorAll('[data-action="toggle-sidebar"]').forEach(btn => {
        btn.addEventListener('click', toggleSidebar);
    });

    // Close sidebar when clicking a link on mobile
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth < 768) {
                toggleSidebar();
            }
        });
    });
}

function initAutoSubmit() {
    document.querySelectorAll('[data-action="auto-submit"]').forEach(el => {
        el.addEventListener('change', function() {
            this.form.submit();
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initAutoSubmit();

    // Register Service Worker
    if ('serviceWorker' in navigator) {
        const swUrl = getMetaContent('sw-url') || window.swUrl || '/static/sw.js';
        navigator.serviceWorker.register(swUrl)
            .then(registration => {
                console.log('ServiceWorker registration successful with scope: ', registration.scope);
            })
            .catch(err => {
                console.log('ServiceWorker registration failed: ', err);
            });
    }

    initDynamicWidths();
    initConfirmButtons();
});

function initDynamicWidths() {
    const elements = document.querySelectorAll('[data-width]');
    elements.forEach(el => {
        el.style.width = el.dataset.width;
    });
}

function initConfirmButtons() {
    document.querySelectorAll('[data-confirm]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });
}
