// KALM OS v4.3 - Persistencia con GitHub

// ═══ GUARDAR NOTAS ═══
function saveNotes() {
    const notes = document.getElementById('persistence-notes');
    const status = document.getElementById('persistence-status');
    if (!notes) return;
    
    if (status) {
        status.textContent = '⏳ Guardando...';
        status.style.color = '#ffaa00';
    }
    
    fetch('/api/persistence/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ 
            name: 'notes', 
            data: { content: notes.value, updated: new Date().toISOString() }
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            if (status) {
                status.textContent = '✅ Guardado en GitHub';
                status.style.color = '#00cc66';
            }
            setTimeout(() => { 
                if (status) {
                    status.textContent = '📝 Listo';
                    status.style.color = '#9370db';
                }
            }, 3000);
        } else {
            if (status) {
                status.textContent = '❌ Error: ' + (data.error || 'desconocido');
                status.style.color = '#ff4444';
            }
        }
    })
    .catch(err => {
        if (status) {
            status.textContent = '❌ Error de conexión';
            status.style.color = '#ff4444';
        }
    });
}

// ═══ CARGAR NOTAS ═══
function loadNotes() {
    const notes = document.getElementById('persistence-notes');
    const status = document.getElementById('persistence-status');
    if (!notes) return;
    
    if (status) {
        status.textContent = '⏳ Cargando...';
        status.style.color = '#ffaa00';
    }
    
    fetch('/api/persistence/load', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name: 'notes' })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok && data.data) {
            notes.value = data.data.content || '';
            if (status) {
                status.textContent = '📂 Cargado desde GitHub';
                status.style.color = '#00cc66';
            }
            setTimeout(() => { 
                if (status) {
                    status.textContent = '📝 Listo';
                    status.style.color = '#9370db';
                }
            }, 2000);
        } else {
            notes.value = '';
            if (status) {
                status.textContent = '📝 Sin notas guardadas';
                status.style.color = '#9370db';
            }
        }
    })
    .catch(err => {
        if (status) {
            status.textContent = '❌ Error cargando';
            status.style.color = '#ff4444';
        }
    });
}

// ═══ CARGAR BACKUPS ═══
function loadBackups() {
    const list = document.getElementById('backup-list');
    if (!list) return;
    
    list.innerHTML = '<span style="color:#ffaa00">⏳ Cargando backups...</span>';
    
    fetch('/api/persistence/backups')
        .then(r => r.json())
        .then(data => {
            if (data.ok && data.backups && data.backups.length > 0) {
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
                list.innerHTML = '<span style="color:#9370db">📋 No hay backups disponibles</span>';
            }
        })
        .catch(err => {
            list.innerHTML = '<span style="color:#ff4444">❌ Error cargando backups</span>';
        });
}

// ═══ CREAR BACKUP ═══
function createBackup() {
    const status = document.getElementById('persistence-status');
    if (status) {
        status.textContent = '⏳ Creando backup...';
        status.style.color = '#ffaa00';
    }
    
    fetch('/api/persistence/backup', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.ok) {
                if (status) {
                    status.textContent = `✅ Backup creado: ${data.backup}`;
                    status.style.color = '#00cc66';
                }
                loadBackups();
                setTimeout(() => { 
                    if (status) {
                        status.textContent = '📝 Listo';
                        status.style.color = '#9370db';
                    }
                }, 3000);
            } else {
                if (status) {
                    status.textContent = '❌ Error creando backup';
                    status.style.color = '#ff4444';
                }
            }
        })
        .catch(err => {
            if (status) {
                status.textContent = '❌ Error de conexión';
                status.style.color = '#ff4444';
            }
        });
}

// ═══ RESTAURAR BACKUP ═══
function restoreBackup(name) {
    if (!confirm(`¿Restaurar backup "${name}"? Se sobrescribirán los datos actuales.`)) return;
    
    const status = document.getElementById('persistence-status');
    if (status) {
        status.textContent = `⏳ Restaurando ${name}...`;
        status.style.color = '#ffaa00';
    }
    
    fetch('/api/persistence/restore', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name: name })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            if (status) {
                status.textContent = '✅ Backup restaurado';
                status.style.color = '#00cc66';
            }
            loadNotes();
            loadBackups();
            setTimeout(() => { 
                if (status) {
                    status.textContent = '📝 Listo';
                    status.style.color = '#9370db';
                }
            }, 3000);
        } else {
            if (status) {
                status.textContent = '❌ Error restaurando backup';
                status.style.color = '#ff4444';
            }
        }
    })
    .catch(err => {
        if (status) {
            status.textContent = '❌ Error de conexión';
            status.style.color = '#ff4444';
        }
    });
}

// ═══ AUTO-GUARDAR ═══
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

// ═══ EXPORTAR FUNCIONES GLOBALMENTE ═══
window.saveNotes = saveNotes;
window.loadNotes = loadNotes;
window.loadBackups = loadBackups;
window.createBackup = createBackup;
window.restoreBackup = restoreBackup;
window.startAutoSave = startAutoSave;
window.stopAutoSave = stopAutoSave;

// ═══ INICIALIZAR ═══
document.addEventListener('DOMContentLoaded', function() {
    const notesArea = document.getElementById('persistence-notes');
    if (notesArea) {
        loadNotes();
        startAutoSave();
        
        notesArea.addEventListener('blur', saveNotes);
        
        notesArea.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                saveNotes();
            }
        });
    }
    
    // Cargar backups cuando se abre la ventana
    const observer = new MutationObserver(() => {
        const win = document.getElementById('win-persistence');
        if (win && win.style.display !== 'none') {
            setTimeout(loadBackups, 300);
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    
    // También cargar backups si la ventana ya está visible al cargar
    setTimeout(() => {
        const win = document.getElementById('win-persistence');
        if (win && win.style.display !== 'none') {
            loadBackups();
        }
    }, 1000);
});

console.log('💾 Persistencia con GitHub cargada');
console.log('📌 Funciones disponibles: saveNotes, loadNotes, createBackup, restoreBackup, loadBackups');