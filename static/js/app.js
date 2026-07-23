// KALM OS v4.3 - Aplicación Principal (CORREGIDA)
// ✅ Kalm AI usa el sistema de pestañas de internal_browser.js
// ✅ Eliminada referencia al viejo iframe browser-frame

// ═══════════════════════════════════════════════════════════
// VARIABLES GLOBALES
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

// ═══════════════════════════════════════════════════════════
// INICIALIZACIÓN
// ═══════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', function() {
    console.log('🏰 Kalm OS v4.3 iniciado');

    fetch('/api/background-check')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.exists) {
                document.body.style.backgroundImage = 'url("/background?t=' + Date.now() + '")';
            }
        })
        .catch(function() {});

    updateResourceMonitor();
    if (window.resourceUpdateInterval) clearInterval(window.resourceUpdateInterval);
    window.resourceUpdateInterval = setInterval(updateResourceMonitor, 5000);

    updateClock();
    if (window.clockUpdateInterval) clearInterval(window.clockUpdateInterval);
    window.clockUpdateInterval = setInterval(updateClock, 1000);

    loadProgramMenu();

    document.addEventListener('click', function(e) {
        var menu = document.getElementById('start-menu');
        var startBtn = document.getElementById('start-btn');
        if (menu && startBtn && !menu.contains(e.target) && !startBtn.contains(e.target)) {
            menu.style.display = 'none';
        }
    });
});

// ═══════════════════════════════════════════════════════════
// RELOJ Y MENÚ INICIO
// ═══════════════════════════════════════════════════════════
function updateClock() {
    var clock = document.getElementById('clock');
    if (clock) clock.textContent = new Date().toLocaleTimeString('es-ES');
}

function toggleStart() {
    var menu = document.getElementById('start-menu');
    if (menu) menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
}

// ═══════════════════════════════════════════════════════════
// MONITOR DE RECURSOS
// ═══════════════════════════════════════════════════════════
var isUpdating = false;
async function updateResourceMonitor() {
    if (isUpdating) return;
    isUpdating = true;
    try {
        var response = await fetch('/api/system-stats');
        if (!response.ok) { isUpdating = false; return; }
        var data = await response.json();

        var cpuVal = document.getElementById('rm-cpu-val');
        var cpuBar = document.getElementById('rm-cpu-bar');
        if (cpuVal) cpuVal.textContent = data.cpu + '%';
        if (cpuBar) cpuBar.style.width = Math.min(data.cpu, 100) + '%';

        var ramVal = document.getElementById('rm-ram-val');
        var ramBar = document.getElementById('rm-ram-bar');
        if (ramVal) ramVal.textContent = (data.ram_used || '0') + ' / ' + (data.ram_total || '0');
        if (ramBar) ramBar.style.width = Math.min(data.ram_percent || 0, 100) + '%';

        var diskVal = document.getElementById('rm-disk-val');
        var diskBar = document.getElementById('rm-disk-bar');
        if (diskVal) diskVal.textContent = (data.disk_used || '0') + ' / ' + (data.disk_total || '0');
        if (diskBar) diskBar.style.width = Math.min(data.disk_percent || 0, 100) + '%';

        var procs = document.getElementById('rm-procs');
        if (procs) procs.textContent = data.processes || 0;

        var netUp = document.getElementById('rm-net-up');
        var netDown = document.getElementById('rm-net-down');
        if (netUp) netUp.textContent = data.net_upload || '0 B/s';
        if (netDown) netDown.textContent = data.net_download || '0 B/s';

    } catch (error) {}
    isUpdating = false;
}

// ═══════════════════════════════════════════════════════════
// TASK MANAGER
// ═══════════════════════════════════════════════════════════
async function loadProcs() {
    try {
        var response = await fetch('/api/processes');
        if (!response.ok) return;
        var data = await response.json();
        var tbody = document.querySelector('#proc-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#9370db">No hay procesos</td></tr>';
            return;
        }
        data.forEach(function(p) {
            var tr = document.createElement('tr');
            tr.innerHTML = '<td>' + p.pid + '</td><td>' + (p.name || '?') + '</td><td>' + (p.cpu || 0) + '</td><td>' + (p.mem || 0) + '</td><td>' + (p.status || '?') + '</td><td><button class="act danger small" onclick="killProc(' + p.pid + ')">🔪</button></td>';
            tbody.appendChild(tr);
        });
    } catch (error) {}
}

