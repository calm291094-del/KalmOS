// KALM OS v4.3 - Juegos (CON TERMINAL AUTOMÁTICA)

let gameProcessId = null;

// Usar el GAME_MAP de window (definido en app.js)
// NO redeclarar const GAME_MAP aquí

function runGame(game) {
    const output = document.getElementById('game-output');
    if (!output) return;
    
    output.textContent = `🎮 Iniciando ${game}...\n`;
    
    // Usar el GAME_MAP global de window
    const gameMap = window.GAME_MAP || {};
    const script = gameMap[game] || `${game}.py`;
    // Ruta CORRECTA: system/program/
    const path = `system/program/${script}`;
    
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok && data.stdout) {
            // Si el script terminó rápido y devolvió salida
            output.textContent = data.stdout;
        } else if (data.ok && data.session_id) {
            gameProcessId = data.session_id;
            
            // Mostrar mensaje en la ventana de juegos
            output.textContent = `✅ ${game} ejecutado (PID ${data.pid})\n\n`;
            output.textContent += `📋 Abriendo TERMINAL para jugar...\n`;
            output.textContent += `💡 El juego se está ejecutando en segundo plano.\n\n`;
            output.textContent += `🔄 Si no ves la salida, asegúrate de que la Terminal esté abierta.`;
            
            // ═══ ABRIR TERMINAL AUTOMÁTICAMENTE ═══
            // Usar la función openTerminalForProcess de file_manager.js
            if (typeof openTerminalForProcess === 'function') {
                openTerminalForProcess(data.session_id, game);
            } else {
                // Fallback: mostrar instrucciones
                output.textContent += `\n\n⚠️ No se pudo abrir la terminal automáticamente.\n`;
                output.textContent += `Abre la Terminal manualmente desde el menú inicio.`;
            }
            
            // Actualizar lista de servidores
            if (typeof loadServers === 'function') {
                loadServers();
            }
        } else {
            output.textContent = `❌ Error: ${data.error || 'desconocido'}`;
        }
    })
    .catch(err => {
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
                // Cerrar terminal si está abierta
                if (typeof closeTerminalWindow === 'function') {
                    closeTerminalWindow();
                }
            }
        });
}

// Juegos rápidos en la terminal
function quickGame(game) {
    const output = document.getElementById('game-output');
    if (!output) return;
    
    const games = {
        'ppt': 'piedra_papel_tijera.py',
        'gato': 'gato.py',
        'ahorcado': 'ahorcado.py'
    };
    
    const script = games[game] || `${game}.py`;
    const path = `system/program/${script}`;
    
    output.textContent = `🎮 Iniciando ${game}...\n`;
    
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
            output.textContent = `✅ ${game} ejecutado (PID ${data.pid})\n📋 Abriendo terminal...`;
            if (typeof openTerminalForProcess === 'function') {
                openTerminalForProcess(data.session_id, game);
            }
        } else {
            output.textContent = `❌ Error: ${data.error || 'desconocido'}`;
        }
    });
}

// Juego de memoria (simplificado)
function memoryGame() {
    const output = document.getElementById('game-output');
    if (!output) return;
    
    const emojis = ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼'];
    let cards = [...emojis, ...emojis];
    cards = cards.sort(() => Math.random() - 0.5);
    
    let revealed = Array(16).fill(false);
    let first = null;
    let moves = 0;
    let pairs = 0;
    
    output.textContent = '🧠 MEMORIA\n';
    output.textContent += '═'.repeat(40) + '\n\n';
    output.textContent += 'Para jugar, abre la terminal.\n';
    output.textContent += 'Este juego funciona mejor en consola.\n\n';
    output.textContent += 'Usa el comando: python system/program/memoria.py';
}

// Estadísticas de juegos
function gameStats() {
    const output = document.getElementById('game-output');
    if (!output) return;
    
    output.textContent = '📊 ESTADÍSTICAS DE JUEGOS\n';
    output.textContent += '═'.repeat(40) + '\n\n';
    
    const stats = {
        'Snake': { wins: 5, highScore: 120 },
        'Buscaminas': { wins: 3, bestTime: '2:30' },
        'Blackjack': { wins: 8, losses: 4 },
        'Ajedrez': { wins: 2, losses: 3 }
    };
    
    for (const [game, data] of Object.entries(stats)) {
        output.textContent += `🎮 ${game}\n`;
        output.textContent += `   Victorias: ${data.wins}\n`;
        if (data.highScore) output.textContent += `   Puntuación máxima: ${data.highScore}\n`;
        if (data.bestTime) output.textContent += `   Mejor tiempo: ${data.bestTime}\n`;
        if (data.losses !== undefined) output.textContent += `   Derrotas: ${data.losses}\n`;
        output.textContent += '\n';
    }
}