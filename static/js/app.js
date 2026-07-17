// Kalm OS v4.3 - Aplicación Principal (VERSIÓN OPTIMIZADA)

// ═══════════════════════════════════════════════════════════
// VARIABLES GLOBALES
// ═══════════════════════════════════════════════════════════

let bookmarksLoadedFlag = false;
let bookmarksLoading = false;
let resourceUpdateInterval = null;
let clockUpdateInterval = null;
// windowZIndex ya está declarado en window_manager.js - NO redeclarar

// ═══════════════════════════════════════════════════════════
// CONSTANTES - MAPAS GLOBALES
// ═══════════════════════════════════════════════════════════

window.TOOL_MAP = {
    'info_sistema': 'herramientas.py',
    'analisis_disco': 'herramientas.py',
    'generar_hash': 'herramientas.py',
    'escanear_puertos': 'herramientas.py',
    'monitor_procesos': 'herramientas.py',
    'limpiar_temporales': 'herramientas.py',
    'convertir_unidades': 'conversor_unidades.py',
    'generar_password': 'generador_passwords.py'
};

window.GAME_MAP = {
    'snake': 'snake.py',
    'buscaminas': 'buscaminas.py',
    'sokoban': 'sokoban.py',
    'blackjack': 'blackjack.py',
    'ajedrez': 'ajedrez.py',
    'tetris': 'tetris.py',
    'conecta4': 'conecta4.py',
    'batalla_naval': 'batalla_naval.py',
    'ahorcado': 'ahorcado.py',
    'gato': 'gato.py',
    'piedra_papel_tijera': 'piedra_papel_tijera.py',
    'memoria': 'memoria.py'
};

// ═══════════════════════════════════════════════════════════
// INICIALIZACIÓN
// ═══════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', function() {
    console.log('🏰 Kalm OS v4.3 iniciado');
    
    // Cargar wallpaper
    fetch('/api/background-check')
        .then(r => r.json())
        .then(data => {
            if (data.exists) {
                document.body.style.backgroundImage = `url('/background?t=${Date.now()}')`;
            }
        })
        .catch(() => {});
    
    // Iniciar monitor de recursos (intervalo más largo para rendimiento)
    updateResourceMonitor();
    if (resourceUpdateInterval) clearInterval(resourceUpdateInterval);
    resourceUpdateInterval = setInterval(updateResourceMonitor, 5000);
    
    // Iniciar reloj
    updateClock();
    if (clockUpdateInterval) clearInterval(clockUpdateInterval);
    clockUpdateInterval = setInterval(updateClock, 1000);
    
    // Cargar menú de programas
    loadProgramMenu();
    
    // Cerrar menú al hacer clic fuera
    document.addEventListener('click', function(e) {
        const menu = document.getElementById('start-menu');
        const startBtn = document.getElementById('start-btn');
        if (menu && startBtn && !menu.contains(e.target) && !startBtn.contains(e.target)) {
            menu.style.display = 'none';
        }
    });
});

// ═══════════════════════════════════════════════════════════
// RELOJ
// ═══════════════════════════════════════════════════════════

function updateClock() {
    const clock = document.getElementById('clock');
    if (clock) {
        clock.textContent = new Date().toLocaleTimeString('es-ES');
    }
}

// ═══════════════════════════════════════════════════════════
// MENÚ INICIO
// ═══════════════════════════════════════════════════════════

function toggleStart() {
    const menu = document.getElementById('start-menu');
    if (menu) {
        menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
    }
}

// ═══════════════════════════════════════════════════════════
// MONITOR DE RECURSOS (OPTIMIZADO)
// ═══════════════════════════════════════════════════════════

let isUpdating = false;

