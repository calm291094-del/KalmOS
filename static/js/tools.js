// KALM OS v4.3 - Herramientas (Carga dinámica desde system/program)
let toolProcessId = null;
let toolsLoaded = false;
let toolsLoading = false;

// Función para cargar herramientas desde el servidor
function loadTools() {
    const container = document.getElementById('tool-buttons');
    if (!container) return;
    
    if (toolsLoading) return;
    toolsLoading = true;

    container.innerHTML = '<div style="color:#9370db;text-align:center;padding:20px;">⏳ Cargando herramientas...</div>';

    fetch('/api/programs')
        .then(r => {
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return r.json();
        })
        .then(programs => {
            if (!Array.isArray(programs)) {
                console.warn('⚠️ /api/programs no devolvió un array');
                container.innerHTML = '<p style="color:#9370db;text-align:center;padding:10px;">🛠️ No hay herramientas disponibles</p>';
                toolsLoading = false;
                return;
            }
            
            // Filtrar herramientas
            const tools = programs.filter(p => 
                p.category === 'utility' || p.category === 'dev' || 
                p.category === 'office' || p.category === 'media' ||
                p.type === 'tool' || p.type === 'utility'
            );
            
            if (tools.length === 0) {
                container.innerHTML = '<p style="color:#9370db;text-align:center;padding:10px;">🛠️ No hay herramientas disponibles en system/program/</p>';
                toolsLoading = false;
                toolsLoaded = true;
                return;
            }
            
            container.innerHTML = '';
            tools.forEach(tool => {
                const btn = document.createElement('button');
                btn.className = 'act';
                const toolName = tool.filename ? tool.filename.replace(/\.[^.]+$/, '') : tool.name;
                btn.textContent = `${tool.icon || '🛠️'} ${tool.name || toolName}`;
                btn.onclick = () => runTool(tool.path || toolName);
                btn.style.cssText = 'margin:4px;padding:8px 14px;cursor:pointer;';
                container.appendChild(btn);
            });
            toolsLoading = false;
            toolsLoaded = true;
        })
        .catch(err => {
            console.error('Error cargando herramientas:', err);
            container.innerHTML = '<p style="color:#ff6b6b;text-align:center;padding:10px;">❌ Error cargando herramientas</p>';
            toolsLoading = false;
        });
}

// Función para ejecutar una herramienta
function runTool(tool) {
    const output = document.getElementById('tool-output');
    if (!output) return;
    
    let path = tool;
    if (!path.includes('/') && !path.includes('\\')) {
        path = `system/program/${tool}.py`;
    }
    
    output.textContent = `⏳ Ejecutando ${tool}...\n`;
    console.log(`🛠️ Ejecutando herramienta: ${path}`);
    
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path, args: [tool] })
    })
    .then(r => r.json())
    .then(data => {
        console.log('📤 Respuesta herramienta:', data);
        if (data.ok && data.stdout) {
            output.textContent = data.stdout;
        } else if (data.ok && data.session_id) {
            toolProcessId = data.session_id;
            output.textContent = `✅ ${tool} ejecutado (PID ${data.pid})\n\n📋 Abriendo TERMINAL...\n`;
            if (typeof openTerminalForProcess === 'function') {
                openTerminalForProcess(data.session_id, tool);
            }
            if (typeof loadServers === 'function') loadServers();
        } else if (data.ok && data.viewer_url) {
            window.open(data.viewer_url, '_blank');
            output.textContent = `📄 ${tool} abierto en visor`;
        } else {
            output.textContent = `❌ Error: ${data.error || 'desconocido'}`;
        }
    })
    .catch(err => {
        console.error('❌ Error ejecutando herramienta:', err);
        output.textContent = `❌ Error de conexión: ${err.message}`;
    });
}

function stopTool() {
    if (!toolProcessId) { 
        alert('No hay herramienta ejecutándose'); 
        return; 
    }
    fetch(`/api/process/stop/${toolProcessId}`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.ok) {
                const output = document.getElementById('tool-output');
                if (output) output.textContent += '\n\n⏹️ Herramienta detenida';
                toolProcessId = null;
                if (typeof closeTerminalWindow === 'function') closeTerminalWindow();
            }
        })
        .catch(err => console.error('❌ Error deteniendo herramienta:', err));
}

// Cuando se abre la ventana de herramientas, cargar herramientas
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        const win = document.getElementById('win-tools');
        if (win && win.style.display !== 'none' && !toolsLoaded) {
            loadTools();
        }
    }, 500);
});

// Observador para cuando se abra la ventana
let toolsObserver = null;

function initToolsObserver() {
    if (toolsObserver) return;
    toolsObserver = new MutationObserver(() => {
        const win = document.getElementById('win-tools');
        if (win && win.style.display !== 'none' && !toolsLoaded && !toolsLoading) {
            loadTools();
        }
    });
    toolsObserver.observe(document.body, { childList: true, subtree: true });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initToolsObserver);
} else {
    initToolsObserver();
}

// Exportar funciones globalmente
window.loadTools = loadTools;
window.runTool = runTool;
window.stopTool = stopTool;

console.log('🛠️ Tools.js cargado - Herramientas disponibles');