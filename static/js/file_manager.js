// KALM OS v4.3 - File Manager (CORREGIDO)

let currentPath = '/D';

// ═══ Cargar archivos ═══
function loadFiles(path) {
    const grid = document.getElementById('file-grid');
    const pathInput = document.getElementById('file-path');
    
    if (!grid) return;
    
    if (!path || path === '' || path === 'D:' || path === 'D:/' || path === 'D:\\') {
        path = '/D';
    }
    
    currentPath = path;
    if (pathInput) pathInput.value = path;
    
    grid.innerHTML = '<div style="text-align:center;padding:40px;color:#9370db">⏳ Cargando...</div>';
    
    fetch(`/api/files?path=${encodeURIComponent(path)}`)
        .then(r => r.json())
        .then(data => renderFiles(data))
        .catch(err => {
            grid.innerHTML = `<div style="color:#ff6b6b;padding:20px">❌ Error: ${err.message}</div>`;
        });
}

// ═══ Renderizar archivos ═══
function renderFiles(data) {
    const grid = document.getElementById('file-grid');
    if (!grid) return;
    
    if (!data || data.error) {
        grid.innerHTML = `<div style="color:#ff6b6b;padding:20px">❌ ${data?.error || 'Error desconocido'}</div>`;
        return;
    }
    
    const items = data.items || [];
    
    if (items.length === 0) {
        grid.innerHTML = '<div style="color:#9370db;padding:20px;text-align:center">📂 Carpeta vacía</div>';
        return;
    }
    
    let html = '';
    items.forEach(item => {
        const ext = item.ext || '';
        const isExecutable = ['.py', '.sh', '.js', '.bat', '.cmd', '.exe'].includes(ext);
        const isDoc = ['.pdf', '.txt', '.md', '.log', '.json', '.xml', '.yaml', '.yml', '.csv', 
                      '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico'].includes(ext);
        
        html += `<div class="file-item" ${item.is_dir ? 'ondblclick="openFolder(\'' + item.path + '\')"' : ''}>
            <div class="file-icon">${item.icon || '📄'}</div>
            <div class="file-name">${item.name}</div>
            <div class="file-size">${item.size_fmt || '-'}</div>
            <div class="file-actions">
                ${item.is_dir ? `<button class="act small" onclick="openFolder('${item.path}')">📂 Abrir</button>` : ''}
                ${isExecutable ? `<button class="act small success" onclick="runProgram('${item.path}')">▶️ Ejecutar</button>` : ''}
                ${isDoc ? `<button class="act small" onclick="openDocument('${item.path}')">👁️ Ver</button>` : ''}
                <button class="act small danger" onclick="deleteFile('${item.path}')">🗑️</button>
            </div>
        </div>`;
    });
    
    grid.innerHTML = html;
}

// ═══ Navegación ═══
function openFolder(path) {
    loadFiles(path);
}

function fileUp() {
    if (!currentPath) return;
    if (currentPath === '/D') return;
    
    const parts = currentPath.split('/');
    parts.pop();
    const parent = parts.join('/') || '/D';
    loadFiles(parent);
}

function refreshFiles() {
    if (currentPath) loadFiles(currentPath);
}

// ═══ Ejecutar programa ═══
function runProgram(path) {
    showNotification(`⏳ Ejecutando ${path.split('/').pop()}...`, 'info');
    
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            if (data.viewer_url) {
                // Abrir documento en visor (nueva ventana o pestaña)
                window.open(data.viewer_url, '_blank');
                showNotification(`📄 ${path.split('/').pop()} abierto en visor`, 'success');
            } else if (data.session_id) {
                // Programa ejecutado - abrir terminal
                showNotification(`✅ ${path.split('/').pop()} ejecutado (PID ${data.pid})`, 'success');
                openTerminalForProcess(data.session_id, path.split('/').pop());
                if (typeof loadServers === 'function') loadServers();
            } else {
                showNotification(data.message || `✅ ${path.split('/').pop()} ejecutado`, 'success');
            }
        } else {
            showNotification(`❌ Error: ${data.error || 'desconocido'}`, 'error');
        }
    })
    .catch(err => {
        showNotification(`❌ Error: ${err.message}`, 'error');
    });
}

// ═══ Abrir documento ═══
function openDocument(path) {
    showNotification(`📄 Abriendo ${path.split('/').pop()}...`, 'info');
    
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok && data.viewer_url) {
            window.open(data.viewer_url, '_blank');
            showNotification(`📄 ${path.split('/').pop()} abierto en visor`, 'success');
        } else {
            showNotification(`❌ Error: ${data?.error || 'No se pudo abrir'}`, 'error');
        }
    })
    .catch(err => {
        showNotification(`❌ Error: ${err.message}`, 'error');
    });
}

