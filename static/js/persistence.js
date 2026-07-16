// Persistencia de datos

function loadBackups() {
    fetch('/api/persistence/backups')
        .then(r => r.json())
        .then(data => {
            const list = document.getElementById('backup-list');
            if (data.backups && data.backups.length > 0) {
                let html = '<div style="display:flex;flex-direction:column;gap:5px">';
                data.backups.forEach(b => {
                    html += `<div style="display:flex;justify-content:space-between;align-items:center;padding:5px 10px;background:rgba(75,0,130,0.2);border-radius:3px">
                        <span style="color:#d8bfd8">📦 ${b}</span>
                        <button class="act small" onclick="restoreBackup('${b}')">🔄 Restaurar</button>
                    </div>`;
                });
                html += '</div>';
                list.innerHTML = html;
            } else {
                list.innerHTML = '<p style="color:#9370db">No hay backups disponibles</p>';
            }
        });
}

function createBackup() {
    fetch('/api/persistence/backup', {method: 'POST'})
        .then(r => r.json())
        .then(data => {
            if (data.ok) {
                alert(`✅ Backup creado: ${data.backup}`);
                loadBackups();
            } else {
                alert('❌ Error creando backup');
            }
        });
}

function restoreBackup(name) {
    if (!confirm(`¿Restaurar backup "${name}"? Se sobrescribirán los datos actuales.`)) return;
    
    fetch('/api/persistence/restore', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name: name})
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            alert('✅ Backup restaurado correctamente');
            location.reload();
        } else {
            alert('❌ Error restaurando backup');
        }
    });
}

function saveNotes() {
    const notes = document.getElementById('persistence-notes').value;
    fetch('/api/persistence/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name: 'notes', data: notes})
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            alert('✅ Notas guardadas');
        }
    });
}

function loadNotes() {
    fetch('/api/persistence/load', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name: 'notes'})
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok && data.data) {
            document.getElementById('persistence-notes').value = data.data;
        }
    });
}

// Cargar notas al abrir la ventana
document.addEventListener('DOMContentLoaded', function() {
    // Esperar a que la ventana de persistencia esté lista
    const checkWin = setInterval(() => {
        if (document.getElementById('persistence-notes')) {
            loadNotes();
            clearInterval(checkWin);
        }
    }, 100);
});