// KALM OS v4.3 - File Manager Moderno (Estilo Total Commander)
// Solo el usuario root puede eliminar archivos

let currentPath = '/D';
let fileManagerInitialized = false;
let currentUser = null;
let selectedItems = new Set();
let viewMode = 'details'; // 'details' | 'icons'

// ═══ OBTENER USUARIO ACTUAL ═══
function getCurrentUser() {
    return new Promise((resolve) => {
        if (currentUser) {
            resolve(currentUser);
            return;
        }
        
        const cookies = document.cookie.split(';');
        for (const c of cookies) {
            const trimmed = c.trim();
            if (trimmed.startsWith('session_id=')) {
                fetch('/api/whoami')
                    .then(r => r.json())
                    .then(data => {
                        currentUser = data.username || 'user';
                        resolve(currentUser);
                    })
                    .catch(() => {
                        currentUser = 'user';
                        resolve(currentUser);
                    });
                return;
            }
        }
        
        currentUser = 'user';
        resolve(currentUser);
    });
}

function isRoot() {
    return currentUser === 'root';
}

// ═══ CONSTANTES ═══
const TEXT_EXTENSIONS = ['.txt', '.md', '.log', '.json', '.xml', '.yaml', '.yml', '.csv', '.py', '.js', '.html', '.css', '.sql', '.sh', '.bat', '.cmd'];
const MUSIC_EXTENSIONS = ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.wma'];
const IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico', '.tiff', '.tif'];
const PDF_EXTENSIONS = ['.pdf'];
const VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'];
const ARCHIVE_EXTENSIONS = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'];

// ═══ ICONOS MODERNOS ═══
function getFileIcon(ext, isDir) {
    if (isDir) return '📁';
    
    const iconMap = {
        '.txt': '📄', '.md': '📝', '.log': '📋', '.pdf': '📕',
        '.doc': '📘', '.docx': '📘', '.xls': '📊', '.xlsx': '📊',
        '.ppt': '📙', '.pptx': '📙',
        '.py': '🐍', '.js': '📦', '.html': '🌐', '.css': '🎨',
        '.json': '📋', '.xml': '📋', '.yaml': '📋', '.yml': '📋',
        '.sql': '🗄️', '.sh': '🐚', '.bat': '📜', '.cmd': '📜',
        '.java': '☕', '.cpp': '⚙️', '.c': '⚙️', '.go': '🐹',
        '.rs': '🦀', '.rb': '💎', '.php': '🐘',
        '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️',
        '.bmp': '🖼️', '.webp': '🖼️', '.svg': '🖼️', '.ico': '🖼️',
        '.mp3': '🎵', '.wav': '🎵', '.ogg': '🎵', '.flac': '🎵',
        '.m4a': '🎵', '.aac': '🎵', '.wma': '🎵',
        '.mp4': '🎬', '.avi': '🎬', '.mkv': '🎬', '.mov': '🎬',
        '.wmv': '🎬', '.flv': '🎬', '.webm': '🎬',
        '.zip': '📦', '.rar': '📦', '.7z': '📦', '.tar': '📦',
        '.gz': '📦', '.bz2': '📦', '.xz': '📦',
        '.exe': '⚙️', '.msi': '📦', '.app': '📱', '.deb': '📦',
        '.rpm': '📦', '.dmg': '💿',
        '.iso': '💿', '.img': '💿',
    };
    
    return iconMap[ext] || '📄';
}

function formatSize(bytes) {
    if (bytes === 0) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + units[i];
}