// ═══ Eliminar ═══
function deleteFile(path) {
    if (!confirm(`¿Eliminar "${path.split('/').pop()}"?`)) return;
    
    fetch('/api/files/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            refreshFiles();
            showNotification('✅ Archivo eliminado', 'success');
        } else {
            showNotification(`❌ Error: ${data.error || 'desconocido'}`, 'error');
        }
    });
}

// ═══ Crear carpeta ═══
function createFolderPrompt() {
    const name = prompt('📁 Nombre de la carpeta:');
    if (!name || name.trim() === '') return;
    
    fetch('/api/files/folder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: currentPath, name: name.trim() })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            refreshFiles();
            showNotification('✅ Carpeta creada', 'success');
        } else {
            showNotification(`❌ Error: ${data.error || 'desconocido'}`, 'error');
        }
    });
}

// ═══ Buscar ═══
function searchFiles() {
    const query = document.getElementById('file-search').value.trim();
    if (!query) {
        refreshFiles();
        return;
    }
    
    const grid = document.getElementById('file-grid');
    grid.innerHTML = '<div style="text-align:center;padding:40px;color:#9370db">⏳ Buscando...</div>';
    
    fetch(`/api/files/search?q=${encodeURIComponent(query)}`)
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                grid.innerHTML = `<div style="color:#ff6b6b;padding:20px">❌ ${data.error}</div>`;
                return;
            }
            
            const results = data.results || [];
            if (results.length === 0) {
                grid.innerHTML = '<div style="color:#9370db;padding:20px;text-align:center">🔍 No se encontraron resultados</div>';
                return;
            }
            
            let html = '';
            results.forEach(item => {
                html += `<div class="file-item" onclick="openDocument('${item.path}')">
                    <div class="file-icon">${item.icon || '📄'}</div>
                    <div class="file-name">${item.name}</div>
                    <div class="file-size">${item.size_fmt || '-'}</div>
                </div>`;
            });
            grid.innerHTML = html;
        })
        .catch(err => {
            grid.innerHTML = `<div style="color:#ff6b6b;padding:20px">❌ Error: ${err.message}</div>`;
        });
}

// ═══ Subir archivos ═══
function uploadFiles(input) {
    const files = input.files;
    if (!files || files.length === 0) return;
    
    const formData = new FormData();
    for (const file of files) {
        formData.append('file', file);
    }
    
    fetch(`/api/files/upload?path=${encodeURIComponent(currentPath)}`, {
        method: 'POST',
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        input.value = '';
        if (data.ok) {
            refreshFiles();
            showNotification('✅ Archivos subidos', 'success');
        } else {
            showNotification('❌ Error subiendo archivos', 'error');
        }
    })
    .catch(() => {
        input.value = '';
        showNotification('❌ Error de conexión', 'error');
    });
}

// ═══ TERMINAL VIRTUAL (CORREGIDA) ═══
function openTerminalForProcess(sessionId, programName) {
    let win = document.getElementById('win-terminal');
    
    if (!win) {
        win = document.createElement('div');
        win.id = 'win-terminal';
        win.className = 'window resizable';
        win.style.cssText = 'top:100px;left:100px;width:750px;height:500px;display:flex;flex-direction:column';
        win.dataset.title = `💻 Terminal: ${programName || 'Proceso'}`;
        
        win.innerHTML = `
            <div class="title-bar" onmousedown="drag(event,'win-terminal')">
                <span>💻 Terminal: ${programName || 'Proceso'}</span>
                <div class="controls">
                    <button class="btn btn-min" onclick="minimizeWin('terminal')">─</button>
                    <button class="btn btn-max" onclick="maximizeWin('terminal')">▢</button>
                    <button class="btn btn-close" onclick="closeTerminalWindow()">✕</button>
                </div>
            </div>
            <div class="window-body" style="padding:0;display:flex;flex-direction:column;height:100%">
                <pre id="term-output" style="flex:1;margin:0;padding:10px;overflow-y:auto;background:#0a0a1a;color:#0f0;font-family:'Consolas',monospace;font-size:13px;white-space:pre-wrap;word-wrap:break-word;min-height:300px">⏳ Conectando al proceso...</pre>
                <div style="padding:8px;background:#0a0a1a;border-top:1px solid #4b0082;display:flex">
                    <span style="color:#0f0;margin-right:8px;font-family:monospace">$</span>
                    <input id="term-input" style="flex:1;background:transparent;color:#0f0;border:none;outline:none;font-family:monospace;font-size:13px" placeholder="Escribe aquí para enviar al proceso...">
                </div>
            </div>
        `;
        document.body.appendChild(win);
    }
    
    win.style.display = 'flex';
    win.classList.add('active');
    win.style.zIndex = ++windowZIndex;
    
    const titleBar = win.querySelector('.title-bar span');
    if (titleBar) titleBar.textContent = `💻 Terminal: ${programName || 'Proceso'}`;
    
    updateTaskbar('terminal');
    startTerminalStream(sessionId);
    
    const input = document.getElementById('term-input');
    if (input) {
        input.onkeydown = function(e) {
            if (e.key === 'Enter') {
                const value = this.value;
                if (value.trim()) {
                    sendTerminalInput(sessionId, value);
                    const output = document.getElementById('term-output');
                    if (output) {
                        output.textContent += `\n${value}`;
                    }
                    this.value = '';
                }
            }
        };
        setTimeout(() => input.focus(), 500);
    }
}

