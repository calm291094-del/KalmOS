// KALM OS v4.3 - Juegos (Carga dinámica desde system/Program)
let gameProcessId = null;

// Función para cargar juegos desde el servidor
function loadGames() {
    const container = document.getElementById('game-buttons');
    if (!container) return;

    container.innerHTML = '<div style="color:#9370db;text-align:center;padding:20px;">⏳ Cargando juegos...</div>';

    fetch('/api/programs')
        .then(r => {
            if (!r.ok) throw new Error('Error en la respuesta');
            return r.json();
        })
        .then(programs => {
            // Filtrar juegos (categoría 'game')
            const games = programs.filter(p => p.category === 'game' || p.type === 'game');
            
            if (games.length === 0) {
                container.innerHTML = '<p style="color:#9370db;text-align:center;padding:10px;">🎮 No hay juegos disponibles en system/Program/</p>';
                return;
            }
            
            container.innerHTML = '';
            games.forEach(game => {
                const btn = document.createElement('button');
                btn.className = 'act success';
                btn.textContent = `${game.icon || '🎮'} ${game.name}`;
                btn.onclick = () => runGame(game.filename.replace(/\.[^.]+$/, ''));
                btn.style.cssText = 'margin:4px;padding:8px 14px;';
                container.appendChild(btn);
            });
        })
        .catch(err => {
            console.error('Error cargando juegos:', err);
            container.innerHTML = '<p style="color:#ff6b6b;text-align:center;padding:10px;">❌ Error cargando juegos</p>';
        });
}

// Función original runGame (se mantiene)
function runGame(game) {
    const output = document.getElementById('game-output');
    if (!output) return;
    output.textContent = `🎮 Iniciando ${game}...\n`;
    
    const script = `${game}.py`;
    const path = `system/Program/${script}`;
    
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok && data.stdout) {
            output.textContent = data.stdout;
        } else if (data.ok && data.session_id) {
            gameProcessId = data.session_id;
            output.textContent = `✅ ${game} ejecutado (PID ${data.pid})\n\n📋 Abriendo TERMINAL...\n`;
            if (typeof openTerminalForProcess === 'function') {
                openTerminalForProcess(data.session_id, game);
            }
            if (typeof loadServers === 'function') loadServers();
        } else {
            output.textContent = `❌ Error: ${data.error || 'desconocido'}`;
        }
    })
    .catch(err => {
        output.textContent = `❌ Error de conexión: ${err.message}`;
    });
}

function stopGame() {
    if (!gameProcessId) { alert('No hay juego ejecutándose'); return; }
    fetch(`/api/process/stop/${gameProcessId}`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.ok) {
                const output = document.getElementById('game-output');
                if (output) output.textContent += '\n\n⏹️ Juego detenido';
                gameProcessId = null;
                if (typeof closeTerminalWindow === 'function') closeTerminalWindow();
            }
        });
}

// Cuando se abre la ventana de juegos, cargar juegos
document.addEventListener('DOMContentLoaded', function() {
    const observer = new MutationObserver(() => {
        const win = document.getElementById('win-games');
        if (win && win.style.display !== 'none') {
            loadGames();
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Si la ventana ya está abierta, cargar
    setTimeout(() => {
        const win = document.getElementById('win-games');
        if (win && win.style.display !== 'none') {
            loadGames();
        }
    }, 500);
});