async function killProc(pid) {
    if (!confirm('¿Matar proceso PID ' + pid + '?')) return;
    try {
        var response = await fetch('/api/kill/' + pid, { method: 'POST' });
        var data = await response.json();
        if (data.ok) loadProcs();
        else alert('❌ No se pudo matar el proceso');
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

// ═══════════════════════════════════════════════════════════
// MENÚ DE PROGRAMAS
// ═══════════════════════════════════════════════════════════
async function loadProgramMenu() {
    var submenu = document.getElementById('program-submenu');
    if (!submenu) return;
    try {
        var response = await fetch('/api/programs');
        if (!response.ok) {
            submenu.innerHTML = '<div class="item" style="color:#ff6b6b">❌ Error</div>';
            return;
        }
        var programs = await response.json();
        submenu.innerHTML = '';
        submenu.dataset.loaded = 'true';
        if (!programs || programs.length === 0) {
            submenu.innerHTML = '<div class="item" style="color:#9370db">📂 No hay programas</div>';
            return;
        }
        var categories = {};
        programs.forEach(function(p) {
            var cat = p.category || 'other';
            if (!categories[cat]) categories[cat] = [];
            categories[cat].push(p);
        });
        var catNames = {
            browser: '🌐 Navegadores', editor: '✏️ Editores', media: '🎵 Multimedia',
            dev: '💻 Desarrollo', server: '🚀 Servidores', office: '📄 Oficina',
            utility: '🔧 Utilidades', game: '🎮 Juegos', other: '📦 Otros'
        };

        Object.keys(categories).forEach(function(cat) {
            var items = categories[cat];
            var header = document.createElement('div');
            header.className = 'program-category';
            header.textContent = catNames[cat] || cat;
            submenu.appendChild(header);
            items.forEach(function(p) {
                var item = document.createElement('div');
                item.className = 'item';
                item.textContent = (p.icon || '📄') + ' ' + p.name;
                item.onclick = function() {
                    toggleStart();
                    executeProgramFromMenu(p.path, p.name);
                };
                submenu.appendChild(item);
            });
        });
    } catch (error) {
        console.error('❌ Error cargando programas:', error);
    }
}

function executeProgramFromMenu(path, name) {
    if (typeof showNotification === 'function') showNotification('⏳ Ejecutando ' + name + '...', 'info');
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    }).then(function(r) { return r.json(); }).then(function(data) {
        if (data.ok && data.session_id) {
            if (typeof showNotification === 'function') showNotification('✅ ' + name + ' ejecutado', 'success');
            if (typeof openTerminalForProcess === 'function') openTerminalForProcess(data.session_id, name);
        } else if (data.ok && data.viewer_url) {
            window.open(data.viewer_url, '_blank');
        } else {
            if (typeof showNotification === 'function') showNotification('❌ Error: ' + data.error, 'error');
        }
    }).catch(function(err) {
        if (typeof showNotification === 'function') showNotification('❌ Error: ' + err.message, 'error');
    });
}

// ═══════════════════════════════════════════════════════════
// KALM AI - CORREGIDO: Usa pestañas de internal_browser.js
// ═══════════════════════════════════════════════════════════

function openKalmAI() {
    console.log('🧠 Abriendo Kalm AI...');
    if (typeof showNotification === 'function') showNotification('🧠 Abriendo Kalm AI...', 'info');

    // Abrir la ventana del navegador
    if (typeof openWin === 'function') openWin('browser');

    // Esperar a que la ventana y internal_browser.js estén listos
    setTimeout(function() {
        if (typeof createTab === 'function') {
            // Buscar si ya existe una pestaña con Kalm AI
            var existingTab = null;
            if (window.browserTabs) {
                for (var i = 0; i < window.browserTabs.length; i++) {
                    if (window.browserTabs[i].url === '/api/kalm/') {
                        existingTab = window.browserTabs[i];
                        break;
                    }
                }
            }

            if (existingTab) {
                // Ya existe: activar esa pestaña
                switchTab(existingTab.id);
                console.log('✅ Pestaña Kalm AI existente activada');
            } else {
                // No existe: crear nueva pestaña
                createTab('/api/kalm/', '🧠 Kalm AI', true);
                console.log('✅ Nueva pestaña Kalm AI creada');
            }

            // Actualizar barra de URL
            var urlInput = document.getElementById('browser-url');
            if (urlInput) urlInput.value = '/api/kalm/';

            // Actualizar estado
            var status = document.getElementById('browser-status');
            if (status) {
                status.textContent = '🧠 Kalm AI - Listo';
                status.style.color = '#00cc66';
            }

            if (typeof showNotification === 'function') showNotification('✅ Kalm AI listo', 'success');
        } else {
            // internal_browser.js aún no cargó, reintentar
            console.log('⏳ internal_browser.js no listo, reintentando...');
            setTimeout(openKalmAI, 500);
        }
    }, 400);
}

function openKalmAIBrowser() {
    // Redirige a openKalmAI (mantiene compatibilidad)
    openKalmAI();
}

function openChatAcademico() {
    console.log('📚 Abriendo Chat Académico...');
    if (typeof showNotification === 'function') showNotification('📚 Abriendo Chat Académico...', 'info');

    if (typeof openWin === 'function') openWin('browser');

    setTimeout(function() {
        if (typeof createTab === 'function') {
            // Buscar si ya hay pestaña de chat académico
            var existingTab = null;
            if (window.browserTabs) {
                for (var i = 0; i < window.browserTabs.length; i++) {
                    if (window.browserTabs[i].url === '/api/kalm/' && window.browserTabs[i].title.indexOf('Académico') !== -1) {
                        existingTab = window.browserTabs[i];
                        break;
                    }
                }
            }

            if (existingTab) {
                switchTab(existingTab.id);
            } else {
                createTab('/api/kalm/', '📚 Chat Académico', true);
            }

            var urlInput = document.getElementById('browser-url');
            if (urlInput) urlInput.value = '/api/kalm/';
        } else {
            setTimeout(openChatAcademico, 500);
        }
    }, 400);
}

