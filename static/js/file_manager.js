// KALM OS v4.3 - File Manager (MEJORADO Y CORREGIDO)
// Solo el usuario root puede eliminar archivos

let currentPath = '/D';
let fileManagerInitialized = false;
let currentUser = null;

// ═══ OBTENER USUARIO ACTUAL ═══
function getCurrentUser() {
    return new Promise((resolve) => {
        if (currentUser) {
            resolve(currentUser);
            return;
        }
        
        // Intentar obtener de la cookie
        const cookies = document.cookie.split(';');
        for (const c of cookies) {
            const trimmed = c.trim();
            if (trimmed.startsWith('session_id=')) {
                // Si tenemos session, intentar obtener usuario
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
        
        // Si no hay sesión, asumir user
        currentUser = 'user';
        resolve(currentUser);
    });
}

// ═══ VERIFICAR SI ES ROOT ═══
function isRoot() {
    return currentUser === 'root';
}

// ═══ EXTENSIONES SOPORTADAS ═══
const TEXT_EXTENSIONS = ['.txt', '.md', '.log', '.json', '.xml', '.yaml', '.yml', '.csv', '.py', '.js', '.html', '.css', '.sql', '.sh', '.bat', '.cmd'];
const MUSIC_EXTENSIONS = ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.wma'];
const IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico', '.tiff', '.tif'];
const PDF_EXTENSIONS = ['.pdf'];
const VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'];
const ARCHIVE_EXTENSIONS = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'];

// ═══ ICONOS POR EXTENSIÓN ═══
function getFileIcon(ext, isDir) {
    if (isDir) return '📁';
    
    const iconMap = {
        // Documentos
        '.txt': '📄', '.md': '📝', '.log': '📋', '.pdf': '📕',
        '.doc': '📘', '.docx': '📘', '.xls': '📊', '.xlsx': '📊',
        '.ppt': '📙', '.pptx': '📙',
        // Código
        '.py': '🐍', '.js': '📦', '.html': '🌐', '.css': '🎨',
        '.json': '📋', '.xml': '📋', '.yaml': '📋', '.yml': '📋',
        '.sql': '🗄️', '.sh': '🐚', '.bat': '📜', '.cmd': '📜',
        '.java': '☕', '.cpp': '⚙️', '.c': '⚙️', '.go': '🐹',
        '.rs': '🦀', '.rb': '💎', '.php': '🐘',
        // Imágenes
        '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️',
        '.bmp': '🖼️', '.webp': '🖼️', '.svg': '🖼️', '.ico': '🖼️',
        '.tiff': '🖼️', '.tif': '🖼️',
        // Música
        '.mp3': '🎵', '.wav': '🎵', '.ogg': '🎵', '.flac': '🎵',
        '.m4a': '🎵', '.aac': '🎵', '.wma': '🎵',
        // Videos
        '.mp4': '🎬', '.avi': '🎬', '.mkv': '🎬', '.mov': '🎬',
        '.wmv': '🎬', '.flv': '🎬', '.webm': '🎬',
        // Archivos comprimidos
        '.zip': '📦', '.rar': '📦', '.7z': '📦', '.tar': '📦',
        '.gz': '📦', '.bz2': '📦', '.xz': '📦',
        // Ejecutables
        '.exe': '⚙️', '.msi': '📦', '.app': '📱', '.deb': '📦',
        '.rpm': '📦', '.dmg': '💿',
        // Otros
        '.iso': '💿', '.img': '💿',
    };
    
    return iconMap[ext] || '📄';
}

// ═══ FORMATO DE TAMAÑO ═══
function formatSize(bytes) {
    if (bytes === 0) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + units[i];
}

// ═══ Cargar archivos ═══
function loadFiles(path) {
    const grid = document.getElementById('file-grid');
    const pathInput = document.getElementById('file-path');
    
    if (!grid) {
        console.warn('⚠️ file-grid no encontrado');
        return;
    }
    
    // Normalizar ruta
    if (!path || path === '' || path === 'D:' || path === 'D:/' || path === 'D:\\') {
        path = '/D';
    }
    
    if (path.startsWith('D:/') || path.startsWith('D:\\')) {
        path = path.replace(/^D:[/\\]/, '/D/');
    }
    
    currentPath = path;
    if (pathInput) pathInput.value = path;
    
    // Mostrar spinner de carga mejorado
    grid.innerHTML = `
        <div style="text-align:center;padding:60px 20px;color:#9370db;">
            <div style="font-size:40px;margin-bottom:15px;">⏳</div>
            <div style="font-size:14px;">Cargando archivos...</div>
        </div>
    `;
    
    const url = `/api/files?path=${encodeURIComponent(path)}`;
    console.log('📂 Cargando:', url);
    
    fetch(url)
        .then(r => {
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return r.json();
        })
        .then(data => {
            // Obtener usuario actual primero
            getCurrentUser().then(() => {
                renderFiles(data);
            });
        })
        .catch(err => {
            console.error('❌ Error cargando archivos:', err);
            grid.innerHTML = `
                <div style="color:#ff6b6b;padding:40px;text-align:center;">
                    <div style="font-size:40px;margin-bottom:15px;">❌</div>
                    <div style="font-size:14px;">Error: ${err.message}</div>
                    <button class="act small" onclick="refreshFiles()" style="margin-top:15px;">🔄 Reintentar</button>
                </div>
            `;
        });
}

// ═══ Renderizar archivos (MEJORADO) ═══
function renderFiles(data) {
    const grid = document.getElementById('file-grid');
    if (!grid) return;
    
    if (!data || data.error) {
        grid.innerHTML = `
            <div style="color:#ff6b6b;padding:40px;text-align:center;">
                <div style="font-size:40px;margin-bottom:15px;">⚠️</div>
                <div style="font-size:14px;">${data?.error || 'Error desconocido'}</div>
            </div>
        `;
        return;
    }
    
    const items = data.items || [];
    
    if (items.length === 0) {
        grid.innerHTML = `
            <div style="color:#9370db;padding:60px 20px;text-align:center;">
                <div style="font-size:48px;margin-bottom:15px;">📂</div>
                <div style="font-size:14px;">Carpeta vacía</div>
                <div style="font-size:12px;color:#6a0dad;margin-top:8px;">Haz clic en "📁 Nuevo" para crear una carpeta</div>
            </div>
        `;
        return;
    }
    
    // Agrupar: carpetas primero, luego archivos
    const folders = items.filter(i => i.is_dir);
    const files = items.filter(i => !i.is_dir);
    const sortedItems = [...folders, ...files];
    
    let html = '';
    sortedItems.forEach(item => {
        const ext = item.ext || '';
        const isDir = item.is_dir || false;
        const isText = TEXT_EXTENSIONS.includes(ext);
        const isMusic = MUSIC_EXTENSIONS.includes(ext);
        const isImage = IMAGE_EXTENSIONS.includes(ext);
        const isPdf = PDF_EXTENSIONS.includes(ext);
        const isVideo = VIDEO_EXTENSIONS.includes(ext);
        const isArchive = ARCHIVE_EXTENSIONS.includes(ext);
        const isExecutable = ['.py', '.sh', '.js', '.bat', '.cmd', '.exe', '.com', '.scr'].includes(ext);
        
        // Escapar nombre para evitar XSS
        const safeName = item.name.replace(/[<>"']/g, '');
        const fileSize = item.size_fmt || '-';
        const modified = item.modified || '-';
        const icon = item.icon || getFileIcon(ext, isDir);
        
        // Determinar qué botones mostrar
        let actionButtons = '';
        const isRootUser = isRoot();
        
        if (isDir) {
            actionButtons = `
                <button class="act small" onclick="openFolder('${item.path}')" title="Abrir carpeta">📂 Abrir</button>
                ${isRootUser ? `<button class="act small danger" onclick="deleteFile('${item.path}')" title="Eliminar carpeta">🗑️</button>` : ''}
            `;
        } else if (isMusic) {
            actionButtons = `
                <button class="act small success" onclick="playMusicFile('${item.path}', '${safeName}')" title="Reproducir">🎵</button>
                <button class="act small" onclick="openMusicPlayer()" title="Abrir reproductor">📋</button>
                ${isRootUser ? `<button class="act small danger" onclick="deleteFile('${item.path}')" title="Eliminar archivo">🗑️</button>` : ''}
            `;
        } else if (isText || isPdf || isImage || isVideo) {
            actionButtons = `
                <button class="act small" onclick="openDocument('${item.path}')" title="Ver archivo">👁️ Ver</button>
                ${isRootUser ? `<button class="act small danger" onclick="deleteFile('${item.path}')" title="Eliminar archivo">🗑️</button>` : ''}
            `;
        } else if (isArchive) {
            actionButtons = `
                <button class="act small" onclick="openArchive('${item.path}', '${safeName}')" title="Ver contenido">📦 Extraer</button>
                ${isRootUser ? `<button class="act small danger" onclick="deleteFile('${item.path}')" title="Eliminar archivo">🗑️</button>` : ''}
            `;
        } else if (isExecutable) {
            actionButtons = `
                <button class="act small success" onclick="runProgram('${item.path}')" title="Ejecutar programa">▶️</button>
                ${isRootUser ? `<button class="act small danger" onclick="deleteFile('${item.path}')" title="Eliminar archivo">🗑️</button>` : ''}
            `;
        } else {
            // Archivo genérico
            actionButtons = `
                <button class="act small" onclick="openDocument('${item.path}')" title="Ver archivo">👁️ Ver</button>
                ${isRootUser ? `<button class="act small danger" onclick="deleteFile('${item.path}')" title="Eliminar archivo">🗑️</button>` : ''}
            `;
        }
        
        // Si no es root, mostrar candado en lugar de eliminar
        if (!isRootUser && !isDir) {
            actionButtons = actionButtons.replace(/<button class="act small danger".*?<\/button>/, '');
            if (actionButtons.trim() === '') {
                actionButtons = `<span style="color:#6a0dad;font-size:10px;">🔒 Solo root</span>`;
            }
        }
        
        // Si es root y no tiene botón de eliminar, agregarlo
        if (isRootUser && !actionButtons.includes('🗑️') && !isDir) {
            actionButtons += ` <button class="act small danger" onclick="deleteFile('${item.path}')" title="Eliminar archivo">🗑️</button>`;
        }
        
        // Si es root y es carpeta, asegurar botón de eliminar
        if (isRootUser && isDir && !actionButtons.includes('🗑️')) {
            actionButtons += ` <button class="act small danger" onclick="deleteFile('${item.path}')" title="Eliminar carpeta">🗑️</button>`;
        }
        
        const sizeClass = isDir ? 'dir-size' : '';
        const nameClass = isDir ? 'dir-name' : '';
        
        html += `
            <div class="file-item ${isDir ? 'folder-item' : 'file-item-row'}" 
                 ${isDir ? `ondblclick="openFolder('${item.path}')"` : ''}
                 data-path="${item.path}"
                 data-name="${safeName}">
                <div class="file-icon">${icon}</div>
                <div class="file-name ${nameClass}" title="${safeName}">${safeName}</div>
                <div class="file-size ${sizeClass}">${fileSize}</div>
                <div class="file-modified">${modified}</div>
                <div class="file-actions">${actionButtons}</div>
            </div>
        `;
    });
    
    grid.innerHTML = html;
    
    // Actualizar contador de archivos
    updateFileCount(sortedItems.length);
}

// ═══ ACTUALIZAR CONTADOR DE ARCHIVOS ═══
function updateFileCount(count) {
    const statusBar = document.querySelector('#win-explorer .file-path');
    if (statusBar) {
        // No modificar el path, solo agregar contador en otro lugar
    }
    const countEl = document.getElementById('file-count');
    if (!countEl) {
        const toolbar = document.querySelector('.file-toolbar');
        if (toolbar) {
            const el = document.createElement('span');
            el.id = 'file-count';
            el.style.cssText = 'color:#9370db;font-size:12px;margin-left:10px;';
            toolbar.appendChild(el);
        }
    }
    const el = document.getElementById('file-count');
    if (el) {
        el.textContent = `📄 ${count} elemento${count !== 1 ? 's' : ''}`;
    }
}

// ═══ REPRODUCIR ARCHIVO DE MÚSICA DESDE EL EXPLORADOR ═══
function playMusicFile(path, name) {
    console.log('🎵 Reproduciendo:', path);
    showNotification(`🎵 Reproduciendo: ${name}`, 'info');
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

// ═══ ABRIR REPRODUCTOR DE MÚSICA ═══
function openMusicPlayer() {
    openWin('music');
    setTimeout(() => {
        if (typeof musicPlayer !== 'undefined' && !musicPlayer.isLoaded && typeof loadMusicFiles === 'function') {
            loadMusicFiles();
        }
    }, 500);
}

// ═══ ABRIR ARCHIVO COMPRIMIDO ═══
function openArchive(path, name) {
    console.log('📦 Abriendo archivo:', path);
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
            // Si no hay visor, intentar descargar
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

// ═══ Navegación ═══
function openFolder(path) {
    console.log('📂 Abriendo carpeta:', path);
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
    
    console.log('📂 Subiendo a:', parent);
    loadFiles(parent);
}

function refreshFiles() {
    if (currentPath) {
        console.log('🔄 Refrescando:', currentPath);
        loadFiles(currentPath);
        showNotification('🔄 Archivos actualizados', 'info');
    }
}

// ═══ Ejecutar programa (MEJORADO) ═══
function runProgram(path) {
    const name = path.split('/').pop();
    console.log('▶️ Ejecutando:', path);
    showNotification(`⏳ Ejecutando ${name}...`, 'info');
    
    // Mostrar feedback visual
    const grid = document.getElementById('file-grid');
    const originalHtml = grid ? grid.innerHTML : '';
    
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    })
    .then(r => r.json())
    .then(data => {
        console.log('📤 Respuesta ejecución:', data);
        if (data.ok) {
            if (data.viewer_url) {
                window.open(data.viewer_url, '_blank');
                showNotification(`📄 ${name} abierto en visor`, 'success');
            } else if (data.session_id) {
                showNotification(`✅ ${name} ejecutado (PID ${data.pid})`, 'success');
                if (typeof openTerminalForProcess === 'function') {
                    openTerminalForProcess(data.session_id, name);
                }
                if (typeof loadServers === 'function') loadServers();
            } else if (data.stdout) {
                // Mostrar salida en una ventana modal
                showOutputWindow(name, data.stdout);
            } else {
                showNotification(data.message || `✅ ${name} ejecutado`, 'success');
            }
        } else {
            showNotification(`❌ Error: ${data.error || 'desconocido'}`, 'error');
        }
    })
    .catch(err => {
        console.error('❌ Error ejecutando:', err);
        showNotification(`❌ Error: ${err.message}`, 'error');
    });
}

// ═══ MOSTRAR VENTANA DE SALIDA ═══
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

// ═══ Abrir documento (TXT, PDF, imágenes, videos) ═══
function openDocument(path) {
    const name = path.split('/').pop();
    console.log('📄 Abriendo documento:', path);
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
            showNotification(`📄 ${name} abierto en visor`, 'success');
        } else if (data.ok && data.stdout) {
            showOutputWindow(name, data.stdout);
        } else {
            // Intentar descargar
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
        console.error('❌ Error abriendo documento:', err);
        showNotification(`❌ Error: ${err.message}`, 'error');
    });
}

// ═══ Eliminar (SOLO ROOT) ═══
function deleteFile(path) {
    const name = path.split('/').pop();
    
    // Verificar si es root
    if (!isRoot()) {
        showNotification('❌ Solo el usuario root puede eliminar archivos', 'error');
        return;
    }
    
    if (!confirm(`⚠️ ¿Eliminar "${name}"?\n\nEsta acción no se puede deshacer.`)) return;
    
    // Verificar nuevamente
    if (!confirm(`¿Estás seguro de eliminar "${name}"?`)) return;
    
    fetch('/api/files/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            refreshFiles();
            showNotification(`✅ "${name}" eliminado`, 'success');
        } else {
            showNotification(`❌ Error: ${data.error || 'desconocido'}`, 'error');
        }
    })
    .catch(err => {
        console.error('❌ Error eliminando:', err);
        showNotification(`❌ Error: ${err.message}`, 'error');
    });
}