async function updateResourceMonitor() {
    if (isUpdating) return;
    isUpdating = true;
    
    try {
        const response = await fetch('/api/system-stats');
        if (!response.ok) {
            isUpdating = false;
            return;
        }
        const data = await response.json();
        
        // CPU
        const cpuVal = document.getElementById('rm-cpu-val');
        const cpuBar = document.getElementById('rm-cpu-bar');
        if (cpuVal) cpuVal.textContent = data.cpu + '%';
        if (cpuBar) cpuBar.style.width = Math.min(data.cpu, 100) + '%';
        
        // RAM
        const ramVal = document.getElementById('rm-ram-val');
        const ramBar = document.getElementById('rm-ram-bar');
        if (ramVal) ramVal.textContent = `${data.ram_used} / ${data.ram_total}`;
        if (ramBar) ramBar.style.width = Math.min(data.ram_percent, 100) + '%';
        
        // Disco
        const diskVal = document.getElementById('rm-disk-val');
        const diskBar = document.getElementById('rm-disk-bar');
        if (diskVal) diskVal.textContent = `${data.disk_used} / ${data.disk_total}`;
        if (diskBar) diskBar.style.width = Math.min(data.disk_percent, 100) + '%';
        
        // Procesos
        const procs = document.getElementById('rm-procs');
        if (procs) procs.textContent = data.processes || 0;
        
        // Red
        const netUp = document.getElementById('rm-net-up');
        const netDown = document.getElementById('rm-net-down');
        const netSent = document.getElementById('rm-net-total-sent');
        const netRecv = document.getElementById('rm-net-total-recv');
        const netUpBar = document.getElementById('rm-net-up-bar');
        const netDownBar = document.getElementById('rm-net-down-bar');
        
        if (netUp) netUp.textContent = data.net_upload || '0 B/s';
        if (netDown) netDown.textContent = data.net_download || '0 B/s';
        if (netSent) netSent.textContent = data.net_total_sent || '0 B';
        if (netRecv) netRecv.textContent = data.net_total_recv || '0 B';
        
        if (netUpBar && netDownBar) {
            const upRaw = data.net_upload_raw || 0;
            const downRaw = data.net_download_raw || 0;
            const maxSpeed = Math.max(upRaw, downRaw, 1024);
            const upPercent = Math.min((Math.log(upRaw + 1) / Math.log(maxSpeed + 1)) * 100, 100);
            const downPercent = Math.min((Math.log(downRaw + 1) / Math.log(maxSpeed + 1)) * 100, 100);
            netUpBar.style.width = upPercent + '%';
            netDownBar.style.width = downPercent + '%';
        }
        
        // Servidores
        try {
            const sr = await fetch('/api/running-procs');
            if (sr.ok) {
                const sd = await sr.json();
                const servers = document.getElementById('rm-servers');
                if (servers) servers.textContent = sd.length || 0;
            }
        } catch (e) {}
        
    } catch (error) {
        // Silenciar errores de red
    }
    isUpdating = false;
}

// ═══════════════════════════════════════════════════════════
// TASK MANAGER
// ═══════════════════════════════════════════════════════════

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
            tr.innerHTML = `
                <td>${p.pid}</td>
                <td>${p.name || '?'}</td>
                <td>${p.cpu || 0}</td>
                <td>${p.mem || 0}</td>
                <td>${p.status || '?'}</td>
                <td><button class="act danger small" onclick="killProc(${p.pid})">🔪</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        // Silenciar errores
    }
}

async function killProc(pid) {
    if (!confirm(`¿Matar proceso PID ${pid}?`)) return;
    
    try {
        const response = await fetch(`/api/kill/${pid}`, { method: 'POST' });
        const data = await response.json();
        if (data.ok) {
            loadProcs();
        } else {
            alert('❌ No se pudo matar el proceso');
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

// ═══════════════════════════════════════════════════════════
// DNS ADMIN
// ═══════════════════════════════════════════════════════════

async function loadDNS() {
    try {
        const response = await fetch('/api/dns');
        if (!response.ok) return;
        const data = await response.json();
        const tbody = document.querySelector('#dns-table tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        const rules = data.rules || {};
        
        if (Object.keys(rules).length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:#9370db">Sin reglas DNS</td></tr>';
            return;
        }
        
        for (const [domain, ip] of Object.entries(rules)) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${domain}</td>
                <td>${ip}</td>
                <td><button class="act danger small" onclick="removeDNS('${domain.replace(/'/g, "\\'")}')">🗑️</button></td>
            `;
            tbody.appendChild(tr);
        }
    } catch (error) {
        // Silenciar errores
    }
}