// ═══ NAVEGACIÓN ═══
function loadFiles(path) {
    const grid = document.getElementById('file-grid');
    const pathInput = document.getElementById('file-path');
    
    if (!grid) return;
    
    if (!path || path === '' || path === 'D:' || path === 'D:/' || path === 'D:\\') {
        path = '/D';
    }
    
    if (path.startsWith('D:/') || path.startsWith('D:\\')) {
        path = path.replace(/^D:[/\\]/, '/D/');
    }
    
    currentPath = path;
    if (pathInput) pathInput.value = path;
    
    grid.innerHTML = `
        <div style="display:flex;justify-content:center;align-items:center;height:200px;color:#9370db;">
            <div style="text-align:center;">
                <div style="font-size:32px;margin-bottom:10px;">⏳</div>
                <div style="font-size:13px;">Cargando...</div>
            </div>
        </div>
    `;
    
    const url = `/api/files?path=${encodeURIComponent(path)}`;
    
    fetch(url)
        .then(r => {
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return r.json();
        })
        .then(data => {
            getCurrentUser().then(() => {
                renderFiles(data);
            });
        })
        .catch(err => {
            console.error('❌ Error:', err);
            grid.innerHTML = `
                <div style="display:flex;justify-content:center;align-items:center;height:200px;flex-direction:column;color:#ff6b6b;">
                    <div style="font-size:32px;margin-bottom:10px;">❌</div>
                    <div style="font-size:13px;">${err.message}</div>
                    <button class="act small" onclick="refreshFiles()" style="margin-top:15px;">🔄 Reintentar</button>
                </div>
            `;
        });
}