// ═══ Crear carpeta (MEJORADO) ═══
function createFolderPrompt() {
    const name = prompt('📁 Nombre de la carpeta:');
    if (!name || name.trim() === '') return;
    
    // Validar nombre
    const invalidChars = /[<>:"/\\|?*]/;
    if (invalidChars.test(name)) {
        showNotification('❌ El nombre contiene caracteres inválidos', 'error');
        return;
    }
    
    if (name.trim().length < 1) {
        showNotification('❌ El nombre debe tener al menos 1 carácter', 'error');
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
        console.error('❌ Error creando carpeta:', err);
        showNotification(`❌ Error: ${err.message}`, 'error');
    });
}

// ═══ Buscar (MEJORADO) ═══
function searchFiles() {
    const input = document.getElementById('file-search');
    const query = input?.value.trim();
    
    if (!query) {
        refreshFiles();
        return;
    }
    
    const grid = document.getElementById('file-grid');
    grid.innerHTML = `
        <div style="text-align:center;padding:60px 20px;color:#9370db;">
            <div style="font-size:40px;margin-bottom:15px;">🔍</div>
            <div style="font-size:14px;">Buscando: "${query}"...</div>
        </div>
    `;
    
    fetch(`/api/files/search?q=${encodeURIComponent(query)}`)
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                grid.innerHTML = `
                    <div style="color:#ff6b6b;padding:40px;text-align:center;">
                        <div style="font-size:40px;margin-bottom:15px;">❌</div>
                        <div style="font-size:14px;">${data.error}</div>
                    </div>
                `;
                return;
            }
            
            const results = data.results || [];
            if (results.length === 0) {
                grid.innerHTML = `
                    <div style="color:#9370db;padding:60px 20px;text-align:center;">
                        <div style="font-size:48px;margin-bottom:15px;">🔍</div>
                        <div style="font-size:14px;">No se encontraron resultados para "${query}"</div>
                    </div>
                `;
                return;
            }
            
            let html = '';
            results.forEach(item => {
                const safeName = item.name.replace(/[<>"']/g, '');
                const ext = item.name.split('.').pop()?.toLowerCase() || '';
                const isMusic = MUSIC_EXTENSIONS.includes('.' + ext);
                const isImage = IMAGE_EXTENSIONS.includes('.' + ext);
                const isDir = item.is_dir || false;
                const icon = item.icon || getFileIcon('.' + ext, isDir);
                const isRootUser = isRoot();
                
                let actionBtn = '';
                if (isMusic) {
                    actionBtn = `<button class="act small success" onclick="playMusicFile('${item.path}', '${safeName}')">🎵</button>`;
                } else if (isImage) {
                    actionBtn = `<button class="act small" onclick="openDocument('${item.path}')">👁️</button>`;
                } else {
                    actionBtn = `<button class="act small" onclick="openDocument('${item.path}')">👁️</button>`;
                }
                
                if (isRootUser) {
                    actionBtn += ` <button class="act small danger" onclick="deleteFile('${item.path}')">🗑️</button>`;
                }
                
                html += `
                    <div class="file-item file-item-row">
                        <div class="file-icon">${icon}</div>
                        <div class="file-name" title="${safeName}">${safeName}</div>
                        <div class="file-size">${item.size_fmt || '-'}</div>
                        <div class="file-actions">${actionBtn}</div>
                    </div>
                `;
            });
            grid.innerHTML = html;
            
            // Mostrar contador
            const countEl = document.getElementById('file-count');
            if (countEl) {
                countEl.textContent = `🔍 ${results.length} resultado${results.length !== 1 ? 's' : ''}`;
            }
        })
        .catch(err => {
            console.error('❌ Error buscando:', err);
            grid.innerHTML = `
                <div style="color:#ff6b6b;padding:40px;text-align:center;">
                    <div style="font-size:40px;margin-bottom:15px;">❌</div>
                    <div style="font-size:14px;">Error: ${err.message}</div>
                </div>
            `;
        });
}