async function addDNS() {
    const domain = document.getElementById('dns-dom')?.value.trim();
    const ip = document.getElementById('dns-ip')?.value.trim();
    
    if (!domain || !ip) {
        alert('❌ Dominio e IP son requeridos');
        return;
    }
    
    try {
        const response = await fetch('/api/dns', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ domain, ip })
        });
        const data = await response.json();
        
        if (data.ok) {
            if (document.getElementById('dns-dom')) document.getElementById('dns-dom').value = '';
            if (document.getElementById('dns-ip')) document.getElementById('dns-ip').value = '';
            loadDNS();
        } else {
            alert('❌ Error: ' + (data.error || 'desconocido'));
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

async function removeDNS(domain) {
    if (!confirm(`¿Eliminar DNS "${domain}"?`)) return;
    
    try {
        const response = await fetch(`/api/dns/${encodeURIComponent(domain)}`, { method: 'DELETE' });
        const data = await response.json();
        if (data.ok) {
            loadDNS();
        } else {
            alert('❌ Error eliminando DNS');
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

// ═══════════════════════════════════════════════════════════
// PROXY ADMIN
// ═══════════════════════════════════════════════════════════

async function loadProxy() {
    try {
        const response = await fetch('/api/proxy');
        if (!response.ok) return;
        const data = await response.json();
        const tbody = document.querySelector('#proxy-table tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        const rules = data.rules || {};
        
        if (Object.keys(rules).length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:#9370db">Sin reglas de proxy</td></tr>';
            return;
        }
        
        for (const [domain, backend] of Object.entries(rules)) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${domain}</td>
                <td>${backend}</td>
                <td><button class="act danger small" onclick="removeProxy('${domain.replace(/'/g, "\\'")}')">🗑️</button></td>
            `;
            tbody.appendChild(tr);
        }
    } catch (error) {
        // Silenciar errores
    }
}

async function addProxy() {
    const domain = document.getElementById('proxy-dom')?.value.trim();
    const backend = document.getElementById('proxy-back')?.value.trim();
    
    if (!domain || !backend) {
        alert('❌ Dominio y backend son requeridos');
        return;
    }
    
    try {
        const response = await fetch('/api/proxy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ domain, backend })
        });
        const data = await response.json();
        
        if (data.ok) {
            if (document.getElementById('proxy-dom')) document.getElementById('proxy-dom').value = '';
            if (document.getElementById('proxy-back')) document.getElementById('proxy-back').value = '';
            loadProxy();
            generatePAC();
        } else {
            alert('❌ Error: ' + (data.error || 'desconocido'));
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

async function removeProxy(domain) {
    if (!confirm(`¿Eliminar proxy "${domain}"?`)) return;
    
    try {
        const response = await fetch(`/api/proxy/${encodeURIComponent(domain)}`, { method: 'DELETE' });
        const data = await response.json();
        if (data.ok) {
            loadProxy();
            generatePAC();
        } else {
            alert('❌ Error eliminando regla');
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

// ═══════════════════════════════════════════════════════════
// SERVIDORES / PROCESOS ACTIVOS
// ═══════════════════════════════════════════════════════════

async function loadServers() {
    try {
        const response = await fetch('/api/running-procs');
        if (!response.ok) return;
        const data = await response.json();
        const tbody = document.querySelector('#srv-table tbody');
        const info = document.getElementById('srv-info');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#9370db">No hay procesos en ejecución</td></tr>';
            if (info) info.textContent = '💤 Sin procesos';
            return;
        }
        
        data.forEach(p => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${p.pid}</td>
                <td>${p.name || '?'}</td>
                <td>${p.type || 'programa'}</td>
                <td>${p.isolated ? '🔒 Sí' : '🔓 No'}</td>
                <td>${p.children_count || 0}</td>
                <td>${p.started ? new Date(p.started).toLocaleString() : '-'}</td>
                <td><button class="act danger small" onclick="stopProcess(${p.pid})">⏹</button></td>
            `;
            tbody.appendChild(tr);
        });
        
        if (info) {
            info.textContent = `🟢 ${data.length} procesos activos`;
        }
    } catch (error) {
        // Silenciar errores
    }
}

async function stopProcess(pid) {
    if (!confirm(`¿Detener proceso PID ${pid}?`)) return;
    
    try {
        const response = await fetch(`/api/stop-proc/${pid}`, { method: 'POST' });
        const data = await response.json();
        if (data.ok) {
            loadServers();
        } else {
            alert('❌ Error: ' + (data.message || 'desconocido'));
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

async function stopAllServers() {
    if (!confirm('⚠️ ¿Detener TODOS los procesos en ejecución?')) return;
    
    try {
        const response = await fetch('/api/stop-all', { method: 'POST' });
        const data = await response.json();
        if (data.ok) {
            alert(`✅ ${data.stopped} proceso(s) detenido(s)`);
            loadServers();
        } else {
            alert('❌ Error deteniendo procesos');
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

// ═══════════════════════════════════════════════════════════
// SCRIPT RUNNER
// ═══════════════════════════════════════════════════════════

async function runScript() {
    const pathInput = document.getElementById('script-path');
    const output = document.getElementById('script-out');
    
    if (!pathInput || !output) return;
    
    const path = pathInput.value.trim();
    if (!path) {
        alert('❌ Ingresa la ruta del archivo');
        return;
    }
    
    output.textContent = '⏳ Ejecutando...';
    
    try {
        const response = await fetch('/api/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: path })
        });
        const data = await response.json();
        
        if (data.ok) {
            if (data.viewer_url) {
                output.textContent = `📄 ${path.split('/').pop()} abierto en visor\n\n🔗 ${data.viewer_url}`;
                window.open(data.viewer_url, '_blank');
            } else if (data.session_id) {
                output.textContent = `✅ ${path.split('/').pop()} ejecutado\nPID: ${data.pid}\nSession: ${data.session_id}\n\n📤 Salida en tiempo real en la terminal virtual`;
                if (typeof openTerminalForProcess === 'function') {
                    openTerminalForProcess(data.session_id, path.split('/').pop());
                }
                loadServers();
            } else if (data.stdout) {
                output.textContent = data.stdout;
            } else {
                output.textContent = data.message || '✅ Ejecutado correctamente';
            }
        } else {
            output.textContent = '❌ Error: ' + (data.error || 'desconocido');
        }
    } catch (error) {
        output.textContent = '❌ Error de conexión: ' + error.message;
    }
}

async function runScriptDirect() {
    const pathInput = document.getElementById('script-path');
    const output = document.getElementById('script-out');
    
    if (!pathInput || !output) return;
    
    const path = pathInput.value.trim();
    if (!path) {
        alert('❌ Ingresa la ruta del archivo');
        return;
    }
    
    output.textContent = '⏳ Ejecutando en modo directo...';
    
    try {
        const response = await fetch('/api/run-direct', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: path })
        });
        const data = await response.json();
        
        if (data.ok) {
            if (data.stdout) {
                output.textContent = data.stdout;
            } else {
                output.textContent = data.message || '✅ Ejecutado correctamente';
            }
        } else {
            output.textContent = '❌ Error: ' + (data.error || 'desconocido');
        }
    } catch (error) {
        output.textContent = '❌ Error de conexión: ' + error.message;
    }
}

async function viewLastLog() {
    const output = document.getElementById('script-out');
    if (!output) return;
    
    output.textContent = '⏳ Cargando log...';
    
    try {
        const response = await fetch('/api/last-log');
        const data = await response.json();
        
        if (data.ok && data.content) {
            output.textContent = data.content;
        } else {
            output.textContent = '📋 No hay logs disponibles';
        }
    } catch (error) {
        output.textContent = '❌ Error cargando log: ' + error.message;
    }
}

// ═══════════════════════════════════════════════════════════
// MENÚ DE PROGRAMAS
// ═══════════════════════════════════════════════════════════

async function loadProgramMenu() {
    const submenu = document.getElementById('program-submenu');
    if (!submenu) return;
    
    try {
        console.log('📂 Cargando programas desde /api/programs...');
        const response = await fetch('/api/programs');
        if (!response.ok) {
            console.error('❌ Error en /api/programs:', response.status);
            submenu.innerHTML = '<div class="item" style="color:#ff6b6b">❌ Error cargando programas</div>';
            return;
        }
        const programs = await response.json();
        console.log(`📂 ${programs.length} programas cargados:`, programs.map(p => p.name));
        
        submenu.innerHTML = '';
        submenu.dataset.loaded = 'true';
        
        if (!programs || programs.length === 0) {
            submenu.innerHTML = '<div class="item" style="color:#9370db;font-style:italic">📂 No hay programas en system/program/</div>';
            console.warn('⚠️ No hay programas en system/program/');
            return;
        }
        
        const categories = {};
        programs.forEach(p => {
            const cat = p.category || 'other';
            if (!categories[cat]) categories[cat] = [];
            categories[cat].push(p);
        });
        
        const catNames = {
            browser: '🌐 Navegadores',
            editor: '✏️ Editores',
            media: '🎵 Multimedia',
            dev: '💻 Desarrollo',
            server: '🚀 Servidores',
            office: '📄 Oficina',
            utility: '🔧 Utilidades',
            game: '🎮 Juegos',
            other: '📦 Otros'
        };
        
        for (const [cat, items] of Object.entries(categories)) {
            const header = document.createElement('div');
            header.className = 'program-category';
            header.textContent = catNames[cat] || cat;
            submenu.appendChild(header);
            
            items.forEach(p => {
                const item = document.createElement('div');
                item.className = 'item';
                const icon = p.icon || '📄';
                item.textContent = `${icon} ${p.name}`;
                item.title = `${p.filename}\n${p.relative_path}`;
                item.onclick = function() {
                    console.log(`▶️ Ejecutando programa: ${p.path}`);
                    toggleStart();
                    executeProgramFromMenu(p.path, p.name);
                };
                submenu.appendChild(item);
            });
        }
        
        console.log('✅ Menú de programas cargado correctamente');
        
    } catch (error) {
        console.error('❌ Error cargando programas:', error);
        submenu.innerHTML = '<div class="item" style="color:#ff6b6b">❌ Error cargando programas</div>';
    }
}

function toggleProgramMenu() {
    const submenu = document.getElementById('program-submenu');
    if (!submenu) return;
    
    if (submenu.style.display === 'block') {
        submenu.style.display = 'none';
    } else {
        submenu.style.display = 'block';
        if (!submenu.dataset.loaded) {
            loadProgramMenu();
        }
    }
}

// ═══ EJECUTAR PROGRAMA DESDE EL MENÚ ═══
function executeProgramFromMenu(path, name) {
    toggleStart();
    
    if (typeof showNotification === 'function') {
        showNotification(`⏳ Ejecutando ${name}...`, 'info');
    }
    
    // Abrir terminal inmediatamente para feedback visual
    let terminalOpened = false;
    
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    })
    .then(r => r.json())
    .then(data => {
        console.log('📤 Respuesta de /api/run:', data);
        
        if (data.ok && data.stdout) {
            // Script terminó rápido, mostrar salida
            if (typeof showNotification === 'function') {
                showNotification(`✅ ${name} ejecutado correctamente`, 'success');
            }
            const output = document.getElementById('script-out');
            if (output) output.textContent = data.stdout;
            openWin('runner');
        } else if (data.ok && data.session_id) {
            // Script en ejecución - abrir terminal
            if (typeof showNotification === 'function') {
                showNotification(`✅ ${name} ejecutado (PID ${data.pid})`, 'success');
            }
            
            // Abrir terminal solo una vez
            if (!terminalOpened && typeof openTerminalForProcess === 'function') {
                terminalOpened = true;
                openTerminalForProcess(data.session_id, name);
            }
            
            if (typeof loadServers === 'function') loadServers();
        } else if (data.ok && data.viewer_url) {
            window.open(data.viewer_url, '_blank');
            if (typeof showNotification === 'function') {
                showNotification(`📄 ${name} abierto en visor`, 'success');
            }
        } else {
            if (typeof showNotification === 'function') {
                showNotification(`❌ Error: ${data.error || 'desconocido'}`, 'error');
            }
            openWin('runner');
            const output = document.getElementById('script-out');
            if (output) output.textContent = `❌ Error: ${data.error || 'desconocido'}`;
        }
    })
    .catch(err => {
        if (typeof showNotification === 'function') {
            showNotification(`❌ Error: ${err.message}`, 'error');
        }
        const output = document.getElementById('script-out');
        if (output) output.textContent = `❌ Error de conexión: ${err.message}`;
        openWin('runner');
    });
}

// ═══════════════════════════════════════════════════════════
// KrootCorp
// ═══════════════════════════════════════════════════════════
// ═══ KROOT CORP - CORREGIDO PARA RENDER ═══
function openKrootCorp() {
    console.log('🏢 Abriendo Kroot Corp IA...');
    
    if (typeof showNotification === 'function') {
        showNotification('🏢 Abriendo Kroot Corp IA...', 'info');
    }
    
    // Usar el proxy de Kalm OS en lugar de localhost:8000
    const krootUrl = '/api/kroot/dashboard';
    
    // Abrir el navegador interno
    openWin('browser');
    
    setTimeout(() => {
        const urlInput = document.getElementById('browser-url');
        if (urlInput) {
            urlInput.value = krootUrl;
            if (typeof browserNavigate === 'function') {
                browserNavigate();
            }
        }
    }, 1500);
    
    // Intentar iniciar Kroot Corp en segundo plano
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            path: 'system/Program/kroot_corp/run.py',
            args: ['--no-browser']
        })
    })
    .then(r => r.json())
    .then(data => {
        console.log('📤 Respuesta Kroot Corp:', data);
        if (data.ok) {
            if (typeof showNotification === 'function') {
                showNotification('✅ Kroot Corp IA iniciado', 'success');
            }
        }
    })
    .catch(err => {
        console.warn('⚠️ Error iniciando Kroot Corp:', err);
        // Si no se puede iniciar, mostrar mensaje
        if (typeof showNotification === 'function') {
            showNotification('⚠️ Kroot Corp no disponible. Usando proxy.', 'warning');
        }
        // Intentar cargar desde el proxy de todos modos
        setTimeout(() => {
            const urlInput = document.getElementById('browser-url');
            if (urlInput) {
                urlInput.value = '/api/kroot/dashboard';
                if (typeof browserNavigate === 'function') {
                    browserNavigate();
                }
            }
        }, 1000);
    });
}

