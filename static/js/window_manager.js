// KALM OS v4.3 - Window Manager (CORREGIDO v3.0)

const windowState = {};
let windowZIndex = 1000;

// ═══ Abrir ventana ═══
function openWin(id) {
    const win = document.getElementById(`win-${id}`);
    if (!win) return;
    
    // Si estaba minimizada, restaurar
    if (win.style.display === 'none') {
        win.style.display = 'flex';
        win.classList.remove('minimized');
    }
    
    win.classList.add('active');
    win.style.zIndex = ++windowZIndex;
    
    updateTaskbar(id);
    
    // Si es el navegador, no cargar página de inicio (lo maneja internal_browser.js)
    if (id === 'browser') return;
    
    // Cargar contenido según ventana - CON GUARDIANES PARA EVITAR ERRORES
    const loaders = {
        'explorer': () => {
            const grid = document.getElementById('file-grid');
            if (grid && grid.children.length === 0 && typeof loadFiles === 'function') loadFiles('/D');
        },
        'taskmgr': () => { if (typeof loadProcs === 'function') loadProcs(); },
        'dns': () => { if (typeof loadDNS === 'function') loadDNS(); },
        'proxy': () => { if (typeof loadProxy === 'function') loadProxy(); },
        'servers': () => { if (typeof loadServers === 'function') loadServers(); },
        'pac': () => { if (typeof loadPACInfo === 'function') loadPACInfo(); },
        'tools': () => { if (typeof loadTools === 'function') loadTools(); },
        'games': () => { if (typeof loadGames === 'function') loadGames(); },
        'music': () => { if (typeof loadMusic === 'function') loadMusic(); },
        'console': () => { /* Terminal ya está lista */ },
        'notepad': () => { /* Notepad ya está listo */ },
        'settings': () => { /* Settings ya está listo */ },
        'calc': () => { /* Calc ya está listo */ },
        'clock': () => { if (typeof startWorldClocks === 'function') startWorldClocks(); },
        'persistence': () => { if (typeof loadPersistence === 'function') loadPersistence(); }
    };
    
    if (loaders[id]) {
        setTimeout(loaders[id], 100);
    }
}

// ═══ Cerrar ventana ═══
function closeWin(id) {
    const win = document.getElementById(`win-${id}`);
    if (!win) return;
    
    win.style.display = 'none';
    win.classList.remove('active', 'minimized', 'maximized');
    
    // Limpiar dataset de maximizar
    delete win.dataset.origTop;
    delete win.dataset.origLeft;
    delete win.dataset.origWidth;
    delete win.dataset.origHeight;
    
    // Si es el navegador, limpiar iframes de pestañas
    if (id === 'browser' && typeof window.browserTabs !== 'undefined') {
        window.browserTabs.forEach(function(tab) {
            var iframe = document.getElementById('iframe-' + tab.id);
            if (iframe) { iframe.src = 'about:blank'; iframe.remove(); }
        });
        window.browserTabs = [];
        window.activeTabId = null;
    }
    
    const tbItem = document.querySelector(`.tb-window[data-win="${id}"]`);
    if (tbItem) tbItem.remove();
}

// ═══ Minimizar ventana (CORREGIDO) ═══
function minimizeWin(id) {
    const win = document.getElementById(`win-${id}`);
    if (!win) return;
    
    // Si está maximizada, restaurar ANTES de minimizar
    // Esto es crucial: si no restauras, al re-abrir se ve rota
    if (win.classList.contains('maximized')) {
        // Restaurar dimensiones guardadas
        if (win.dataset.origTop) {
            win.style.top = win.dataset.origTop;
            win.style.left = win.dataset.origLeft;
            win.style.width = win.dataset.origWidth;
            win.style.height = win.dataset.origHeight;
        }
        win.classList.remove('maximized');
        
        // Restaurar icono del botón maximizar
        const maxBtn = win.querySelector('.btn-max');
        if (maxBtn) maxBtn.textContent = '▢';
    }
    
    // Ahora sí minimizar: OCULTAR la ventana
    win.style.display = 'none';
    win.classList.add('minimized');
    win.classList.remove('active');
}

// ═══ Maximizar/Restaurar (CORREGIDO) ═══
function maximizeWin(id) {
    const win = document.getElementById(`win-${id}`);
    if (!win) return;
    
    if (win.classList.contains('maximized')) {
        // ═══ RESTAURAR ═══
        if (win.dataset.origTop) {
            win.style.top = win.dataset.origTop;
            win.style.left = win.dataset.origLeft;
            win.style.width = win.dataset.origWidth;
            win.style.height = win.dataset.origHeight;
        }
        win.classList.remove('maximized');
        
        const maxBtn = win.querySelector('.btn-max');
        if (maxBtn) maxBtn.textContent = '▢';
    } else {
        // ═══ MAXIMIZAR - Guardar estado ACTUAL primero ═══
        win.dataset.origTop = win.style.top || '0px';
        win.dataset.origLeft = win.style.left || '0px';
        win.dataset.origWidth = win.style.width || '800px';
        win.dataset.origHeight = win.style.height || '500px';
        
        win.style.top = '0';
        win.style.left = '0';
        win.style.width = '100%';
        win.style.height = 'calc(100% - 50px)';
        win.classList.add('maximized');
        
        const maxBtn = win.querySelector('.btn-max');
        if (maxBtn) maxBtn.textContent = '❐';
    }
    
    win.classList.add('active');
    win.style.zIndex = ++windowZIndex;
}