// ═══ Subir archivos (MEJORADO) ═══
function uploadFiles(input) {
    const files = input.files;
    if (!files || files.length === 0) return;
    
    // Mostrar progreso
    const grid = document.getElementById('file-grid');
    const originalHtml = grid ? grid.innerHTML : '';
    
    const formData = new FormData();
    let totalFiles = files.length;
    let uploaded = 0;
    
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
        showNotification('❌ Error de conexión al subir archivos', 'error');
    });
}

// ═══ EXPORTAR ARCHIVOS (DESCARGAR) ═══
function downloadFile(path) {
    const name = path.split('/').pop();
    const link = document.createElement('a');
    link.href = path;
    link.download = name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showNotification(`📥 Descargando ${name}...`, 'info');
}

// ═══ TERMINAL VIRTUAL ═══
function openTerminalForProcess(sessionId, programName) {
    let win = document.getElementById('win-terminal');
    
    if (win) {
        win.style.display = 'flex';
        win.classList.add('active');
        win.style.zIndex = ++windowZIndex;
        const titleBar = win.querySelector('.title-bar span');
        if (titleBar) titleBar.textContent = `💻 Terminal: ${programName || 'Proceso'}`;
        startTerminalStream(sessionId);
        updateTaskbar('terminal');
        return win;
    }
    
    win = document.createElement('div');
    win.id = 'win-terminal';
    win.className = 'window resizable';
    win.style.cssText = 'top:100px;left:100px;width:750px;height:500px;display:flex;flex-direction:column;z-index:9999;';
    win.dataset.title = `💻 Terminal: ${programName || 'Proceso'}`;
    
    win.innerHTML = `
        <div class="title-bar" onmousedown="startDrag(event,'terminal')">
            <span>💻 Terminal: ${programName || 'Proceso'}</span>
            <div class="controls">
                <button class="btn btn-min" onclick="minimizeWin('terminal')">─</button>
                <button class="btn btn-max" onclick="maximizeWin('terminal')">▢</button>
                <button class="btn btn-close" onclick="closeTerminalWindow()">✕</button>
            </div>
        </div>
        <div class="window-body" style="padding:0;display:flex;flex-direction:column;height:100%;">
            <pre id="term-output" style="flex:1;margin:0;padding:10px;overflow-y:auto;background:#0a0a1a;color:#0f0;font-family:'Consolas',monospace;font-size:13px;white-space:pre-wrap;word-wrap:break-word;min-height:300px;">⏳ Conectando al proceso...</pre>
            <div style="padding:8px;background:#0a0a1a;border-top:1px solid #4b0082;display:flex;">
                <span style="color:#0f0;margin-right:8px;font-family:monospace;">$</span>
                <input id="term-input" style="flex:1;background:transparent;color:#0f0;border:none;outline:none;font-family:monospace;font-size:13px;" placeholder="Escribe aquí para enviar...">
            </div>
        </div>
    `;
    
    document.body.appendChild(win);
    win.style.display = 'flex';
    win.classList.add('active');
    win.style.zIndex = ++windowZIndex;
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
                    if (output) output.textContent += `\n${value}`;
                    this.value = '';
                }
            }
        };
        setTimeout(() => input.focus(), 300);
    }
    
    return win;
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
    
    if (window.termEventSource) {
        window.termEventSource.close();
        window.termEventSource = null;
    }
    
    const url = `/api/process/stream/${sessionId}`;
    const eventSource = new EventSource(url);
    window.termEventSource = eventSource;
    
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 2;
    let timeoutId = null;
    
    const resetTimeout = () => {
        if (timeoutId) clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            if (window.termEventSource) {
                window.termEventSource.close();
                window.termEventSource = null;
                output.textContent += '\n\x1b[33m⏱️ Tiempo de espera agotado\x1b[0m\n';
            }
        }, 30000);
    };
    
    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            resetTimeout();
            
            if (data.type === 'output') {
                output.textContent += data.data;
                output.scrollTop = output.scrollHeight;
            } else if (data.type === 'exit') {
                output.textContent += `\n\n\x1b[33m📋 Proceso terminado (código ${data.code || 0})\x1b[0m\n`;
                eventSource.close();
                window.termEventSource = null;
                if (timeoutId) clearTimeout(timeoutId);
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
            if (timeoutId) clearTimeout(timeoutId);
        } else if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            output.textContent += `\n\x1b[33m⚠️ Reconectando... (${reconnectAttempts}/${maxReconnectAttempts})\x1b[0m\n`;
            resetTimeout();
        } else {
            output.textContent += '\n\x1b[31m❌ Error de conexión persistente\x1b[0m\n';
            eventSource.close();
            window.termEventSource = null;
            if (timeoutId) clearTimeout(timeoutId);
        }
    };
    
    resetTimeout();
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