// Exportar función globalmente
window.openKrootCorp = openKrootCorp;

// ═══════════════════════════════════════════════════════════
// PAC CONFIGURATION
// ═══════════════════════════════════════════════════════════

async function loadPACInfo() {
    try {
        const response = await fetch('/api/pac-info');
        if (!response.ok) return;
        const data = await response.json();
        
        const infoDiv = document.getElementById('pac-info');
        const instrDiv = document.getElementById('pac-instructions');
        
        if (!data.ok || !infoDiv) {
            if (infoDiv) infoDiv.innerHTML = `<span style="color:#f44">❌ ${data.error || 'Error cargando PAC'}</span>`;
            return;
        }
        
        infoDiv.innerHTML = `
            <div style="margin-bottom:10px">
                <b style="color:#da70d6">📄 Archivo PAC:</b><br>
                <code style="background:#0a0514;padding:8px;border-radius:4px;color:#0f0;word-break:break-all;display:block;margin-top:5px;font-size:12px">${data.pac_url}</code>
            </div>
            <div style="font-size:11px;color:#9370db">
                💡 Copia esta URL y configúrala en tu navegador como proxy automático.
            </div>
        `;
        
        if (instrDiv && data.instructions) {
            instrDiv.innerHTML = '';
            
            const browsers = [
                {name: 'Firefox', key: 'firefox', icon: '🦊'},
                {name: 'Chrome', key: 'chrome', icon: '🌐'},
                {name: 'Edge', key: 'edge', icon: '📘'}
            ];
            
            browsers.forEach(b => {
                const steps = data.instructions[b.key]?.steps || [];
                const div = document.createElement('div');
                div.style.cssText = 'background:rgba(26,0,51,0.5);padding:10px;border-radius:5px;margin-bottom:8px;border:1px solid #4b0082';
                div.innerHTML = `
                    <h4 style="color:#da70d6;margin-bottom:5px;font-size:13px">${b.icon} ${b.name}</h4>
                    <ol style="margin-left:20px;font-size:11px;color:#d8bfd8">
                        ${steps.map(s => `<li style="margin:2px 0">${s}</li>`).join('')}
                    </ol>
                `;
                instrDiv.appendChild(div);
            });
        }
        
        loadProxyLog();
        
    } catch (error) {
        console.error('Error cargando PAC:', error);
    }
}