// ═══ RENDERIZAR (ESTILO TOTAL COMMANDER) ═══
function renderFiles(data) {
    const grid = document.getElementById('file-grid');
    if (!grid) return;
    
    if (!data || data.error) {
        grid.innerHTML = `
            <div style="display:flex;justify-content:center;align-items:center;height:200px;color:#ff6b6b;">
                <div style="text-align:center;">
                    <div style="font-size:32px;margin-bottom:10px;">⚠️</div>
                    <div style="font-size:13px;">${data?.error || 'Error desconocido'}</div>
                </div>
            </div>
        `;
        return;
    }
    
    const items = data.items || [];
    
    if (items.length === 0) {
        grid.innerHTML = `
            <div style="display:flex;justify-content:center;align-items:center;height:200px;flex-direction:column;color:#9370db;">
                <div style="font-size:48px;margin-bottom:15px;">📂</div>
                <div style="font-size:14px;">Carpeta vacía</div>
                <div style="font-size:12px;color:#6a0dad;margin-top:5px;">Haz clic en "📁 Nuevo" para crear una carpeta</div>
            </div>
        `;
        return;
    }
    
    const folders = items.filter(i => i.is_dir);
    const files = items.filter(i => !i.is_dir);
    const sortedItems = [...folders, ...files];
    
    let html = `
        <div style="display:grid;grid-template-columns:45px 1fr 100px 130px auto;gap:4px;padding:4px 8px;background:rgba(75,0,130,0.2);border-bottom:1px solid rgba(106,13,173,0.3);font-size:11px;color:#9370db;font-weight:600;position:sticky;top:0;z-index:5;">
            <div style="text-align:center;">📁</div>
            <div>Nombre</div>
            <div style="text-align:right;">Tamaño</div>
            <div style="text-align:right;">Modificado</div>
            <div style="text-align:center;">Acciones</div>
        </div>
    `;
    
    sortedItems.forEach((item, index) => {
        const ext = item.ext || '';
        const isDir = item.is_dir || false;
        const safeName = item.name.replace(/[<>"']/g, '');
        const fileSize = item.size_fmt || '-';
        const modified = item.modified || '-';
        const icon = item.icon || getFileIcon(ext, isDir);
        const isRootUser = isRoot();
        const isSelected = selectedItems.has(item.path);
        
        const bgColor = isSelected ? 'rgba(106,13,173,0.25)' : (index % 2 === 0 ? 'rgba(10,5,20,0.2)' : 'transparent');
        
        let actionButtons = '';
        
        if (isDir) {
            actionButtons = `
                <button class="act small" onclick="openFolder('${item.path}')" title="Abrir">📂</button>
                ${isRootUser ? `<button class="act small danger" onclick="deleteFile('${item.path}')" title="Eliminar">🗑️</button>` : ''}
            `;
        } else if (MUSIC_EXTENSIONS.includes(ext)) {
            actionButtons = `
                <button class="act small success" onclick="playMusicFile('${item.path}', '${safeName}')" title="Reproducir">🎵</button>
                <button class="act small" onclick="openMusicPlayer()" title="Abrir reproductor">📋</button>
                ${isRootUser ? `<button class="act small danger" onclick="deleteFile('${item.path}')" title="Eliminar">🗑️</button>` : ''}
            `;
        } else if (TEXT_EXTENSIONS.includes(ext) || PDF_EXTENSIONS.includes(ext) || IMAGE_EXTENSIONS.includes(ext) || VIDEO_EXTENSIONS.includes(ext)) {
            actionButtons = `
                <button class="act small" onclick="openDocument('${item.path}')" title="Ver">👁️</button>
                ${isRootUser ? `<button class="act small danger" onclick="deleteFile('${item.path}')" title="Eliminar">🗑️</button>` : ''}
            `;
        } else if (ARCHIVE_EXTENSIONS.includes(ext)) {
            actionButtons = `
                <button class="act small" onclick="openArchive('${item.path}', '${safeName}')" title="Extraer">📦</button>
                ${isRootUser ? `<button class="act small danger" onclick="deleteFile('${item.path}')" title="Eliminar">🗑️</button>` : ''}
            `;
        } else if (['.py', '.sh', '.js', '.bat', '.cmd', '.exe', '.com', '.scr'].includes(ext)) {
            actionButtons = `
                <button class="act small success" onclick="runProgram('${item.path}')" title="Ejecutar">▶️</button>
                ${isRootUser ? `<button class="act small danger" onclick="deleteFile('${item.path}')" title="Eliminar">🗑️</button>` : ''}
            `;
        } else {
            actionButtons = `
                <button class="act small" onclick="openDocument('${item.path}')" title="Ver">👁️</button>
                ${isRootUser ? `<button class="act small danger" onclick="deleteFile('${item.path}')" title="Eliminar">🗑️</button>` : ''}
            `;
        }
        
        if (!isRootUser) {
            actionButtons = actionButtons.replace(/<button class="act small danger".*?<\/button>/, '');
            if (actionButtons.trim() === '') {
                actionButtons = `<span style="color:#6a0dad;font-size:10px;">🔒</span>`;
            }
        }
        
        const nameStyle = isDir ? 'font-weight:600;color:#da70d6;' : 'color:#e6e6fa;';
        const sizeStyle = isDir ? 'color:#6a0dad;' : 'color:#9370db;';
        
        html += `
            <div class="file-item-modern" 
                 style="display:grid;grid-template-columns:45px 1fr 100px 130px auto;gap:4px;padding:6px 8px;background:${bgColor};border-radius:4px;margin:1px 0;cursor:pointer;transition:background 0.15s;align-items:center;"
                 onmouseover="this.style.background='rgba(106,13,173,0.15)'"
                 onmouseout="this.style.background='${bgColor}'"
                 onclick="selectItem('${item.path}')"
                 ondblclick="${isDir ? `openFolder('${item.path}')` : `openDocument('${item.path}')`}"
                 data-path="${item.path}">
                <div style="text-align:center;font-size:20px;">${icon}</div>
                <div style="${nameStyle}font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${safeName}">${safeName}</div>
                <div style="${sizeStyle}font-size:12px;text-align:right;">${fileSize}</div>
                <div style="color:#6a0dad;font-size:11px;text-align:right;">${modified}</div>
                <div style="display:flex;gap:3px;justify-content:center;flex-wrap:wrap;">${actionButtons}</div>
            </div>
        `;
    });
    
    grid.innerHTML = html;
    updateStatusBar(sortedItems.length);
}

function selectItem(path) {
    if (selectedItems.has(path)) {
        selectedItems.delete(path);
    } else {
        selectedItems.add(path);
    }
    loadFiles(currentPath);
}

function updateStatusBar(count) {
    const statusEl = document.getElementById('file-status');
    if (!statusEl) {
        const toolbar = document.querySelector('.file-toolbar');
        if (toolbar) {
            const el = document.createElement('span');
            el.id = 'file-status';
            el.style.cssText = 'color:#9370db;font-size:12px;margin-left:auto;padding:0 10px;';
            toolbar.appendChild(el);
        }
    }
    const el = document.getElementById('file-status');
    if (el) {
        const selected = selectedItems.size;
        el.textContent = `${count} elementos ${selected > 0 ? `(${selected} seleccionados)` : ''}`;
    }
}

// ═══ REPRODUCTOR DE MÚSICA ═══
function playMusicFile(path, name) {
    console.log('🎵 Reproduciendo:', path);
    showNotification(`🎵 ${name}`, 'info');
    openWin('music');
    
    setTimeout(() => {
        if (typeof musicPlayer !== 'undefined' && musicPlayer) {
            let foundIndex = -1;
            for (let i = 0; i < musicPlayer.playlist.length; i++) {
                if (musicPlayer.playlist[i].path === path || musicPlayer.playlist[i].url === path) {
                    foundIndex = i;
                    break;
                }
            }
            
            if (foundIndex >= 0) {
                if (typeof selectTrack === 'function') {
                    selectTrack(foundIndex);
                }
            } else {
                const newTrack = {
                    name: name,
                    path: path,
                    url: path,
                    isDemo: false,
                    size: 0
                };
                musicPlayer.playlist.push(newTrack);
                const newIndex = musicPlayer.playlist.length - 1;
                if (typeof selectTrack === 'function') {
                    selectTrack(newIndex);
                }
                if (typeof updatePlaylistUI === 'function') {
                    updatePlaylistUI();
                }
            }
        }
    }, 500);
}

function openMusicPlayer() {
    openWin('music');
    setTimeout(() => {
        if (typeof musicPlayer !== 'undefined' && !musicPlayer.isLoaded && typeof loadMusicFiles === 'function') {
            loadMusicFiles();
        }
    }, 500);
}

// ═══ ARCHIVOS COMPRIMIDOS ═══
function openArchive(path, name) {
    console.log('📦 Abriendo:', path);
    showNotification(`📦 Extrayendo ${name}...`, 'info');
    
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok && data.viewer_url) {
            window.open(data.viewer_url, '_blank');
            showNotification(`📦 ${name} abierto`, 'success');
        } else {
            showNotification(`📦 ${name} - Descargando...`, 'info');
            const link = document.createElement('a');
            link.href = path;
            link.download = name;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    })
    .catch(err => {
        showNotification(`❌ Error: ${err.message}`, 'error');
    });
}