function closeTerminalWindow() {
    const win = document.getElementById('win-terminal');
    if (win) {
        if (window.termEventSource) {
            window.termEventSource.close();
            window.termEventSource = null;
        }
        win.remove();
        const tbItem = document.querySelector(`.tb-window[data-win="terminal"]`);
        if (tbItem) tbItem.remove();
    }
}

function startTerminalStream(sessionId) {
    const output = document.getElementById('term-output');
    if (!output) return;
    
    // Cerrar conexión anterior
    if (window.termEventSource) {
        window.termEventSource.close();
        window.termEventSource = null;
    }
    
    // Usar EventSource con reconexión controlada
    const url = `/api/process/stream/${sessionId}`;
    const eventSource = new EventSource(url);
    window.termEventSource = eventSource;
    
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 2; // Solo 2 intentos, no infinito
    
    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            if (data.type === 'output') {
                output.textContent += data.data;
                output.scrollTop = output.scrollHeight;
            } else if (data.type === 'exit') {
                output.textContent += `\n\n\x1b[33m📋 Proceso terminado (código ${data.code || 0})\x1b[0m\n`;
                eventSource.close();
                window.termEventSource = null;
            } else if (data.type === 'error') {
                output.textContent += `\n\x1b[31m❌ Error: ${data.data}\x1b[0m\n`;
            } else if (data.type === 'connected') {
                output.textContent = output.textContent.replace('⏳ Conectando al proceso...', '✅ Conectado al proceso\n');
            }
        } catch (e) {
            console.error('Error parsing SSE:', e);
        }
    };
    
    eventSource.onerror = function() {
        if (eventSource.readyState === EventSource.CLOSED) {
            output.textContent += '\n\x1b[31m❌ Conexión cerrada\x1b[0m\n';
            window.termEventSource = null;
        } else if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            output.textContent += `\n\x1b[33m⚠️ Reconectando... (${reconnectAttempts}/${maxReconnectAttempts})\x1b[0m\n`;
        } else {
            output.textContent += '\n\x1b[31m❌ Error de conexión persistente\x1b[0m\n';
            eventSource.close();
            window.termEventSource = null;
        }
    };
}

function sendTerminalInput(sessionId, data) {
    fetch('/api/process/input', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, input: data })
    })
    .then(r => r.json())
    .then(response => {
        if (!response.ok) {
            console.error('Error enviando input:', response.error);
        }
    })
    .catch(err => console.error('Error:', err));
}

// ═══ NOTIFICACIONES ═══
function showNotification(message, type = 'info') {
    const colors = {
        info: '#9370db',
        success: '#00cc66',
        error: '#ff4444',
        warning: '#ffaa00'
    };
    
    const div = document.createElement('div');
    div.style.cssText = `
        position: fixed;
        bottom: 60px;
        right: 20px;
        background: rgba(10,5,20,0.95);
        border: 1px solid ${colors[type] || '#9370db'};
        color: #fff;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 10000;
        max-width: 400px;
        font-size: 13px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.5);
        animation: slideIn 0.3s ease;
        font-family: 'Segoe UI', sans-serif;
    `;
    div.textContent = message;
    document.body.appendChild(div);
    
    setTimeout(() => {
        div.style.opacity = '0';
        div.style.transition = 'opacity 0.5s';
        setTimeout(() => div.remove(), 500);
    }, 5000);
}

// ═══ INICIALIZAR ═══
document.addEventListener('DOMContentLoaded', function() {
    const observer = new MutationObserver(() => {
        const win = document.getElementById('win-explorer');
        if (win && win.style.display !== 'none') {
            const grid = document.getElementById('file-grid');
            if (grid && grid.children.length === 0) {
                loadFiles('/D');
            }
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    
    setTimeout(() => {
        const win = document.getElementById('win-explorer');
        if (win && win.style.display !== 'none') {
            loadFiles('/D');
        }
    }, 500);
});

const styleNotif = document.createElement('style');
styleNotif.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(styleNotif);

// ═══ Asegurar que openTerminalForProcess esté disponible globalmente ═══
window.openTerminalForProcess = openTerminalForProcess;
window.closeTerminalWindow = closeTerminalWindow;
window.showNotification = showNotification;

console.log('📁 File Manager cargado - Terminal disponible globalmente');