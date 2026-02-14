document.addEventListener('DOMContentLoaded', function() {
    initWorkerSearch();
    initImportModal();
    initImagePreview();
    initSalairesSearch();
    initPrintButton();
    initChantierSelect();
    // Custom dates toggle is often triggered by select change
    // We can attach it if the element exists
    const filterSelect = document.getElementById('filterSelect');
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            toggleCustomDates(this.value);
            if (this.value !== 'custom') {
                this.closest('form').submit();
            }
        });
        // Init state
        toggleCustomDates(filterSelect.value);
    }
});

function initWorkerSearch() {
    const searchInput = document.getElementById('workerSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            let filter = this.value.toLowerCase();
            let rows = document.querySelectorAll('tbody tr');
            rows.forEach(row => {
                let nameEl = row.querySelector('.worker-name');
                let posteEl = row.querySelector('.worker-poste');
                if (nameEl && posteEl) {
                    let name = nameEl.textContent.toLowerCase();
                    let poste = posteEl.textContent.toLowerCase();
                    if (name.includes(filter) || poste.includes(filter)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                }
            });
        });
    }
}

function initPrintButton() {
    const btn = document.getElementById('print-btn');
    if (btn) {
        btn.addEventListener('click', function() {
            window.print();
        });
    }
}

function initChantierSelect() {
    const selects = document.querySelectorAll('#chantier_id, #chantier_select');
    selects.forEach(select => {
        select.addEventListener('change', function() {
            this.form.submit();
        });
    });
}

function initImportModal() {
    const modal = document.getElementById('import-modal');
    const modalPanel = document.getElementById('import-modal-panel');
    const openBtn = document.getElementById('open-import-modal');
    const closeBtn = document.getElementById('close-import-modal');

    if (modal && modalPanel) {
        window.openImportModal = function() {
            modal.classList.remove('hidden');
            setTimeout(() => {
                modal.classList.remove('opacity-0');
                modalPanel.classList.remove('scale-95');
                modalPanel.classList.add('scale-100');
            }, 10);
        };

        window.closeImportModal = function() {
            modal.classList.add('opacity-0');
            modalPanel.classList.remove('scale-100');
            modalPanel.classList.add('scale-95');
            setTimeout(() => {
                modal.classList.add('hidden');
            }, 200);
        };

        if (openBtn) openBtn.addEventListener('click', window.openImportModal);
        if (closeBtn) closeBtn.addEventListener('click', window.closeImportModal);
    }
}

function initImagePreview() {
    initFileUpload();
    const input = document.querySelector('input[name="photo_profil"]');
    if (input) {
        input.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    var img = document.getElementById('preview-image');
                    if (img) {
                        img.src = e.target.result;
                        img.classList.remove('hidden');

                        var placeholder = document.getElementById('placeholder-icon');
                        if(placeholder) {
                            placeholder.classList.add('hidden');
                        } else {
                            var div = input.parentElement.querySelector('div.text-center');
                             if(div) div.classList.add('opacity-0');
                        }
                    }
                }
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
}

function initSalairesSearch() {
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

function toggleCustomDates(value) {
    const customDates = document.getElementById('customDates');
    if (customDates) {
        if (value === 'custom') {
            customDates.classList.remove('hidden');
        } else {
            customDates.classList.add('hidden');
        }
    }
}
window.toggleCustomDates = toggleCustomDates;

function initFileUpload() {
    const fileInput = document.getElementById('file-upload');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const display = document.getElementById('file-name-display');
            if (display && this.files && this.files[0]) {
                display.innerText = this.files[0].name;
                display.classList.add('text-gray-900', 'font-medium');
            }
        });
    }
}