// ═══ NAVEGACIÓN ═══
function openFolder(path) {
    console.log('📂 Abriendo:', path);
    selectedItems.clear();
    loadFiles(path);
}

function fileUp() {
    if (!currentPath) return;
    if (currentPath === '/D' || currentPath === '/D/') {
        showNotification('📂 Ya estás en la raíz', 'warning');
        return;
    }
    
    let parent = currentPath.replace(/\/$/, '');
    const parts = parent.split('/');
    parts.pop();
    parent = parts.join('/');
    
    if (!parent || parent === '' || parent === '/D') {
        parent = '/D';
    }
    
    selectedItems.clear();
    loadFiles(parent);
}

function refreshFiles() {
    if (currentPath) {
        selectedItems.clear();
        loadFiles(currentPath);
        showNotification('🔄 Actualizado', 'info');
    }
}

// ═══ EJECUTAR PROGRAMA ═══
function runProgram(path) {
    const name = path.split('/').pop();
    console.log('▶️ Ejecutando:', path);
    showNotification(`⏳ Ejecutando ${name}...`, 'info');
    
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    })
    .then(r => r.json())
    .then(data => {
        console.log('📤 Respuesta:', data);
        if (data.ok) {
            if (data.viewer_url) {
                window.open(data.viewer_url, '_blank');
                showNotification(`📄 ${name} abierto`, 'success');
            } else if (data.session_id) {
                showNotification(`✅ ${name} ejecutado (PID ${data.pid})`, 'success');
                if (typeof openTerminalForProcess === 'function') {
                    openTerminalForProcess(data.session_id, name);
                }
                if (typeof loadServers === 'function') loadServers();
            } else if (data.stdout) {
                showOutputWindow(name, data.stdout);
            } else {
                showNotification(data.message || `✅ ${name} ejecutado`, 'success');
            }
        } else {
            showNotification(`❌ Error: ${data.error || 'desconocido'}`, 'error');
        }
    })
    .catch(err => {
        console.error('❌ Error:', err);
        showNotification(`❌ Error: ${err.message}`, 'error');
    });
}

