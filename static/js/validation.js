document.addEventListener('DOMContentLoaded', function() {
    initValidationModals();
    initImagePreview();
    initConfirmForms();
});

function initValidationModals() {
    const modal = document.getElementById('refuseModal');

    // Open Modal Triggers
    const refuseBtns = document.querySelectorAll('[data-action="refuse"]');
    refuseBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const type = this.dataset.type;
            const id = this.dataset.id;
            const form = document.getElementById('refuseForm');
            if (form && modal) {
                form.action = `/validation/${type}/${id}/refuser`;
                modal.classList.remove('hidden');
                const comment = document.getElementById('commentaire');
                if (comment) comment.focus();
            }
        });
    });

    // Close Modal Triggers
    const closeBtns = document.querySelectorAll('[data-action="close-modal"]');
    closeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            if (modal) modal.classList.add('hidden');
        });
    });

    // Click outside
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                 this.classList.add('hidden');
            }
        });
    }
}

function initImagePreview() {
    const images = document.querySelectorAll('[data-preview-url]');
    images.forEach(img => {
        img.addEventListener('click', function() {
            window.open(this.dataset.previewUrl);
        });
    });
}

function initConfirmForms() {
    const forms = document.querySelectorAll('form[data-confirm]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });
}
