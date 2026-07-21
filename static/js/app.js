// Kalm OS v4.3 - Aplicación Principal (VERSIÓN DEFINITIVA Y COMPLETA)

// ═══════════════════════════════════════════════════════════
// VARIABLES GLOBALES (Protegidas con window. para evitar redeclaración)
// ═══════════════════════════════════════════════════════════
window.bookmarksLoadedFlag = window.bookmarksLoadedFlag || false;
window.bookmarksLoading = window.bookmarksLoading || false;
window.resourceUpdateInterval = window.resourceUpdateInterval || null;
window.clockUpdateInterval = window.clockUpdateInterval || null;
window.windowZIndex = window.windowZIndex || 100;

window.TOOL_MAP = {
    'info_sistema': 'herramientas.py', 'analisis_disco': 'herramientas.py',
    'generar_hash': 'herramientas.py', 'escanear_puertos': 'herramientas.py',
    'monitor_procesos': 'herramientas.py', 'limpiar_temporales': 'herramientas.py',
    'convertir_unidades': 'conversor_unidades.py', 'generar_password': 'generador_passwords.py'
};

window.GAME_MAP = {
    'snake': 'snake.py', 'buscaminas': 'buscaminas.py', 'sokoban': 'sokoban.py',
    'blackjack': 'blackjack.py', 'ajedrez': 'ajedrez.py', 'tetris': 'tetris.py',
    'conecta4': 'conecta4.py', 'batalla_naval': 'batalla_naval.py', 'ahorcado': 'ahorcado.py',
    'gato': 'gato.py', 'piedra_papel_tijera': 'piedra_papel_tijera.py', 'memoria': 'memoria.py'
};

document.addEventListener('DOMContentLoaded', function() {
    console.log('🏰 Kalm OS v4.3 iniciado');
    fetch('/api/background-check').then(r => r.json()).then(data => {
        if (data.exists) document.body.style.backgroundImage = `url('/background?t=${Date.now()}')`;
    }).catch(() => {});
    
    updateResourceMonitor();
    if (window.resourceUpdateInterval) clearInterval(window.resourceUpdateInterval);
    window.resourceUpdateInterval = setInterval(updateResourceMonitor, 5000);
    
    updateClock();
    if (window.clockUpdateInterval) clearInterval(window.clockUpdateInterval);
    window.clockUpdateInterval = setInterval(updateClock, 1000);
    
    loadProgramMenu();
    
    document.addEventListener('click', function(e) {
        const menu = document.getElementById('start-menu');
        const startBtn = document.getElementById('start-btn');
        if (menu && startBtn && !menu.contains(e.target) && !startBtn.contains(e.target)) {
            menu.style.display = 'none';
        }
    });
});

function updateClock() {
    const clock = document.getElementById('clock');
    if (clock) clock.textContent = new Date().toLocaleTimeString('es-ES');
}

function toggleStart() {
    const menu = document.getElementById('start-menu');
    if (menu) menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
}

let isUpdating = false;
async function updateResourceMonitor() {
    if (isUpdating) return;
    isUpdating = true;
    try {
        const response = await fetch('/api/system-stats');
        if (!response.ok) { isUpdating = false; return; }
        const data = await response.json();
        
        const cpuVal = document.getElementById('rm-cpu-val'), cpuBar = document.getElementById('rm-cpu-bar');
        if (cpuVal) cpuVal.textContent = data.cpu + '%';
        if (cpuBar) cpuBar.style.width = Math.min(data.cpu, 100) + '%';
        
        const ramVal = document.getElementById('rm-ram-val'), ramBar = document.getElementById('rm-ram-bar');
        if (ramVal) ramVal.textContent = `${data.ram_used} / ${data.ram_total}`;
        if (ramBar) ramBar.style.width = Math.min(data.ram_percent, 100) + '%';
        
        const diskVal = document.getElementById('rm-disk-val'), diskBar = document.getElementById('rm-disk-bar');
        if (diskVal) diskVal.textContent = `${data.disk_used} / ${data.disk_total}`;
        if (diskBar) diskBar.style.width = Math.min(data.disk_percent, 100) + '%';
        
        const procs = document.getElementById('rm-procs');
        if (procs) procs.textContent = data.processes || 0;
        
        const netUp = document.getElementById('rm-net-up'), netDown = document.getElementById('rm-net-down');
        if (netUp) netUp.textContent = data.net_upload || '0 B/s';
        if (netDown) netDown.textContent = data.net_download || '0 B/s';
        
    } catch (error) {}
    isUpdating = false;
}