function showOutputWindow(name, output) {
    const win = document.createElement('div');
    win.id = 'win-output';
    win.className = 'window resizable';
    win.style.cssText = 'top:80px;left:80px;width:700px;height:500px;display:flex;flex-direction:column;z-index:9999;';
    win.dataset.title = `📤 Salida: ${name}`;
    
    win.innerHTML = `
        <div class="title-bar" onmousedown="startDrag(event,'output')">
            <span>📤 Salida: ${name}</span>
            <div class="controls">
                <button class="btn btn-min" onclick="minimizeWin('output')">─</button>
                <button class="btn btn-max" onclick="maximizeWin('output')">▢</button>
                <button class="btn btn-close" onclick="closeWin('output')">✕</button>
            </div>
        </div>
        <div class="window-body" style="padding:10px;display:flex;flex-direction:column;height:100%;background:#0a0a1a;">
            <div style="display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap;">
                <button class="act small" onclick="navigator.clipboard.writeText(document.getElementById('output-content').textContent).then(() => showNotification('📋 Copiado', 'success'))">📋 Copiar</button>
                <button class="act small" onclick="document.getElementById('output-content').textContent=''">🗑️ Limpiar</button>
                <button class="act small success" onclick="closeWin('output')">✅ Cerrar</button>
            </div>
            <pre id="output-content" style="flex:1;margin:0;padding:10px;overflow-y:auto;background:#0a0a1a;color:#e6e6fa;font-family:'Consolas',monospace;font-size:13px;white-space:pre-wrap;word-wrap:break-word;border:1px solid #4b0082;border-radius:4px;">${output}</pre>
        </div>
    `;
    
    document.body.appendChild(win);
    win.style.display = 'flex';
    win.classList.add('active');
    win.style.zIndex = ++windowZIndex;
    updateTaskbar('output');
}

// ═══ ABRIR DOCUMENTO ═══
function openDocument(path) {
    const name = path.split('/').pop();
    console.log('📄 Abriendo:', path);
    showNotification(`📄 Abriendo ${name}...`, 'info');
    
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok && data.viewer_url) {
            window.open(data.viewer_url, '_blank');
            showNotification(`📄 ${name} abierto`, 'success');
        } else if (data.ok && data.stdout) {
            showOutputWindow(name, data.stdout);
        } else {
            const link = document.createElement('a');
            link.href = path;
            link.download = name;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            showNotification(`📄 ${name} descargado`, 'success');
        }
    })
    .catch(err => {
        console.error('❌ Error:', err);
        showNotification(`❌ Error: ${err.message}`, 'error');
    });
}

// ═══ ELIMINAR (SOLO ROOT) ═══
function deleteFile(path) {
    const name = path.split('/').pop();
    
    if (!isRoot()) {
        showNotification('❌ Solo root puede eliminar', 'error');
        return;
    }
    
    if (!confirm(`⚠️ ¿Eliminar "${name}"?\n\nEsta acción no se puede deshacer.`)) return;
    if (!confirm(`¿Estás seguro de eliminar "${name}"?`)) return;
    
    fetch('/api/files/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            selectedItems.delete(path);
            refreshFiles();
            showNotification(`✅ "${name}" eliminado`, 'success');
        } else {
            showNotification(`❌ Error: ${data.error || 'desconocido'}`, 'error');
        }
    })
    .catch(err => {
        console.error('❌ Error:', err);
        showNotification(`❌ Error: ${err.message}`, 'error');
    });
}