async function generatePAC() {
    try {
        const response = await fetch('/api/pac/generate', { method: 'POST' });
        const data = await response.json();
        if (data.ok) {
            alert('✅ PAC regenerado correctamente');
            loadPACInfo();
        } else {
            alert('❌ Error: ' + (data.error || 'desconocido'));
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

async function loadProxyLog() {
    try {
        const response = await fetch('/api/proxy-log');
        if (!response.ok) return;
        const logs = await response.json();
        const logDiv = document.getElementById('proxy-log');
        if (!logDiv) return;
        
        if (!logs || logs.length === 0) {
            logDiv.textContent = '📋 Sin actividad en el proxy';
            return;
        }
        
        let text = '';
        logs.slice().reverse().forEach(l => {
            const time = l.time ? l.time.split('T')[1]?.split('.')[0] || '--:--:--' : '--:--:--';
            const status = l.status < 400 ? '✅' : (l.status < 500 ? '⚠️' : '❌');
            text += `[${time}] ${status} ${l.method || '?'} ${l.host || '?'}${l.path || ''} → ${l.status || '?'} (${l.size || 0}b)\n`;
        });
        logDiv.textContent = text || '📋 Sin actividad';
        
    } catch (error) {
        console.error('Error cargando log proxy:', error);
    }
}

async function clearProxyLog() {
    if (!confirm('¿Limpiar el log del proxy?')) return;
    
    try {
        await fetch('/api/proxy/clear-log', { method: 'POST' });
        loadProxyLog();
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

// ═══════════════════════════════════════════════════════════
// WALLPAPER
// ═══════════════════════════════════════════════════════════

async function uploadBg() {
    const input = document.getElementById('bg-file');
    if (!input || !input.files || input.files.length === 0) {
        alert('❌ Selecciona una imagen');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', input.files[0]);
    
    try {
        const response = await fetch('/api/background', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        if (data.ok) {
            alert('✅ Wallpaper actualizado');
            document.body.style.backgroundImage = `url('/background?t=${Date.now()}')`;
        } else {
            alert('❌ Error subiendo wallpaper');
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

// ═══════════════════════════════════════════════════════════
// LOGOUT / SHUTDOWN
// ═══════════════════════════════════════════════════════════

async function logout() {
    if (!confirm('¿Cerrar sesión?')) return;
    
    try {
        await fetch('/api/logout', { method: 'POST' });
        document.cookie = 'session_id=; path=/; max-age=0';
        window.location.href = '/';
    } catch (error) {
        window.location.href = '/';
    }
}

async function shutdown() {
    if (!confirm('⚠️ ¿Apagar Kalm OS?\n\nSe detendrán todos los servicios.')) return;
    
    try {
        await fetch('/api/shutdown', { method: 'POST' });
        document.body.innerHTML = `
            <div style="display:flex;justify-content:center;align-items:center;height:100vh;flex-direction:column;background:#0a0514;color:#da70d6;font-family:sans-serif">
                <div style="font-size:64px;margin-bottom:20px">🏰</div>
                <div style="font-size:24px">Kalm OS - Apagando...</div>
                <div style="font-size:14px;color:#9370db;margin-top:10px">El servidor se detendrá en breve</div>
            </div>
        `;
    } catch (error) {
        alert('❌ Error apagando: ' + error.message);
    }
}

// ═══════════════════════════════════════════════════════════
// NAVEGADOR INTERNO (BOOKMARKS)
// ═══════════════════════════════════════════════════════════

function loadBrowserBookmarks() {
    const container = document.getElementById('browser-bookmarks');
    if (!container) return;
    
    if (bookmarksLoadedFlag) return;
    if (bookmarksLoading) return;
    bookmarksLoading = true;
    
    fetch('/api/browser/bookmarks')
        .then(r => {
            if (!r.ok) {
                container.innerHTML = '<span style="color:#9370db;font-size:11px">📖 Marcadores</span>';
                bookmarksLoading = false;
                bookmarksLoadedFlag = true;
                return;
            }
            return r.json();
        })
        .then(bookmarks => {
            container.innerHTML = '';
            
            if (bookmarks && bookmarks.length > 0) {
                bookmarks.forEach(bm => {
                    const btn = document.createElement('button');
                    btn.className = 'act small';
                    btn.textContent = `${bm.icon || '🌐'} ${bm.name}`;
                    btn.style.cssText = 'background:rgba(75,0,130,0.3);border-color:#6a0dad;margin:2px';
                    btn.onclick = function() {
                        const urlInput = document.getElementById('browser-url');
                        if (urlInput) {
                            urlInput.value = bm.url || bm.domain;
                            browserNavigate();
                        }
                    };
                    container.appendChild(btn);
                });
            } else {
                container.innerHTML = '<span style="color:#9370db;font-size:11px">📖 Sin marcadores</span>';
            }
            bookmarksLoading = false;
            bookmarksLoadedFlag = true;
        })
        .catch(err => {
            console.error('Error cargando bookmarks:', err);
            container.innerHTML = '<span style="color:#9370db;font-size:11px">📖 Marcadores</span>';
            bookmarksLoading = false;
            bookmarksLoadedFlag = true;
        });
}

// ═══════════════════════════════════════════════════════════
// FUNCIONES DE VENTANAS ADICIONALES
// ═══════════════════════════════════════════════════════════

function openTools() {
    openWin('tools');
}

function openGames() {
    openWin('games');
}

function openMusic() {
    openWin('music');
}

function openCalculator() {
    openWin('calc');
}

function openNotepad() {
    openWin('notepad');
}

function openWorldClock() {
    openWin('clock');
}

// ═══════════════════════════════════════════════════════════
// INICIALIZACIÓN DE VENTANAS
// ═══════════════════════════════════════════════════════════

const originalOpenWin = window.openWin || function() {};

window.openWin = function(id) {
    if (typeof originalOpenWin === 'function') {
        originalOpenWin(id);
    }
    
    setTimeout(() => {
        switch(id) {
            case 'taskmgr':
                loadProcs();
                break;
            case 'dns':
                loadDNS();
                break;
            case 'proxy':
                loadProxy();
                break;
            case 'servers':
                loadServers();
                break;
            case 'pac':
                loadPACInfo();
                break;
            case 'browser':
                loadBrowserBookmarks();
                break;
            case 'tools':
                if (typeof loadTools === 'function') loadTools();
                break;
            case 'games':
                if (typeof loadGames === 'function') loadGames();
                break;
        }
    }, 300);
};

// ═══════════════════════════════════════════════════════════
// FUNCIONES PARA CALCULADORA
// ═══════════════════════════════════════════════════════════

if (typeof window.calcDisplay === 'undefined') {
    window.calcDisplay = '';
    window.calcMemory = 0;
    window.calcOperator = '';
    window.calcNewNumber = true;
}

function calcInput(value) {
    const display = document.getElementById('calc-display');
    if (!display) return;
    
    if (value === 'C') {
        window.calcDisplay = '';
        window.calcOperator = '';
        window.calcNewNumber = true;
        display.value = '0';
        return;
    }
    
    if (value === '±') {
        if (window.calcDisplay.startsWith('-')) {
            window.calcDisplay = window.calcDisplay.substring(1);
        } else if (window.calcDisplay !== '0' && window.calcDisplay !== '') {
            window.calcDisplay = '-' + window.calcDisplay;
        }
        display.value = window.calcDisplay || '0';
        return;
    }
    
    if (value === 'sqrt') {
        try {
            const num = parseFloat(window.calcDisplay) || 0;
            if (num < 0) {
                display.value = 'Error';
                window.calcDisplay = '';
                return;
            }
            const result = Math.sqrt(num);
            window.calcDisplay = result.toString();
            display.value = window.calcDisplay;
            window.calcNewNumber = true;
        } catch(e) {
            display.value = 'Error';
            window.calcDisplay = '';
        }
        return;
    }
    
    if (['+', '-', '*', '/'].includes(value)) {
        if (!window.calcNewNumber && window.calcDisplay) {
            calcResult();
        }
        window.calcOperator = value;
        window.calcMemory = parseFloat(window.calcDisplay) || 0;
        window.calcNewNumber = true;
        display.value = window.calcDisplay + ' ' + value;
        return;
    }
    
    if (value === '=') {
        calcResult();
        return;
    }
    
    if (window.calcNewNumber) {
        window.calcDisplay = (value === '.' ? '0.' : value);
        window.calcNewNumber = false;
    } else {
        if (value === '.' && window.calcDisplay.includes('.')) return;
        window.calcDisplay += value;
    }
    display.value = window.calcDisplay;
}

function calcResult() {
    const display = document.getElementById('calc-display');
    if (!display) return;
    
    if (!window.calcOperator) {
        display.value = window.calcDisplay || '0';
        return;
    }
    
    const current = parseFloat(window.calcDisplay) || 0;
    let result = 0;
    
    switch(window.calcOperator) {
        case '+': result = window.calcMemory + current; break;
        case '-': result = window.calcMemory - current; break;
        case '*': result = window.calcMemory * current; break;
        case '/': 
            if (current === 0) {
                display.value = 'Error';
                window.calcDisplay = '';
                window.calcOperator = '';
                return;
            }
            result = window.calcMemory / current; 
            break;
        default: result = current;
    }
    
    window.calcDisplay = result.toString();
    display.value = window.calcDisplay;
    window.calcOperator = '';
    window.calcNewNumber = true;
}

// ═══════════════════════════════════════════════════════════
// FUNCIONES PARA NOTEPAD
// ═══════════════════════════════════════════════════════════

function notepadSave() {
    const content = document.getElementById('notepad-content');
    const status = document.getElementById('notepad-status');
    if (!content || !status) return;
    
    const name = prompt('Nombre del archivo:', 'nota.txt');
    if (name) {
        localStorage.setItem('kalm_notepad_' + name, content.value);
        status.textContent = '✅ Guardado: ' + name;
        setTimeout(() => status.textContent = '📝 Listo', 2000);
    }
}

function notepadLoad() {
    const content = document.getElementById('notepad-content');
    const status = document.getElementById('notepad-status');
    if (!content || !status) return;
    
    const name = prompt('Nombre del archivo a cargar:', 'nota.txt');
    if (name) {
        const saved = localStorage.getItem('kalm_notepad_' + name);
        if (saved) {
            content.value = saved;
            status.textContent = '📂 Cargado: ' + name;
        } else {
            status.textContent = '❌ Archivo no encontrado';
        }
        setTimeout(() => status.textContent = '📝 Listo', 2000);
    }
}

function notepadClear() {
    const content = document.getElementById('notepad-content');
    const status = document.getElementById('notepad-status');
    if (!content || !status) return;
    if (confirm('¿Borrar todo el contenido?')) {
        content.value = '';
        status.textContent = '🗑️ Limpiado';
        setTimeout(() => status.textContent = '📝 Listo', 2000);
    }
}

// ═══════════════════════════════════════════════════════════
// FUNCIONES PARA REPRODUCTOR
// ═══════════════════════════════════════════════════════════

function musicPlay() {
    const info = document.getElementById('music-info');
    if (info) {
        info.textContent = '▶️ Reproduciendo música...';
        const progress = document.getElementById('music-progress');
        if (progress) progress.style.width = '45%';
        const time = document.getElementById('music-time');
        if (time) time.textContent = '1:15';
        const duration = document.getElementById('music-duration');
        if (duration) duration.textContent = '3:45';
    }
}

function musicPause() {
    const info = document.getElementById('music-info');
    if (info) info.textContent = '⏸️ Pausado';
}

function musicNext() {
    const info = document.getElementById('music-info');
    const progress = document.getElementById('music-progress');
    if (info) info.textContent = '⏭️ Siguiente canción';
    if (progress) progress.style.width = '0%';
    const time = document.getElementById('music-time');
    if (time) time.textContent = '0:00';
}

function musicPrev() {
    const info = document.getElementById('music-info');
    const progress = document.getElementById('music-progress');
    if (info) info.textContent = '⏮️ Canción anterior';
    if (progress) progress.style.width = '0%';
    const time = document.getElementById('music-time');
    if (time) time.textContent = '0:00';
}

// ═══════════════════════════════════════════════════════════
// FUNCIONES PARA RELOJ
// ═══════════════════════════════════════════════════════════

function updateWorldClocks() {
    const now = new Date();
    const localDisplay = document.getElementById('clock-display');
    if (localDisplay) {
        localDisplay.textContent = now.toLocaleTimeString('es-ES');
    }
    
    const cities = [
        { id: 'clock-london', offset: 0 },
        { id: 'clock-ny', offset: -4 },
        { id: 'clock-tokyo', offset: 9 },
        { id: 'clock-sydney', offset: 10 }
    ];
    
    cities.forEach(city => {
        const el = document.getElementById(city.id);
        if (el) {
            const cityTime = new Date(now.getTime() + (now.getTimezoneOffset() + city.offset * 60) * 60000);
            el.textContent = cityTime.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
        }
    });
}

if (document.getElementById('clock-display')) {
    updateWorldClocks();
    setInterval(updateWorldClocks, 1000);
}

// ═══════════════════════════════════════════════════════════
// FUNCIONES PARA HERRAMIENTAS Y JUEGOS (desde window)
// ═══════════════════════════════════════════════════════════

// Estas funciones se cargan desde tools.js y games.js
// window.runTool y window.runGame ya están definidas

// ═══════════════════════════════════════════════════════════
// EXPORTAR FUNCIONES GLOBALMENTE
// ═══════════════════════════════════════════════════════════

window.runTool = runTool;
window.runGame = runGame;
window.loadTools = loadTools;
window.loadGames = loadGames;
window.openTerminalForProcess = openTerminalForProcess;
window.closeTerminalWindow = closeTerminalWindow;

console.log('🏰 Kalm OS v4.3 - Aplicación cargada correctamente');