// ═══ NOTIFICACIONES MEJORADAS ═══
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
        padding: 14px 24px;
        border-radius: 10px;
        z-index: 10000;
        max-width: 450px;
        font-size: 14px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.6);
        animation: slideIn 0.3s ease;
        font-family: 'Segoe UI', sans-serif;
        backdrop-filter: blur(10px);
        border-left: 4px solid ${colors[type] || '#9370db'};
    `;
    div.innerHTML = `<span style="margin-right:10px;">${icons[type] || 'ℹ️'}</span> ${message}`;
    document.body.appendChild(div);
    
    setTimeout(() => {
        div.style.opacity = '0';
        div.style.transition = 'opacity 0.5s ease, transform 0.3s ease';
        div.style.transform = 'translateX(20px)';
        setTimeout(() => div.remove(), 500);
    }, 4500);
}

// ═══ EXPORTAR FUNCIONES GLOBALMENTE ═══
window.openTerminalForProcess = openTerminalForProcess;
window.closeTerminalWindow = closeTerminalWindow;
window.startTerminalStream = startTerminalStream;
window.sendTerminalInput = sendTerminalInput;
window.showNotification = showNotification;
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

// ═══ INICIALIZAR ═══
if (!fileManagerInitialized) {
    fileManagerInitialized = true;
    
    // Obtener usuario al cargar
    getCurrentUser().then(() => {
        console.log(`👤 Usuario actual: ${currentUser}`);
        if (isRoot()) {
            console.log('🔑 Modo ROOT - Eliminación permitida');
        } else {
            console.log('🔒 Modo USER - Eliminación restringida');
        }
    });
    
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(() => {
            const win = document.getElementById('win-explorer');
            if (win && win.style.display !== 'none') {
                console.log('📂 Inicializando explorador - cargando /D');
                loadFiles('/D');
            }
        }, 500);
    });
    
    const observer = new MutationObserver(() => {
        const win = document.getElementById('win-explorer');
        if (win && win.style.display !== 'none' && win.style.display !== '') {
            const grid = document.getElementById('file-grid');
            if (grid && grid.children.length === 0) {
                console.log('📂 Observador: cargando /D');
                loadFiles('/D');
            }
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    
    const styleNotif = document.createElement('style');
    styleNotif.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        .file-item {
            display: grid;
            grid-template-columns: 40px 1fr 100px 140px auto;
            gap: 10px;
            align-items: center;
            padding: 8px 12px;
            border-bottom: 1px solid rgba(75,0,130,0.15);
            transition: background 0.2s;
            cursor: default;
        }
        .file-item:hover {
            background: rgba(106,13,173,0.15);
        }
        .file-item.folder-item {
            cursor: pointer;
        }
        .file-item.folder-item:hover {
            background: rgba(106,13,173,0.2);
        }
        .file-icon {
            font-size: 22px;
            text-align: center;
        }
        .file-name {
            color: #e6e6fa;
            font-size: 13px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .file-name.dir-name {
            font-weight: 600;
            color: #da70d6;
        }
        .file-size {
            color: #9370db;
            font-size: 12px;
            text-align: right;
        }
        .file-size.dir-size {
            color: #6a0dad;
        }
        .file-modified {
            color: #6a0dad;
            font-size: 11px;
        }
        .file-actions {
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
            justify-content: flex-end;
        }
        .act.small {
            padding: 3px 8px;
            font-size: 11px;
            border-radius: 4px;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            background: rgba(75,0,130,0.3);
            color: #e6e6fa;
        }
        .act.small:hover {
            transform: scale(1.05);
            background: rgba(106,13,173,0.4);
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
        .act.small:disabled {
            opacity: 0.4;
            cursor: not-allowed;
            transform: none;
        }
        @media (max-width: 768px) {
            .file-item {
                grid-template-columns: 35px 1fr 70px auto;
                font-size: 12px;
                padding: 6px 8px;
            }
            .file-modified {
                display: none;
            }
            .file-size {
                font-size: 10px;
            }
            .file-icon {
                font-size: 18px;
            }
            .file-name {
                font-size: 12px;
            }
            .act.small {
                font-size: 9px;
                padding: 2px 5px;
            }
        }
        @media (max-width: 480px) {
            .file-item {
                grid-template-columns: 30px 1fr auto;
                gap: 5px;
            }
            .file-size {
                display: none;
            }
            .file-icon {
                font-size: 16px;
            }
            .file-name {
                font-size: 11px;
            }
        }
    `;
    document.head.appendChild(styleNotif);
}

console.log('📁 File Manager v2.0 - Solo ROOT puede eliminar');
console.log('📌 Características:');
console.log('   - Iconos por extensión');
console.log('   - Vista mejorada con columnas');
console.log('   - Solo root puede eliminar');
console.log('   - Soporte para archivos comprimidos');
console.log('   - Búsqueda mejorada');
console.log('   - Notificaciones con íconos');