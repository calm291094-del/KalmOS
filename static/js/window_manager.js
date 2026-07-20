// KALM OS v4.3 - Window Manager (OPTIMIZADO)

const windowState = {};
let windowZIndex = 1000;

// ═══ Abrir ventana ═══
function openWin(id) {
    const win = document.getElementById(`win-${id}`);
    if (!win) return;
    
    if (win.classList.contains('minimized')) {
        win.classList.remove('minimized');
    }
    
    win.style.display = 'flex';
    win.classList.add('active');
    win.style.zIndex = ++windowZIndex;
    
    updateTaskbar(id);
    
    // ═══ SI ES EL NAVEGADOR, NO CARGAR PÁGINA DE INICIO ═══
    if (id === 'browser') {
        // No hacer nada, dejar que forceLoadKalmAI maneje la carga
        return;
    }
    
    // Cargar contenido según ventana
    const loaders = {
        'explorer': () => { const grid = document.getElementById('file-grid'); if (grid && grid.children.length === 0) loadFiles('/D'); },
        'taskmgr': loadProcs,
        'dns': loadDNS,
        'proxy': loadProxy,
        'servers': loadServers,
        'pac': loadPACInfo,
        'tools': () => { if (typeof loadTools === 'function') loadTools(); },
        'games': () => { if (typeof loadGames === 'function') loadGames(); }
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
    win.classList.remove('active', 'minimized');
    
    const tbItem = document.querySelector(`.tb-window[data-win="${id}"]`);
    if (tbItem) tbItem.remove();
}

// ═══ Minimizar ventana ═══
function minimizeWin(id) {
    const win = document.getElementById(`win-${id}`);
    if (!win) return;
    
    win.classList.add('minimized');
    win.classList.remove('active');
}

// ═══ Maximizar/Restaurar ═══
function maximizeWin(id) {
    const win = document.getElementById(`win-${id}`);
    if (!win) return;
    
    win.classList.toggle('maximized');
    if (win.classList.contains('maximized')) {
        if (!win.dataset.origTop) {
            win.dataset.origTop = win.style.top;
            win.dataset.origLeft = win.style.left;
            win.dataset.origWidth = win.style.width;
            win.dataset.origHeight = win.style.height;
        }
        win.style.top = '0';
        win.style.left = '0';
        win.style.width = '100%';
        win.style.height = 'calc(100% - 50px)';
    } else {
        if (win.dataset.origTop) {
            win.style.top = win.dataset.origTop;
            win.style.left = win.dataset.origLeft;
            win.style.width = win.dataset.origWidth;
            win.style.height = win.dataset.origHeight;
        }
    }
}

// ═══ Traer al frente ═══
function bringToFront(winId) {
    const win = document.getElementById(`win-${winId}`);
    if (!win) return;
    
    win.classList.add('active');
    win.style.zIndex = ++windowZIndex;
}

// ═══ Taskbar ═══
function updateTaskbar(id) {
    const container = document.getElementById('taskbar-windows');
    if (!container) return;
    
    let tbItem = container.querySelector(`.tb-window[data-win="${id}"]`);
    
    if (!tbItem) {
        tbItem = document.createElement('div');
        tbItem.className = 'tb-window';
        tbItem.dataset.win = id;
        
        const win = document.getElementById(`win-${id}`);
        const title = win ? win.dataset.title || id : id;
        tbItem.textContent = title;
        
        tbItem.addEventListener('click', (e) => {
            e.stopPropagation();
            const winEl = document.getElementById(`win-${id}`);
            if (!winEl) return;
            
            if (winEl.classList.contains('minimized')) {
                winEl.classList.remove('minimized');
                winEl.classList.add('active');
                winEl.style.display = 'flex';
                winEl.style.zIndex = ++windowZIndex;
            } else if (winEl) {
                winEl.classList.add('active');
                winEl.style.zIndex = ++windowZIndex;
            }
        });
        
        container.appendChild(tbItem);
    }
    
    container.querySelectorAll('.tb-window').forEach(el => {
        el.classList.toggle('active', el.dataset.win === id);
    });
}

// ═══ DRAG (CORREGIDO) ═══
let dragData = null;

function startDrag(e, winId) {
    const win = document.getElementById(`win-${winId}`);
    if (!win || win.classList.contains('maximized')) return;
    
    const event = e.touches ? e.touches[0] : e;
    
    win.classList.add('active');
    win.style.zIndex = ++windowZIndex;
    
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

document.addEventListener('mousemove', (e) => {
    if (!dragData) return;
    
    const win = dragData.win;
    const x = e.clientX - dragData.offsetX;
    const y = e.clientY - dragData.offsetY;
    
    const maxX = window.innerWidth - win.offsetWidth;
    const maxY = window.innerHeight - 50 - win.offsetHeight;
    
    win.style.left = Math.max(0, Math.min(x, maxX)) + 'px';
    win.style.top = Math.max(0, Math.min(y, maxY)) + 'px';
});

document.addEventListener('mouseup', () => {
    dragData = null;
});

document.addEventListener('touchmove', (e) => {
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

document.addEventListener('touchend', () => {
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

document.addEventListener('mousemove', (e) => {
    if (!resizeData) return;
    handleResize(e.clientX, e.clientY);
});

document.addEventListener('touchmove', (e) => {
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

document.addEventListener('mouseup', () => {
    resizeData = null;
});

document.addEventListener('touchend', () => {
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

document.addEventListener('click', (e) => {
    const menu = document.getElementById('start-menu');
    const startBtn = document.getElementById('start-btn');
    if (!menu || !startBtn) return;
    
    if (!menu.contains(e.target) && !startBtn.contains(e.target)) {
        menu.style.display = 'none';
    }
});

// ═══ MONITOREO (CORREGIDO - SIN ERRORES DE RED) ═══
let monitorInterval = null;

function startMonitoring() {
    if (monitorInterval) return;
    monitorInterval = setInterval(updateStats, 2000);
    setTimeout(updateStats, 500);
}

function updateStats() {
    // Usar fetch con timeout para evitar errores de red
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    
    fetch('/api/system-stats', { signal: controller.signal })
        .then(r => {
            if (!r.ok) throw new Error('Error en respuesta');
            return r.json();
        })
        .then(data => {
            const cpuVal = document.getElementById('rm-cpu-val');
            const cpuBar = document.getElementById('rm-cpu-bar');
            if (cpuVal) cpuVal.textContent = data.cpu + '%';
            if (cpuBar) cpuBar.style.width = Math.min(data.cpu, 100) + '%';
            
            const ramVal = document.getElementById('rm-ram-val');
            const ramBar = document.getElementById('rm-ram-bar');
            if (ramVal) ramVal.textContent = `${data.ram_used} / ${data.ram_total}`;
            if (ramBar) ramBar.style.width = Math.min(data.ram_percent || 0, 100) + '%';
            
            const diskVal = document.getElementById('rm-disk-val');
            const diskBar = document.getElementById('rm-disk-bar');
            if (diskVal) diskVal.textContent = `${data.disk_used} / ${data.disk_total}`;
            if (diskBar) diskBar.style.width = Math.min(data.disk_percent || 0, 100) + '%';
            
            const procs = document.getElementById('rm-procs');
            if (procs) procs.textContent = data.processes || 0;
            
            if (data.net_upload) {
                const netUp = document.getElementById('rm-net-up');
                const netDown = document.getElementById('rm-net-down');
                const netSent = document.getElementById('rm-net-total-sent');
                const netRecv = document.getElementById('rm-net-total-recv');
                
                if (netUp) netUp.textContent = data.net_upload;
                if (netDown) netDown.textContent = data.net_download;
                if (netSent) netSent.textContent = data.net_total_sent || '0 B';
                if (netRecv) netRecv.textContent = data.net_total_recv || '0 B';
            }
        })
        .catch(err => {
            // Silenciar errores de red - no mostrar en consola
            if (err.name === 'AbortError') {
                // Timeout, ignorar
            }
        })
        .finally(() => {
            clearTimeout(timeoutId);
        });
}

document.addEventListener('DOMContentLoaded', startMonitoring);

console.log('🪟 Window Manager v2.0 - Windows 10 Style');
