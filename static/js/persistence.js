// KALM OS v4.3 - Persistencia con GitHub

function saveNotes() {
    const notes = document.getElementById('persistence-notes')?.value || '';
    const status = document.getElementById('persistence-status');
    if (status) status.textContent = '⏳ Guardando...';
    
    fetch('/api/persistence/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ 
            name: 'notes', 
            data: { content: notes, updated: new Date().toISOString() }
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            if (status) status.textContent = '✅ Guardado en GitHub';
            setTimeout(() => { if (status) status.textContent = '📝 Listo'; }, 3000);
        } else {
            if (status) status.textContent = '❌ Error guardando';
        }
    })
    .catch(err => {
        if (status) status.textContent = '❌ Error de conexión';
    });
}

function loadNotes() {
    const notes = document.getElementById('persistence-notes');
    const status = document.getElementById('persistence-status');
    if (!notes) return;
    
    if (status) status.textContent = '⏳ Cargando...';
    
    fetch('/api/persistence/load', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name: 'notes' })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok && data.data) {
            notes.value = data.data.content || '';
            if (status) status.textContent = '📂 Cargado';
            setTimeout(() => { if (status) status.textContent = '📝 Listo'; }, 2000);
        } else {
            notes.value = '';
            if (status) status.textContent = '📝 Sin notas guardadas';
        }
    })
    .catch(err => {
        if (status) status.textContent = '❌ Error cargando';
    });
}

// Auto-guardar cada 30 segundos
let autoSaveInterval = null;

function startAutoSave() {
    if (autoSaveInterval) clearInterval(autoSaveInterval);
    autoSaveInterval = setInterval(saveNotes, 30000);
}

function stopAutoSave() {
    if (autoSaveInterval) {
        clearInterval(autoSaveInterval);
        autoSaveInterval = null;
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    const notesArea = document.getElementById('persistence-notes');
    if (notesArea) {
        loadNotes();
        startAutoSave();
        
        // Guardar al perder el foco
        notesArea.addEventListener('blur', saveNotes);
    }
});

console.log('💾 Persistencia con GitHub cargada');