async function loadProcs() {
    try {
        const response = await fetch('/api/processes');
        if (!response.ok) return;
        const data = await response.json();
        const tbody = document.querySelector('#proc-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#9370db">No hay procesos</td></tr>';
            return;
        }
        data.forEach(p => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${p.pid}</td><td>${p.name || '?'}</td><td>${p.cpu || 0}</td><td>${p.mem || 0}</td><td>${p.status || '?'}</td><td><button class="act danger small" onclick="killProc(${p.pid})">🔪</button></td>`;
            tbody.appendChild(tr);
        });
    } catch (error) {}
}

async function killProc(pid) {
    if (!confirm(`¿Matar proceso PID ${pid}?`)) return;
    try {
        const response = await fetch(`/api/kill/${pid}`, { method: 'POST' });
        const data = await response.json();
        if (data.ok) loadProcs();
        else alert('❌ No se pudo matar el proceso');
    } catch (error) { alert('❌ Error: ' + error.message); }
}

async function loadProgramMenu() {
    const submenu = document.getElementById('program-submenu');
    if (!submenu) return;
    try {
        const response = await fetch('/api/programs');
        if (!response.ok) { submenu.innerHTML = '<div class="item" style="color:#ff6b6b">❌ Error</div>'; return; }
        const programs = await response.json();
        submenu.innerHTML = '';
        submenu.dataset.loaded = 'true';
        if (!programs || programs.length === 0) {
            submenu.innerHTML = '<div class="item" style="color:#9370db">📂 No hay programas</div>';
            return;
        }
        const categories = {};
        programs.forEach(p => {
            const cat = p.category || 'other';
            if (!categories[cat]) categories[cat] = [];
            categories[cat].push(p);
        });
        const catNames = { browser: '🌐 Navegadores', editor: '✏️ Editores', media: '🎵 Multimedia', dev: '💻 Desarrollo', server: '🚀 Servidores', office: '📄 Oficina', utility: '🔧 Utilidades', game: '🎮 Juegos', other: '📦 Otros' };
        
        for (const [cat, items] of Object.entries(categories)) {
            const header = document.createElement('div');
            header.className = 'program-category';
            header.textContent = catNames[cat] || cat;
            submenu.appendChild(header);
            items.forEach(p => {
                const item = document.createElement('div');
                item.className = 'item';
                item.textContent = `${p.icon || '📄'} ${p.name}`;
                item.onclick = function() {
                    toggleStart();
                    executeProgramFromMenu(p.path, p.name);
                };
                submenu.appendChild(item);
            });
        }
    } catch (error) {
        console.error('❌ Error cargando programas:', error);
    }
}

function executeProgramFromMenu(path, name) {
    if (typeof showNotification === 'function') showNotification(`⏳ Ejecutando ${name}...`, 'info');
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    }).then(r => r.json()).then(data => {
        if (data.ok && data.session_id) {
            if (typeof showNotification === 'function') showNotification(`✅ ${name} ejecutado`, 'success');
            if (typeof openTerminalForProcess === 'function') openTerminalForProcess(data.session_id, name);
        } else if (data.ok && data.viewer_url) {
            window.open(data.viewer_url, '_blank');
        } else {
            if (typeof showNotification === 'function') showNotification(`❌ Error: ${data.error}`, 'error');
        }
    }).catch(err => {
        if (typeof showNotification === 'function') showNotification(`❌ Error: ${err.message}`, 'error');
    });
}

// ═══════════════════════════════════════════════════════════
// KALM AI - FUNCIONES COMPLETAS (RESTAURADAS)
// ═══════════════════════════════════════════════════════════

function openKalmAI() {
    console.log('🧠 Abriendo Kalm AI...');
    if (typeof showNotification === 'function') showNotification('🧠 Abriendo Kalm AI...', 'info');
    openKalmAIBrowser();
}

function openKalmAIBrowser() {
    console.log('🌐 Abriendo navegador con Kalm AI...');
    let win = document.getElementById('win-browser');
    if (!win) {
        if (typeof openWin === 'function') openWin('browser');
        setTimeout(loadKalmAIInFrame, 500);
    } else {
        win.style.display = 'flex';
        win.classList.add('active');
        win.style.zIndex = ++window.windowZIndex;
        if (typeof updateTaskbar === 'function') updateTaskbar('browser');
        setTimeout(loadKalmAIInFrame, 300);
    }
}

function loadKalmAIInFrame() {
    console.log('🔄 Cargando Kalm AI en el frame...');
    const frame = document.getElementById('browser-frame');
    const urlInput = document.getElementById('browser-url');
    const status = document.getElementById('browser-status');
    if (!frame) { console.error('❌ Frame no encontrado'); return; }
    
    const kalmUrl = '/api/kalm/';
    if (urlInput) urlInput.value = kalmUrl;
    if (status) { status.textContent = '🧠 Cargando Kalm AI...'; status.style.color = '#ffaa00'; }
    
    frame.srcdoc = '';
    frame.src = 'about:blank';
    setTimeout(function() {
        frame.src = kalmUrl;
        console.log('✅ Frame cargado con ' + kalmUrl);
    }, 200);
    
    setTimeout(function() {
        fetch('/api/kalm/health').then(function(r) {
            if (r.ok && status) { status.textContent = '✅ Kalm AI - Listo'; status.style.color = '#00cc66'; }
        }).catch(function() {
            if (status) { status.textContent = '⚠️ Kalm AI no disponible'; status.style.color = '#ffaa00'; }
        });
    }, 3000);
}

function forceLoadKalmAI() { loadKalmAIInFrame(); }
function openChatAcademico() { openKalmAI(); }
function openKrootCorp() { openKalmAI(); }

// ═══════════════════════════════════════════════════════════
// FUNCIONES AUXILIARES Y EXPORTACIÓN
// ═══════════════════════════════════════════════════════════

function showNotification(message, type = 'info') {
    const colors = { info: '#9370db', success: '#00cc66', error: '#ff4444', warning: '#ffaa00' };
    const div = document.createElement('div');
    div.style.cssText = `position: fixed; bottom: 60px; right: 20px; background: rgba(10,5,20,0.95); border: 1px solid ${colors[type] || '#9370db'}; color: #fff; padding: 12px 20px; border-radius: 8px; z-index: 10000; max-width: 400px; font-size: 13px; box-shadow: 0 5px 20px rgba(0,0,0,0.5); font-family: 'Segoe UI', sans-serif;`;
    div.textContent = message;
    document.body.appendChild(div);
    setTimeout(() => { div.style.opacity = '0'; div.style.transition = 'opacity 0.5s'; setTimeout(() => div.remove(), 500); }, 5000);
}

function loadBrowserBookmarks() {
    const container = document.getElementById('browser-bookmarks');
    if (!container || window.bookmarksLoadedFlag || window.bookmarksLoading) return;
    window.bookmarksLoading = true;
    fetch('/api/browser/bookmarks').then(r => r.ok ? r.json() : null).then(bookmarks => {
        container.innerHTML = '';
        if (bookmarks && bookmarks.length > 0) {
            bookmarks.forEach(bm => {
                const btn = document.createElement('button');
                btn.className = 'act small';
                btn.textContent = `${bm.icon || '🌐'} ${bm.name}`;
                btn.style.cssText = 'background:rgba(75,0,130,0.3);border-color:#6a0dad;margin:2px';
                btn.onclick = function() {
                    const urlInput = document.getElementById('browser-url');
                    if (urlInput) { urlInput.value = bm.url || bm.domain; if (typeof browserNavigate === 'function') browserNavigate(); }
                };
                container.appendChild(btn);
            });
        } else { container.innerHTML = '<span style="color:#9370db;font-size:11px">📖 Sin marcadores</span>'; }
        window.bookmarksLoading = false;
        window.bookmarksLoadedFlag = true;
    }).catch(() => {
        container.innerHTML = '<span style="color:#9370db;font-size:11px">📖 Marcadores</span>';
        window.bookmarksLoading = false;
        window.bookmarksLoadedFlag = true;
    });
}

const originalOpenWin = window.openWin || function() {};
window.openWin = function(id) {
    if (typeof originalOpenWin === 'function') originalOpenWin(id);
    setTimeout(() => {
        if (id === 'taskmgr') loadProcs();
        if (id === 'browser') loadBrowserBookmarks();
    }, 300);
};

window.runTool = window.runTool || function() {};
window.runGame = window.runGame || function() {};
window.openTerminalForProcess = window.openTerminalForProcess || function() {};
window.openKalmAI = openKalmAI;
window.openChatAcademico = openChatAcademico;
window.openKrootCorp = openKrootCorp;
window.showNotification = showNotification;
window.loadKalmAIInFrame = loadKalmAIInFrame;
window.forceLoadKalmAI = forceLoadKalmAI;

console.log('🏰 Kalm OS v4.3 - Aplicación cargada correctamente');
