document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const btn = this.querySelector('button[type="submit"]');
            if (btn.disabled) { e.preventDefault(); return; }
            btn.disabled = true;
            btn.classList.add('opacity-75', 'cursor-not-allowed');
            const icon = btn.querySelector('i');
            if (icon) icon.className = 'fas fa-circle-notch fa-spin';
        });
    }
});

// Register Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        const swUrl = window.swUrl || '/static/sw.js';
        navigator.serviceWorker.register(swUrl)
            .then(registration => {
                console.log('ServiceWorker registration successful with scope: ', registration.scope);
            })
            .catch(err => {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}