// ═══ CREAR CARPETA ═══
function createFolderPrompt() {
    const name = prompt('📁 Nombre de la carpeta:');
    if (!name || name.trim() === '') return;
    
    const invalidChars = /[<>:"/\\|?*]/;
    if (invalidChars.test(name)) {
        showNotification('❌ Caracteres inválidos', 'error');
        return;
    }
    
    fetch('/api/files/folder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: currentPath, name: name.trim() })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            refreshFiles();
            showNotification(`✅ Carpeta "${name}" creada`, 'success');
        } else {
            showNotification(`❌ Error: ${data.error || 'desconocido'}`, 'error');
        }
    })
    .catch(err => {
        console.error('❌ Error:', err);
        showNotification(`❌ Error: ${err.message}`, 'error');
    });
}

// ═══ BUSCAR ═══
function searchFiles() {
    const input = document.getElementById('file-search');
    const query = input?.value.trim();
    
    if (!query) {
        refreshFiles();
        return;
    }
    
    const grid = document.getElementById('file-grid');
    grid.innerHTML = `
        <div style="display:flex;justify-content:center;align-items:center;height:200px;flex-direction:column;color:#9370db;">
            <div style="font-size:32px;margin-bottom:10px;">🔍</div>
            <div style="font-size:13px;">Buscando: "${query}"...</div>
        </div>
    `;
    
    fetch(`/api/files/search?q=${encodeURIComponent(query)}`)
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                grid.innerHTML = `
                    <div style="display:flex;justify-content:center;align-items:center;height:200px;color:#ff6b6b;">
                        <div style="text-align:center;">
                            <div style="font-size:32px;margin-bottom:10px;">❌</div>
                            <div style="font-size:13px;">${data.error}</div>
                        </div>
                    </div>
                `;
                return;
            }
            
            const results = data.results || [];
            if (results.length === 0) {
                grid.innerHTML = `
                    <div style="display:flex;justify-content:center;align-items:center;height:200px;flex-direction:column;color:#9370db;">
                        <div style="font-size:48px;margin-bottom:15px;">🔍</div>
                        <div style="font-size:14px;">No se encontraron resultados</div>
                        <div style="font-size:12px;color:#6a0dad;">"${query}"</div>
                    </div>
                `;
                return;
            }
            
            let html = `
                <div style="display:grid;grid-template-columns:45px 1fr 100px auto;gap:4px;padding:4px 8px;background:rgba(75,0,130,0.2);border-bottom:1px solid rgba(106,13,173,0.3);font-size:11px;color:#9370db;font-weight:600;position:sticky;top:0;z-index:5;">
                    <div style="text-align:center;">📁</div>
                    <div>Nombre</div>
                    <div style="text-align:right;">Tamaño</div>
                    <div style="text-align:center;">Acciones</div>
                </div>
            `;
            
            results.forEach((item, index) => {
                const ext = item.name.split('.').pop()?.toLowerCase() || '';
                const safeName = item.name.replace(/[<>"']/g, '');
                const icon = item.icon || getFileIcon('.' + ext, false);
                const isMusic = MUSIC_EXTENSIONS.includes('.' + ext);
                const bgColor = index % 2 === 0 ? 'rgba(10,5,20,0.2)' : 'transparent';
                const isRootUser = isRoot();
                
                let actionBtn = '';
                if (isMusic) {
                    actionBtn = `<button class="act small success" onclick="playMusicFile('${item.path}', '${safeName}')">🎵</button>`;
                } else {
                    actionBtn = `<button class="act small" onclick="openDocument('${item.path}')">👁️</button>`;
                }
                
                if (isRootUser) {
                    actionBtn += ` <button class="act small danger" onclick="deleteFile('${item.path}')">🗑️</button>`;
                }
                
                html += `
                    <div style="display:grid;grid-template-columns:45px 1fr 100px auto;gap:4px;padding:6px 8px;background:${bgColor};border-radius:4px;margin:1px 0;align-items:center;">
                        <div style="text-align:center;font-size:20px;">${icon}</div>
                        <div style="color:#e6e6fa;font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${safeName}">${safeName}</div>
                        <div style="color:#9370db;font-size:12px;text-align:right;">${item.size_fmt || '-'}</div>
                        <div style="display:flex;gap:3px;justify-content:center;flex-wrap:wrap;">${actionBtn}</div>
                    </div>
                `;
            });
            grid.innerHTML = html;
        })
        .catch(err => {
            console.error('❌ Error:', err);
            grid.innerHTML = `
                <div style="display:flex;justify-content:center;align-items:center;height:200px;color:#ff6b6b;">
                    <div style="text-align:center;">
                        <div style="font-size:32px;margin-bottom:10px;">❌</div>
                        <div style="font-size:13px;">Error: ${err.message}</div>
                    </div>
                </div>
            `;
        });
}

