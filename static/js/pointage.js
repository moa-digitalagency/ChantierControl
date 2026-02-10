function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const display = document.getElementById('current-time-display');
    if(display) display.textContent = timeString;
}

function setCurrentTime(btn) {
    const input = btn.parentElement.querySelector('input');
    if (input) {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        input.value = `${hours}:${minutes}`;
        // Trigger change event to update calculations
        input.dispatchEvent(new Event('change'));
    }
}

function calculateDuration(startStr, endStr) {
    if (!startStr || !endStr) return 0;

    let start = new Date("2000-01-01T" + startStr);
    let end = new Date("2000-01-01T" + endStr);

    // Handle overnight (if end is before start, assume next day)
    if (end < start) {
        end.setDate(end.getDate() + 1);
    }

    return (end - start) / 1000 / 60 / 60; // Returns hours
}

function updateRow(id) {
    const checkInInput = document.querySelector(`input[name="check_in_${id}"]`);
    const checkOutInput = document.querySelector(`input[name="check_out_${id}"]`);
    const breakStartInput = document.querySelector(`input[name="break_start_${id}"]`);
    const breakEndInput = document.querySelector(`input[name="break_end_${id}"]`);

    if (!checkInInput || !checkOutInput) return { hours: 0, money: 0 };

    const checkIn = checkInInput.value;
    const checkOut = checkOutInput.value;
    const breakStart = breakStartInput ? breakStartInput.value : '';
    const breakEnd = breakEndInput ? breakEndInput.value : '';

    let totalHours = 0;

    if (checkIn && checkOut) {
        let workDuration = calculateDuration(checkIn, checkOut);

        if (breakStart && breakEnd) {
            let breakDuration = calculateDuration(breakStart, breakEnd);
            workDuration -= breakDuration;
        }

        totalHours = Math.max(0, workDuration);
    }

    // Update UI for this row
    const hoursDisplay = document.getElementById(`hours_display_${id}`);
    if (hoursDisplay) hoursDisplay.textContent = totalHours.toFixed(2);

    const rateEl = document.querySelector(`.rate[data-id="${id}"]`);
    const rate = rateEl ? (parseFloat(rateEl.textContent) || 0) : 0;
    const totalMoney = totalHours * rate;

    const totalDisplay = document.getElementById(`total_display_${id}`);
    if (totalDisplay) totalDisplay.textContent = totalMoney.toFixed(2);

    return { hours: totalHours, money: totalMoney };
}

function updateAllTotals() {
    let grandTotalHours = 0;
    let grandTotalMoney = 0;

    // Get all worker IDs from the input fields present
    const inputs = document.querySelectorAll('input[name^="check_in_"]');

    inputs.forEach(input => {
        const id = input.getAttribute('data-id');
        const result = updateRow(id);
        grandTotalHours += result.hours;
        grandTotalMoney += result.money;
    });

    const hoursEl = document.getElementById('grand-total-hours');
    const moneyEl = document.getElementById('grand-total-money');

    if(hoursEl) hoursEl.textContent = grandTotalHours.toFixed(2);
    if(moneyEl) moneyEl.textContent = grandTotalMoney.toFixed(2);
}

function switchMode(mode) {
    const btnDirect = document.getElementById('btn-mode-direct');
    const btnManuel = document.getElementById('btn-mode-manuel');
    const divDirect = document.getElementById('mode-direct');
    const divManuel = document.getElementById('mode-manuel');

    if (!btnDirect || !btnManuel || !divDirect || !divManuel) return;

    if (mode === 'direct') {
        btnDirect.classList.remove('text-gray-500', 'hover:text-gray-900');
        btnDirect.classList.add('bg-primary-50', 'text-primary-700', 'shadow-sm');

        btnManuel.classList.remove('bg-primary-50', 'text-primary-700', 'shadow-sm');
        btnManuel.classList.add('text-gray-500', 'hover:text-gray-900');

        divDirect.classList.remove('hidden');
        divManuel.classList.add('hidden');
    } else {
        btnManuel.classList.remove('text-gray-500', 'hover:text-gray-900');
        btnManuel.classList.add('bg-primary-50', 'text-primary-700', 'shadow-sm');

        btnDirect.classList.remove('bg-primary-50', 'text-primary-700', 'shadow-sm');
        btnDirect.classList.add('text-gray-500', 'hover:text-gray-900');

        divManuel.classList.remove('hidden');
        divDirect.classList.add('hidden');
    }
    localStorage.setItem('pointage_mode', mode);
}

function submitAction(ouvrierId, action) {
    const chantierId = new URLSearchParams(window.location.search).get('chantier_id');

    fetch(`/main_oeuvre/pointage/action/${ouvrierId}/${action}?chantier_id=${chantierId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update UI
            const timeArrivee = document.getElementById(`time-arrivee-${ouvrierId}`);
            if(data.check_in && timeArrivee) timeArrivee.textContent = data.check_in;

            const timeDepart = document.getElementById(`time-depart-${ouvrierId}`);
            if(data.check_out && timeDepart) timeDepart.textContent = data.check_out;

            const timePause = document.getElementById(`time-pause-${ouvrierId}`);
            if(data.break_start && timePause) timePause.textContent = data.break_start;

            const timeReprise = document.getElementById(`time-reprise-${ouvrierId}`);
            if(data.break_end && timeReprise) timeReprise.textContent = data.break_end;

            const directHours = document.getElementById(`direct-hours-${ouvrierId}`);
            if(data.heures && directHours) directHours.textContent = data.heures + " h";

            // Visual feedback
            const strip = document.getElementById(`status-strip-${ouvrierId}`);
            if (strip) {
                if (action === 'arrivee') strip.classList.replace('bg-gray-200', 'bg-green-500') || strip.classList.add('bg-green-500');
                if (action === 'depart') strip.className = 'absolute left-0 top-0 bottom-0 w-1 bg-gray-400 transition-colors';
            }

            // Toast or notification could be added here
            const card = timeArrivee ? timeArrivee.closest('.bg-white') : null;
            if (card) {
                card.classList.add('ring-2', 'ring-green-400');
                setTimeout(() => card.classList.remove('ring-2', 'ring-green-400'), 500);
            }

        } else {
            alert('Erreur: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Une erreur est survenue.');
    });
}

// Attach event listeners
document.addEventListener('DOMContentLoaded', function() {
    setInterval(updateClock, 1000);
    updateClock();

    const inputs = document.querySelectorAll('.time-input');
    inputs.forEach(input => {
        input.addEventListener('change', function() {
            const id = this.getAttribute('data-id');
            updateRow(id); // Update specific row immediately
            updateAllTotals(); // Update grand totals
        });
        // Also update on keyup for typing
        input.addEventListener('keyup', function() {
             if(this.value.length === 5) { // Full time string HH:MM
                 const id = this.getAttribute('data-id');
                 updateRow(id);
                 updateAllTotals();
             }
        });
    });

    // Initial calculation
    updateAllTotals();

    // Load saved mode
    const savedMode = localStorage.getItem('pointage_mode') || 'manuel';
    switchMode(savedMode);
});