function openKrootCorp() {
    console.log('🏢 Abriendo Kroot Corp...');
    if (typeof showNotification === 'function') showNotification('🏢 Abriendo Kroot Corp...', 'info');

    if (typeof openWin === 'function') openWin('browser');

    setTimeout(function() {
        if (typeof createTab === 'function') {
            createTab('https://krootcorp.com', '🏢 Kroot Corp', true);

            var urlInput = document.getElementById('browser-url');
            if (urlInput) urlInput.value = 'https://krootcorp.com';
        } else {
            setTimeout(openKrootCorp, 500);
        }
    }, 400);
}

// Función de compatibilidad: si algo más la llama, redirige a openKalmAI
function loadKalmAIInFrame() {
    openKalmAI();
}

function forceLoadKalmAI() {
    openKalmAI();
}

// ═══════════════════════════════════════════════════════════
// NOTIFICACIONES
// ═══════════════════════════════════════════════════════════
function showNotification(message, type) {
    type = type || 'info';
    var colors = { info: '#9370db', success: '#00cc66', error: '#ff4444', warning: '#ffaa00' };
    var div = document.createElement('div');
    div.style.cssText = 'position:fixed;bottom:60px;right:20px;background:rgba(10,5,20,0.95);' +
        'border:1px solid ' + (colors[type] || '#9370db') + ';color:#fff;padding:12px 20px;' +
        'border-radius:8px;z-index:10000;max-width:400px;font-size:13px;' +
        'box-shadow:0 5px 20px rgba(0,0,0,0.5);font-family:Segoe UI,sans-serif;transition:opacity 0.5s;';
    div.textContent = message;
    document.body.appendChild(div);
    setTimeout(function() {
        div.style.opacity = '0';
        setTimeout(function() { div.remove(); }, 500);
    }, 4000);
}

// ═══════════════════════════════════════════════════════════
// MARCADORES DEL NAVEGADOR
// ═══════════════════════════════════════════════════════════
function loadBrowserBookmarks() {
    var container = document.getElementById('browser-bookmarks');
    if (!container || window.bookmarksLoadedFlag || window.bookmarksLoading) return;
    window.bookmarksLoading = true;
    fetch('/api/browser/bookmarks')
        .then(function(r) { return r.ok ? r.json() : null; })
        .then(function(bookmarks) {
            container.innerHTML = '';
            if (bookmarks && bookmarks.length > 0) {
                bookmarks.forEach(function(bm) {
                    var btn = document.createElement('button');
                    btn.className = 'act small';
                    btn.textContent = (bm.icon || '🌐') + ' ' + bm.name;
                    btn.style.cssText = 'background:rgba(75,0,130,0.3);border-color:#6a0dad;margin:2px;cursor:pointer;';
                    btn.onclick = function() {
                        var urlInput = document.getElementById('browser-url');
                        if (urlInput) {
                            var url = bm.url || bm.domain || '';
                            if (url && !url.startsWith('http') && !url.startsWith('/') && !url.startsWith('#')) {
                                url = 'https://' + url;
                            }
                            urlInput.value = url;
                            if (typeof browserNavigate === 'function') browserNavigate();
                        }
                    };
                    container.appendChild(btn);
                });
            } else {
                container.innerHTML = '<span style="color:#9370db;font-size:11px">📖 Sin marcadores</span>';
            }
            window.bookmarksLoading = false;
            window.bookmarksLoadedFlag = true;
        })
        .catch(function() {
            container.innerHTML = '<span style="color:#9370db;font-size:11px">📖 Marcadores</span>';
            window.bookmarksLoading = false;
            window.bookmarksLoadedFlag = true;
        });
}

// ═══════════════════════════════════════════════════════════
// ENHANCE DE openWin (agrega carga de datos al abrir ventanas)
// ═══════════════════════════════════════════════════════════
var originalOpenWin = window.openWin || function() {};
window.openWin = function(id) {
    if (typeof originalOpenWin === 'function') originalOpenWin(id);
    setTimeout(function() {
        if (id === 'taskmgr') loadProcs();
        if (id === 'browser') loadBrowserBookmarks();
    }, 300);
};

// ═══════════════════════════════════════════════════════════
// EXPORTACIONES
// ═══════════════════════════════════════════════════════════
window.runTool = window.runTool || function() {};
window.runGame = window.runGame || function() {};
window.openTerminalForProcess = window.openTerminalForProcess || function() {};
window.openKalmAI = openKalmAI;
window.openKalmAIBrowser = openKalmAIBrowser;
window.openChatAcademico = openChatAcademico;
window.openKrootCorp = openKrootCorp;
window.showNotification = showNotification;
window.loadKalmAIInFrame = loadKalmAIInFrame;
window.forceLoadKalmAI = forceLoadKalmAI;
window.loadBrowserBookmarks = loadBrowserBookmarks;

console.log('🏰 Kalm OS v4.3 - Aplicación cargada correctamente');
