// KALM OS v4.3 - Herramientas (Carga dinámica desde system/Program)
let toolProcessId = null;

// Función para cargar herramientas desde el servidor
function loadTools() {
    const container = document.getElementById('tool-buttons');
    if (!container) return;

    container.innerHTML = '<div style="color:#9370db;text-align:center;padding:20px;">⏳ Cargando herramientas...</div>';

    fetch('/api/programs')
        .then(r => {
            if (!r.ok) throw new Error('Error en la respuesta');
            return r.json();
        })
        .then(programs => {
            // Filtrar herramientas (categoría 'utility', 'dev', 'office', 'media')
            const tools = programs.filter(p => 
                p.category === 'utility' || p.category === 'dev' || 
                p.category === 'office' || p.category === 'media' ||
                p.type === 'tool' || p.type === 'utility'
            );
            
            if (tools.length === 0) {
                container.innerHTML = '<p style="color:#9370db;text-align:center;padding:10px;">🛠️ No hay herramientas disponibles en system/Program/</p>';
                return;
            }
            
            container.innerHTML = '';
            tools.forEach(tool => {
                const btn = document.createElement('button');
                btn.className = 'act';
                btn.textContent = `${tool.icon || '🛠️'} ${tool.name}`;
                btn.onclick = () => runTool(tool.filename.replace(/\.[^.]+$/, ''));
                btn.style.cssText = 'margin:4px;padding:8px 14px;cursor:pointer;';
                container.appendChild(btn);
            });
        })
        .catch(err => {
            console.error('Error cargando herramientas:', err);
            container.innerHTML = '<p style="color:#ff6b6b;text-align:center;padding:10px;">❌ Error cargando herramientas</p>';
        });
}

// Función para ejecutar una herramienta
function runTool(tool) {
    const output = document.getElementById('tool-output');
    if (!output) return;
    output.textContent = `⏳ Ejecutando ${tool}...\n`;
    
    const path = `system/Program/${tool}.py`;
    
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path, args: [tool] })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok && data.stdout) {
            output.textContent = data.stdout;
        } else if (data.ok && data.session_id) {
            toolProcessId = data.session_id;
            output.textContent = `✅ ${tool} ejecutado (PID ${data.pid})\n\n📋 Abriendo TERMINAL...\n`;
            if (typeof openTerminalForProcess === 'function') {
                openTerminalForProcess(data.session_id, tool);
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

function stopTool() {
    if (!toolProcessId) { alert('No hay herramienta ejecutándose'); return; }
    fetch(`/api/process/stop/${toolProcessId}`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.ok) {
                const output = document.getElementById('tool-output');
                if (output) output.textContent += '\n\n⏹️ Herramienta detenida';
                toolProcessId = null;
                if (typeof closeTerminalWindow === 'function') closeTerminalWindow();
            }
        });
}

// Cuando se abre la ventana de herramientas, cargar herramientas
document.addEventListener('DOMContentLoaded', function() {
    // Si la ventana ya está visible, cargar
    setTimeout(() => {
        const win = document.getElementById('win-tools');
        if (win && win.style.display !== 'none') {
            loadTools();
        }
    }, 300);
});

// Observador para cuando se abra la ventana
const toolsObserver = new MutationObserver(() => {
    const win = document.getElementById('win-tools');
    if (win && win.style.display !== 'none') {
        loadTools();
    }
});
toolsObserver.observe(document.body, { childList: true, subtree: true });

// Exportar funciones globalmente
window.loadTools = loadTools;
window.runTool = runTool;
window.stopTool = stopTool;

console.log('🛠️ Tools.js cargado - Herramientas disponibles');