const DB_NAME = 'chantiers_db';
const STORE_NAME = 'saisies_offline';

// Open DB
function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, 1);
        request.onupgradeneeded = (e) => {
            const db = e.target.result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
            }
        };
        request.onsuccess = (e) => resolve(e.target.result);
        request.onerror = (e) => reject(e);
    });
}

// Save data
async function saveOffline(data) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([STORE_NAME], 'readwrite');
        const store = transaction.objectStore(STORE_NAME);
        const request = store.add(data);
        request.onsuccess = () => resolve();
        request.onerror = (e) => reject(e);
    });
}

// Get all data
async function getOfflineData() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([STORE_NAME], 'readonly');
        const store = transaction.objectStore(STORE_NAME);
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = (e) => reject(e);
    });
}

// Delete item
async function deleteItem(id) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([STORE_NAME], 'readwrite');
        const store = transaction.objectStore(STORE_NAME);
        const request = store.delete(id);
        request.onsuccess = () => resolve();
        request.onerror = (e) => reject(e);
    });
}

const toBase64 = file => new Promise((resolve, reject) => {
    if (!file || !file.type) return resolve(null);
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
});

function dataURLtoFile(dataurl, filename) {
    if (!dataurl) return null;
    var arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while(n--){
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, {type:mime});
}

document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('.offline-form');

    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            if (!navigator.onLine) {
                e.preventDefault();

                const formData = new FormData(form);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    if (value instanceof File && value.name) {
                        data[key] = await toBase64(value);
                        data[key + '_name'] = value.name;
                    } else {
                        data[key] = value;
                    }
                }

                data.action = form.getAttribute('action');
                data.method = form.getAttribute('method') || 'POST';
                data.timestamp = Date.now();

                try {
                    await saveOffline(data);

                    // Show success message manually since we prevent default
                    const flashDiv = document.createElement('div');
                    flashDiv.className = 'fixed top-4 right-4 bg-yellow-100 text-yellow-800 border border-yellow-200 p-4 rounded-lg shadow-lg z-50';
                    flashDiv.innerHTML = '<i class="fas fa-wifi mr-2"></i> Hors ligne: Données sauvegardées localement.';
                    document.body.appendChild(flashDiv);
                    setTimeout(() => flashDiv.remove(), 5000);

                    form.reset();
                    // Clear photo preview if any
                    const preview = document.getElementById('photoPreview');
                    if (preview) preview.classList.add('hidden');

                } catch (err) {
                    console.error(err);
                    alert('Erreur lors de la sauvegarde hors ligne.');
                }
            }
        });
    });

    window.addEventListener('online', syncData);

    // Try to sync on load
    if (navigator.onLine) {
        setTimeout(syncData, 2000); // Wait a bit
    }
});

async function syncData() {
    try {
        const items = await getOfflineData();
        if (items.length === 0) return;

        console.log(`Syncing ${items.length} items...`);

        const flashDiv = document.createElement('div');
        flashDiv.className = 'fixed top-4 right-4 bg-blue-100 text-blue-800 border border-blue-200 p-4 rounded-lg shadow-lg z-50';
        flashDiv.innerHTML = '<i class="fas fa-sync fa-spin mr-2"></i> Synchronisation en cours...';
        document.body.appendChild(flashDiv);

        let syncedCount = 0;

        for (const item of items) {
            const formData = new FormData();

            for (const key in item) {
                if (key === 'id' || key === 'action' || key === 'method' || key === 'timestamp') continue;
                if (key.endsWith('_name')) continue;

                if (item[key] && typeof item[key] === 'string' && item[key].startsWith('data:')) {
                    // It's a file
                    const file = dataURLtoFile(item[key], item[key + '_name']);
                    if (file) formData.append(key, file);
                } else {
                    formData.append(key, item[key]);
                }
            }

            try {
                const response = await fetch(item.action, {
                    method: item.method,
                    body: formData
                });

                if (response.ok || response.redirected) {
                    await deleteItem(item.id);
                    syncedCount++;
                } else {
                    console.error('Sync failed for item', item.id, response.status);
                }
            } catch (err) {
                console.error('Sync error for item', item.id, err);
            }
        }

        flashDiv.remove();

        if (syncedCount > 0) {
            const successDiv = document.createElement('div');
            successDiv.className = 'fixed top-4 right-4 bg-green-100 text-green-800 border border-green-200 p-4 rounded-lg shadow-lg z-50';
            successDiv.innerHTML = `<i class="fas fa-check-circle mr-2"></i> ${syncedCount} éléments synchronisés avec succès.`;
            document.body.appendChild(successDiv);
            setTimeout(() => successDiv.remove(), 5000);

            // Reload page to show new data if we are on dashboard
            if (window.location.pathname.includes('dashboard')) {
                setTimeout(() => window.location.reload(), 2000);
            }
        }

    } catch (err) {
        console.error('Sync error:', err);
    }
}
