document.addEventListener('DOMContentLoaded', function() {
    initPhotoPreview();
    initCostCalculation();
});

function initPhotoPreview() {
    const photoInput = document.getElementById('photoInput');
    if (photoInput) {
        photoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('photoPreview');
                    if (preview) {
                        preview.src = e.target.result;
                        preview.classList.remove('hidden');
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
}

function initCostCalculation() {
    const quantiteInput = document.getElementById('quantite');
    const tarifInput = document.getElementById('tarif');

    if (quantiteInput && tarifInput) {
        const calculerCout = function() {
            const quantite = parseFloat(quantiteInput.value) || 0;
            const tarif = parseFloat(tarifInput.value) || 0;
            const total = quantite * tarif;
            const coutTotal = document.getElementById('coutTotal');
            if (coutTotal) {
                coutTotal.value = total.toFixed(2) + ' MAD';
            }
        };

        quantiteInput.addEventListener('input', calculerCout);
        tarifInput.addEventListener('input', calculerCout);
    }
}