// ═══ SUBIR ARCHIVOS ═══
function uploadFiles(input) {
    const files = input.files;
    if (!files || files.length === 0) return;
    
    const formData = new FormData();
    const totalFiles = files.length;
    
    for (const file of files) {
        formData.append('file', file);
    }
    
    showNotification(`⏳ Subiendo ${totalFiles} archivo${totalFiles > 1 ? 's' : ''}...`, 'info');
    
    fetch(`/api/files/upload?path=${encodeURIComponent(currentPath)}`, {
        method: 'POST',
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        input.value = '';
        if (data.ok) {
            refreshFiles();
            showNotification(`✅ ${totalFiles} archivo${totalFiles > 1 ? 's' : ''} subido${totalFiles > 1 ? 's' : ''}`, 'success');
        } else {
            showNotification(`❌ Error subiendo archivos: ${data.error || 'desconocido'}`, 'error');
        }
    })
    .catch(() => {
        input.value = '';
        showNotification('❌ Error de conexión', 'error');
    });
}

// ═══ NOTIFICACIONES ═══
function showNotification(message, type = 'info') {
    const colors = {
        info: '#9370db',
        success: '#00cc66',
        error: '#ff4444',
        warning: '#ffaa00'
    };
    
    const icons = {
        info: 'ℹ️',
        success: '✅',
        error: '❌',
        warning: '⚠️'
    };
    
    const div = document.createElement('div');
    div.style.cssText = `
        position: fixed;
        bottom: 70px;
        right: 20px;
        background: rgba(10,5,20,0.95);
        border: 2px solid ${colors[type] || '#9370db'};
        color: #fff;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 10000;
        max-width: 400px;
        font-size: 13px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.6);
        animation: slideIn 0.3s ease;
        font-family: 'Segoe UI', sans-serif;
        backdrop-filter: blur(10px);
        border-left: 4px solid ${colors[type] || '#9370db'};
        display:flex;align-items:center;gap:10px;
    `;
    div.innerHTML = `<span style="font-size:18px;">${icons[type] || 'ℹ️'}</span> <span>${message}</span>`;
    document.body.appendChild(div);
    
    setTimeout(() => {
        div.style.opacity = '0';
        div.style.transition = 'opacity 0.5s ease, transform 0.3s ease';
        div.style.transform = 'translateX(20px)';
        setTimeout(() => div.remove(), 500);
    }, 4000);
}

// ═══ EXPORTAR ═══
window.openTerminalForProcess = openTerminalForProcess;
window.closeTerminalWindow = closeTerminalWindow;
window.loadFiles = loadFiles;
window.renderFiles = renderFiles;
window.openFolder = openFolder;
window.fileUp = fileUp;
window.refreshFiles = refreshFiles;
window.runProgram = runProgram;
window.openDocument = openDocument;
window.deleteFile = deleteFile;
window.createFolderPrompt = createFolderPrompt;
window.searchFiles = searchFiles;
window.uploadFiles = uploadFiles;
window.playMusicFile = playMusicFile;
window.openMusicPlayer = openMusicPlayer;
window.downloadFile = downloadFile;
window.openArchive = openArchive;
window.getCurrentUser = getCurrentUser;
window.isRoot = isRoot;
window.showNotification = showNotification;