// ═══ Traer al frente ═══
function bringToFront(winId) {
    const win = document.getElementById(`win-${winId}`);
    if (!win) return;
    
    // Quitar 'active' de todas las ventanas primero
    document.querySelectorAll('.window').forEach(function(w) {
        w.classList.remove('active');
    });
    
    win.classList.add('active');
    win.style.zIndex = ++windowZIndex;
}

// ═══ Taskbar (CORREGIDO - toggle minimizar) ═══
function updateTaskbar(id) {
    const container = document.getElementById('taskbar-windows');
    if (!container) return;
    
    let tbItem = container.querySelector(`.tb-window[data-win="${id}"]`);
    
    if (!tbItem) {
        tbItem = document.createElement('div');
        tbItem.className = 'tb-window';
        tbItem.dataset.win = id;
        
        const win = document.getElementById(`win-${id}`);
        const title = win ? (win.dataset.title || id) : id;
        tbItem.textContent = title;
        
        tbItem.addEventListener('click', function(e) {
            e.stopPropagation();
            const winEl = document.getElementById(`win-${id}`);
            if (!winEl) return;
            
            if (winEl.style.display === 'none') {
                // ═══ ESTABA MINIMIZADA → RESTAURAR ═══
                winEl.style.display = 'flex';
                winEl.classList.remove('minimized');
                winEl.classList.add('active');
                winEl.style.zIndex = ++windowZIndex;
            } else if (winEl.classList.contains('active')) {
                // ═══ ESTÁ ACTIVA Y EN FOCO → MINIMIZAR ═══
                minimizeWin(id);
            } else {
                // ═══ ESTÁ VISIBLE PERO NO EN FOCO → TRAER AL FRENTE ═══
                bringToFront(id);
            }
        });
        
        container.appendChild(tbItem);
    }
    
    // Marcar como activa en la taskbar
    container.querySelectorAll('.tb-window').forEach(function(el) {
        el.classList.toggle('active', el.dataset.win === id);
    });
}

// ═══ DRAG (CORREGIDO) ═══
let dragData = null;

function startDrag(e, winId) {
    const win = document.getElementById(`win-${winId}`);
    if (!win || win.classList.contains('maximized')) return;
    
    const event = e.touches ? e.touches[0] : e;
    
    bringToFront(winId);
    
    const rect = win.getBoundingClientRect();
    
    dragData = {
        win: win,
        winId: winId,
        offsetX: event.clientX - rect.left,
        offsetY: event.clientY - rect.top,
        isTouch: !!e.touches
    };
    
    e.preventDefault();
}

document.addEventListener('mousemove', function(e) {
    if (!dragData) return;
    
    const win = dragData.win;
    const x = e.clientX - dragData.offsetX;
    const y = e.clientY - dragData.offsetY;
    
    const maxX = window.innerWidth - win.offsetWidth;
    const maxY = window.innerHeight - 50 - win.offsetHeight;
    
    win.style.left = Math.max(0, Math.min(x, maxX)) + 'px';
    win.style.top = Math.max(0, Math.min(y, maxY)) + 'px';
});

document.addEventListener('mouseup', function() {
    dragData = null;
});

document.addEventListener('touchmove', function(e) {
    if (!dragData || !dragData.isTouch) return;
    
    const touch = e.touches[0];
    const win = dragData.win;
    const x = touch.clientX - dragData.offsetX;
    const y = touch.clientY - dragData.offsetY;
    
    const maxX = window.innerWidth - win.offsetWidth;
    const maxY = window.innerHeight - 50 - win.offsetHeight;
    
    win.style.left = Math.max(0, Math.min(x, maxX)) + 'px';
    win.style.top = Math.max(0, Math.min(y, maxY)) + 'px';
    
    e.preventDefault();
}, { passive: false });

document.addEventListener('touchend', function() {
    dragData = null;
});

// ═══ RESIZE ═══
let resizeData = null;

function startResize(e, winId, direction) {
    const win = document.getElementById(`win-${winId}`);
    if (!win || win.classList.contains('maximized')) return;
    
    const event = e.touches ? e.touches[0] : e;
    const rect = win.getBoundingClientRect();
    
    resizeData = {
        win: win,
        winId: winId,
        direction: direction,
        startX: event.clientX,
        startY: event.clientY,
        startWidth: rect.width,
        startHeight: rect.height,
        startLeft: rect.left,
        startTop: rect.top,
        isTouch: !!e.touches
    };
    
    e.preventDefault();
}

document.addEventListener('mousemove', function(e) {
    if (!resizeData) return;
    handleResize(e.clientX, e.clientY);
});

document.addEventListener('touchmove', function(e) {
    if (!resizeData || !resizeData.isTouch) return;
    const touch = e.touches[0];
    handleResize(touch.clientX, touch.clientY);
    e.preventDefault();
}, { passive: false });

