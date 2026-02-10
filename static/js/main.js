function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    if (sidebar) sidebar.classList.toggle('open');
    if (overlay) overlay.classList.toggle('hidden');
}

document.addEventListener('DOMContentLoaded', () => {
    // Close sidebar when clicking a link on mobile
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth < 768) {
                toggleSidebar();
            }
        });
    });

    // Register Service Worker
    if ('serviceWorker' in navigator) {
        const swUrl = window.swUrl || '/static/sw.js';
        navigator.serviceWorker.register(swUrl)
            .then(registration => {
                console.log('ServiceWorker registration successful with scope: ', registration.scope);
            })
            .catch(err => {
                console.log('ServiceWorker registration failed: ', err);
            });
    }
});