// ═══ INICIALIZAR ═══
if (!fileManagerInitialized) {
    fileManagerInitialized = true;
    
    getCurrentUser().then(() => {
        console.log(`👤 Usuario: ${currentUser}`);
        if (isRoot()) console.log('🔑 Modo ROOT');
        else console.log('🔒 Modo USER');
    });
    
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(() => {
            const win = document.getElementById('win-explorer');
            if (win && win.style.display !== 'none') {
                loadFiles('/D');
            }
        }, 500);
    });
    
    const observer = new MutationObserver(() => {
        const win = document.getElementById('win-explorer');
        if (win && win.style.display !== 'none' && win.style.display !== '') {
            const grid = document.getElementById('file-grid');
            if (grid && grid.children.length === 0) {
                loadFiles('/D');
            }
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        .file-item-modern:hover {
            background: rgba(106,13,173,0.2) !important;
        }
        .file-toolbar {
            display: flex;
            gap: 6px;
            align-items: center;
            padding: 6px 10px;
            background: rgba(10,5,20,0.5);
            border-bottom: 1px solid rgba(106,13,173,0.2);
            flex-wrap: wrap;
        }
        .file-toolbar .act.small {
            padding: 4px 10px;
            font-size: 12px;
            border-radius: 4px;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            background: rgba(75,0,130,0.3);
            color: #e6e6fa;
        }
        .file-toolbar .act.small:hover {
            background: rgba(106,13,173,0.5);
            transform: scale(1.03);
        }
        .file-toolbar input {
            padding: 4px 10px;
            border-radius: 4px;
            border: 1px solid rgba(106,13,173,0.3);
            background: rgba(10,5,20,0.6);
            color: #e6e6fa;
            font-size: 12px;
            outline: none;
        }
        .file-toolbar input:focus {
            border-color: #6a0dad;
            box-shadow: 0 0 10px rgba(106,13,173,0.2);
        }
        .file-path {
            flex: 1;
            min-width: 150px;
            font-family: monospace;
            font-size: 12px;
        }
        .window-body {
            background: #0a0514;
        }
        #file-grid {
            padding: 4px;
            max-height: calc(100% - 50px);
            overflow-y: auto;
        }
        #file-grid::-webkit-scrollbar {
            width: 6px;
        }
        #file-grid::-webkit-scrollbar-track {
            background: rgba(10,5,20,0.5);
            border-radius: 3px;
        }
        #file-grid::-webkit-scrollbar-thumb {
            background: #6a0dad;
            border-radius: 3px;
        }
        #file-grid::-webkit-scrollbar-thumb:hover {
            background: #9370db;
        }
        .act.small.success {
            background: rgba(0,136,0,0.4);
            color: #00cc66;
        }
        .act.small.success:hover {
            background: rgba(0,136,0,0.6);
        }
        .act.small.danger {
            background: rgba(139,0,0,0.4);
            color: #ff4444;
        }
        .act.small.danger:hover {
            background: rgba(139,0,0,0.6);
        }
        @media (max-width: 768px) {
            .file-item-modern {
                grid-template-columns: 35px 1fr 60px auto !important;
                font-size: 12px;
                padding: 4px 6px !important;
            }
            .file-item-modern .file-modified {
                display: none;
            }
            .file-toolbar input {
                font-size: 10px;
                padding: 3px 6px;
            }
            .file-toolbar .act.small {
                font-size: 10px;
                padding: 3px 6px;
            }
            .file-path {
                min-width: 80px;
                font-size: 10px;
            }
        }
        @media (max-width: 480px) {
            .file-item-modern {
                grid-template-columns: 30px 1fr auto !important;
                gap: 3px !important;
            }
            .file-item-modern .file-size {
                display: none;
            }
            .file-toolbar {
                gap: 3px;
                padding: 4px 6px;
            }
            .file-toolbar input {
                min-width: 60px;
            }
        }
    `;
    document.head.appendChild(style);
}

console.log('📁 File Manager Moderno v3.0 - Estilo Total Commander');
console.log('📌 Características: Selección múltiple, diseño moderno, responsive');
