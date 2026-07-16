// KALM OS v4.3 - Herramientas Profesionales (CON TERMINAL AUTOMÁTICA)

let toolProcessId = null;

// Usar el TOOL_MAP de window (definido en app.js)
// NO redeclarar const TOOL_MAP aquí

function runTool(tool) {
    const output = document.getElementById('tool-output');
    if (!output) return;
    
    output.textContent = `⏳ Ejecutando ${tool}...\n`;
    
    // Usar el TOOL_MAP global de window
    const toolMap = window.TOOL_MAP || {};
    const script = toolMap[tool] || 'herramientas.py';
    // Ruta CORRECTA: system/program/
    const path = `system/program/${script}`;
    
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            path: path,
            args: [tool]
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok && data.stdout) {
            // Si el script terminó rápido y devolvió salida
            output.textContent = data.stdout;
        } else if (data.ok && data.session_id) {
            toolProcessId = data.session_id;
            
            // Mostrar mensaje en la ventana de herramientas
            output.textContent = `✅ ${tool} ejecutado (PID ${data.pid})\n\n`;
            output.textContent += `📋 Abriendo TERMINAL para ver la salida...\n`;
            output.textContent += `💡 La herramienta se está ejecutando en segundo plano.\n\n`;
            output.textContent += `📤 La salida se mostrará en la terminal.`;
            
            // ═══ ABRIR TERMINAL AUTOMÁTICAMENTE ═══
            if (typeof openTerminalForProcess === 'function') {
                openTerminalForProcess(data.session_id, tool);
            } else {
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
                // Cerrar terminal si está abierta
                if (typeof closeTerminalWindow === 'function') {
                    closeTerminalWindow();
                }
            }
        });
}

// Herramientas rápidas en la terminal
function runQuickTool(tool, args) {
    const output = document.getElementById('tool-output');
    if (!output) return;
    
    output.textContent = `⏳ Ejecutando ${tool}...\n`;
    
    const path = `system/program/${tool}.py`;
    
    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            path: path,
            args: args || []
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok && data.stdout) {
            output.textContent = data.stdout;
        } else if (data.ok && data.session_id) {
            output.textContent = `✅ ${tool} ejecutado (PID ${data.pid})\n📋 Abriendo terminal...`;
            if (typeof openTerminalForProcess === 'function') {
                openTerminalForProcess(data.session_id, tool);
            }
        } else {
            output.textContent = `❌ Error: ${data.error || 'desconocido'}`;
        }
    })
    .catch(err => {
        output.textContent = `❌ Error: ${err.message}`;
    });
}

// Generar contraseña (directo en JS)
function generatePassword() {
    const output = document.getElementById('tool-output');
    if (!output) return;
    
    const length = parseInt(prompt('Longitud de la contraseña (8-32):', '16')) || 16;
    const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?';
    let password = '';
    for (let i = 0; i < length; i++) {
        password += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    
    output.textContent = `🔑 CONTRASEÑA GENERADA\n`;
    output.textContent += `═`.repeat(40) + '\n\n';
    output.textContent += `  ${password}\n\n`;
    output.textContent += `═`.repeat(40) + '\n';
    output.textContent += `📊 Longitud: ${password.length} caracteres\n`;
    output.textContent += `📊 Fuerza: ${password.length >= 16 ? 'Alta' : password.length >= 10 ? 'Media' : 'Baja'}`;
}