// KALM OS v4.3 - Juegos (Carga dinámica desde system/program)
let gameProcessId = null;
let gamesLoaded = false;
let gamesLoading = false;

// Función para cargar juegos desde el servidor
function loadGames() {
    const container = document.getElementById('game-buttons');
    if (!container) return;
    
    // Evitar recargas múltiples mientras se carga
    if (gamesLoading) return;
    gamesLoading = true;

    container.innerHTML = '<div style="color:#9370db;text-align:center;padding:20px;">⏳ Cargando juegos...</div>';

    fetch('/api/programs')
        .then(r => {
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return r.json();
        })
        .then(programs => {
            // Verificar que programs es un array
            if (!Array.isArray(programs)) {
                console.warn('⚠️ /api/programs no devolvió un array:', programs);
                container.innerHTML = '<p style="color:#9370db;text-align:center;padding:10px;">📦 No hay juegos disponibles</p>';
                gamesLoading = false;
                return;
            }
            
            // Filtrar juegos (categoría 'game')
            const games = programs.filter(p => p.category === 'game' || p.type === 'game' || p.name?.toLowerCase().includes('juego'));
            
            if (games.length === 0) {
                container.innerHTML = '<p style="color:#9370db;text-align:center;padding:10px;">🎮 No hay juegos disponibles en system/program/</p>';
                gamesLoading = false;
                gamesLoaded = true;
                return;
            }
            
            container.innerHTML = '';
            games.forEach(game => {
                const btn = document.createElement('button');
                btn.className = 'act success';
                // Usar el nombre del archivo sin extensión como identificador
                const gameName = game.filename ? game.filename.replace(/\.[^.]+$/, '') : game.name;
                btn.textContent = `${game.icon || '🎮'} ${game.name || gameName}`;
                btn.onclick = () => runGame(game.path || gameName);
                btn.style.cssText = 'margin:4px;padding:8px 14px;cursor:pointer;';
                container.appendChild(btn);
            });
            gamesLoading = false;
            gamesLoaded = true;
        })
        .catch(err => {
            console.error('❌ Error cargando juegos:', err);
            container.innerHTML = '<p style="color:#ff6b6b;text-align:center;padding:10px;">❌ Error cargando juegos</p>';
            gamesLoading = false;
        });
}

// Función para ejecutar un juego
function runGame(game) {
    const output = document.getElementById('game-output');
    if (!output) return;
    
    // Determinar la ruta del juego
    let path = game;
    // Si es solo un nombre, construir la ruta
    if (!path.includes('/') && !path.includes('\\')) {
        path = `system/program/${game}.py`;
    }
    
    output.textContent = `🎮 Iniciando ${game}...\n`;
    console.log(`🎮 Ejecutando juego: ${path}`);
    
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    })
    .then(r => r.json())
    .then(data => {
        console.log('📤 Respuesta juego:', data);
        if (data.ok && data.stdout) {
            output.textContent = data.stdout;
        } else if (data.ok && data.session_id) {
            gameProcessId = data.session_id;
            output.textContent = `✅ ${game} ejecutado (PID ${data.pid})\n\n📋 Abriendo TERMINAL...\n`;
            if (typeof openTerminalForProcess === 'function') {
                openTerminalForProcess(data.session_id, game);
            }
            if (typeof loadServers === 'function') loadServers();
        } else if (data.ok && data.viewer_url) {
            window.open(data.viewer_url, '_blank');
            output.textContent = `📄 ${game} abierto en visor`;
        } else {
            output.textContent = `❌ Error: ${data.error || 'desconocido'}`;
        }
    })
    .catch(err => {
        console.error('❌ Error ejecutando juego:', err);
        output.textContent = `❌ Error de conexión: ${err.message}`;
    });
}

function stopGame() {
    if (!gameProcessId) { 
        alert('No hay juego ejecutándose'); 
        return; 
    }
    fetch(`/api/process/stop/${gameProcessId}`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.ok) {
                const output = document.getElementById('game-output');
                if (output) output.textContent += '\n\n⏹️ Juego detenido';
                gameProcessId = null;
                if (typeof closeTerminalWindow === 'function') closeTerminalWindow();
            }
        })
        .catch(err => console.error('❌ Error deteniendo juego:', err));
}

// Cuando se abre la ventana de juegos, cargar juegos
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        const win = document.getElementById('win-games');
        if (win && win.style.display !== 'none' && !gamesLoaded) {
            loadGames();
        }
    }, 500);
});

// Observador para cuando se abra la ventana - usando un solo observer
let gamesObserver = null;

function initGamesObserver() {
    if (gamesObserver) return;
    gamesObserver = new MutationObserver(() => {
        const win = document.getElementById('win-games');
        if (win && win.style.display !== 'none' && !gamesLoaded && !gamesLoading) {
            loadGames();
        }
    });
    gamesObserver.observe(document.body, { childList: true, subtree: true });
}

// Iniciar observer después de que el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGamesObserver);
} else {
    initGamesObserver();
}

// Exportar funciones globalmente
window.loadGames = loadGames;
window.runGame = runGame;
window.stopGame = stopGame;

console.log('🎮 Games.js cargado - Juegos disponibles');