function handleResize(clientX, clientY) {
    const data = resizeData;
    if (!data) return;
    
    const win = data.win;
    let newWidth = data.startWidth;
    let newHeight = data.startHeight;
    let newLeft = data.startLeft;
    let newTop = data.startTop;
    
    const deltaX = clientX - data.startX;
    const deltaY = clientY - data.startY;
    
    const minWidth = 280;
    const minHeight = 200;
    
    if (data.direction.includes('e')) {
        newWidth = Math.max(minWidth, data.startWidth + deltaX);
    }
    if (data.direction.includes('w')) {
        newWidth = Math.max(minWidth, data.startWidth - deltaX);
        newLeft = data.startLeft + (data.startWidth - newWidth);
    }
    if (data.direction.includes('s')) {
        newHeight = Math.max(minHeight, data.startHeight + deltaY);
    }
    if (data.direction.includes('n')) {
        newHeight = Math.max(minHeight, data.startHeight - deltaY);
        newTop = data.startTop + (data.startHeight - newHeight);
    }
    
    const maxWidth = window.innerWidth - newLeft;
    const maxHeight = window.innerHeight - 50 - newTop;
    
    newWidth = Math.min(newWidth, maxWidth);
    newHeight = Math.min(newHeight, maxHeight);
    
    win.style.width = newWidth + 'px';
    win.style.height = newHeight + 'px';
    win.style.left = newLeft + 'px';
    win.style.top = newTop + 'px';
}

document.addEventListener('mouseup', function() {
    resizeData = null;
});

document.addEventListener('touchend', function() {
    resizeData = null;
});

// ═══ RELOJ ═══
function updateClock() {
    const clock = document.getElementById('clock');
    if (!clock) return;
    
    const now = new Date();
    clock.textContent = now.toLocaleTimeString('es-ES', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
}

setInterval(updateClock, 1000);
updateClock();

// ═══ MENÚ INICIO ═══
function toggleStart() {
    const menu = document.getElementById('start-menu');
    if (!menu) return;
    
    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
}

document.addEventListener('click', function(e) {
    const menu = document.getElementById('start-menu');
    const startBtn = document.getElementById('start-btn');
    if (!menu || !startBtn) return;
    
    if (!menu.contains(e.target) && !startBtn.contains(e.target)) {
        menu.style.display = 'none';
    }
});

// ═══ MONITOREO DE RECURSOS ═══
let monitorInterval = null;

function startMonitoring() {
    if (monitorInterval) return;
    monitorInterval = setInterval(updateStats, 2000);
    setTimeout(updateStats, 500);
}

function updateStats() {
    const controller = new AbortController();
    const timeoutId = setTimeout(function() { controller.abort(); }, 5000);
    
    fetch('/api/system-stats', { signal: controller.signal })
        .then(function(r) {
            if (!r.ok) throw new Error('Error HTTP');
            return r.json();
        })
        .then(function(data) {
            // CPU
            var cpuVal = document.getElementById('rm-cpu-val');
            var cpuBar = document.getElementById('rm-cpu-bar');
            if (cpuVal) cpuVal.textContent = data.cpu + '%';
            if (cpuBar) cpuBar.style.width = Math.min(data.cpu, 100) + '%';
            
            // RAM
            var ramVal = document.getElementById('rm-ram-val');
            var ramBar = document.getElementById('rm-ram-bar');
            if (ramVal) ramVal.textContent = (data.ram_used || '0') + ' / ' + (data.ram_total || '0');
            if (ramBar) ramBar.style.width = Math.min(data.ram_percent || 0, 100) + '%';
            
            // Disco
            var diskVal = document.getElementById('rm-disk-val');
            var diskBar = document.getElementById('rm-disk-bar');
            if (diskVal) diskVal.textContent = (data.disk_used || '0') + ' / ' + (data.disk_total || '0');
            if (diskBar) diskBar.style.width = Math.min(data.disk_percent || 0, 100) + '%';
            
            // Procesos
            var procs = document.getElementById('rm-procs');
            if (procs) procs.textContent = data.processes || 0;
            
            // Red
            if (data.net_upload) {
                var netUp = document.getElementById('rm-net-up');
                var netDown = document.getElementById('rm-net-down');
                var netSent = document.getElementById('rm-net-total-sent');
                var netRecv = document.getElementById('rm-net-total-recv');
                
                if (netUp) netUp.textContent = data.net_upload;
                if (netDown) netDown.textContent = data.net_download;
                if (netSent) netSent.textContent = data.net_total_sent || '0 B';
                if (netRecv) netRecv.textContent = data.net_total_recv || '0 B';
            }

            // Servidores
            var servers = document.getElementById('rm-servers');
            if (servers && data.servers !== undefined) servers.textContent = data.servers;
        })
        .catch(function(err) {
            if (err.name !== 'AbortError') {
                // Silenciar otros errores de red
            }
        })
        .finally(function() {
            clearTimeout(timeoutId);
        });
}

document.addEventListener('DOMContentLoaded', startMonitoring);

console.log('🪟 Window Manager v3.0 (Corregido)');
