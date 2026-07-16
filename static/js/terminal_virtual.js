// Terminal Virtual con conexión SSE (Server-Sent Events)
class VirtualTerminal {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.sessionId = null;
        this.eventSource = null;
        this.isRunning = false;
        this.outputBuffer = '';
        this.callbacks = {};
    }
    
    start(programPath, args) {
        // Iniciar proceso en el servidor
        fetch('/api/process/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ path: programPath, args: args || [] })
        })
        .then(r => r.json())
        .then(data => {
            if (data.ok) {
                this.sessionId = data.session_id;
                this.isRunning = true;
                this.connectStream();
                if (this.callbacks.onStart) {
                    this.callbacks.onStart(data);
                }
            } else {
                if (this.callbacks.onError) {
                    this.callbacks.onError(data.error);
                }
            }
        })
        .catch(err => {
            if (this.callbacks.onError) {
                this.callbacks.onError(err.message);
            }
        });
    }
    
    connectStream() {
        // Usar EventSource para streaming en tiempo real
        const url = `/api/process/stream/${this.sessionId}`;
        this.eventSource = new EventSource(url);
        
        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleOutput(data);
            } catch (e) {
                console.error('Error parsing SSE data:', e);
            }
        };
        
        this.eventSource.onerror = (event) => {
            if (this.eventSource.readyState === EventSource.CLOSED) {
                this.isRunning = false;
                if (this.callbacks.onClose) {
                    this.callbacks.onClose();
                }
            }
        };
    }
    
    handleOutput(data) {
        if (data.type === 'output') {
            this.outputBuffer += data.data;
            if (this.callbacks.onOutput) {
                this.callbacks.onOutput(data.data);
            }
        } else if (data.type === 'exit') {
            this.isRunning = false;
            if (this.callbacks.onExit) {
                this.callbacks.onExit(data.code);
            }
            this.eventSource.close();
        } else if (data.type === 'error') {
            if (this.callbacks.onError) {
                this.callbacks.onError(data.data);
            }
        }
    }
    
    sendInput(input) {
        if (!this.isRunning || !this.sessionId) return;
        
        fetch('/api/process/input', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                session_id: this.sessionId, 
                input: input 
            })
        });
    }
    
    stop() {
        if (this.sessionId) {
            fetch(`/api/process/stop/${this.sessionId}`, { method: 'POST' })
                .then(() => {
                    this.isRunning = false;
                    if (this.eventSource) {
                        this.eventSource.close();
                    }
                });
        }
    }
    
    on(event, callback) {
        this.callbacks[event] = callback;
    }
}

// ═══ TERMINAL VIRTUAL PARA EL NAVEGADOR ═══
class VirtualTerminalUI {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.terminal = new VirtualTerminal(containerId);
        this.setupUI();
    }
    
    setupUI() {
        // Crear la UI de la terminal
        this.container.innerHTML = `
            <div style="display:flex;flex-direction:column;height:100%;background:#0a0a1a;border-radius:5px">
                <div class="term-toolbar" style="padding:8px;background:#1a0033;border-bottom:1px solid #6a0dad;display:flex;gap:8px;flex-wrap:wrap;align-items:center">
                    <input id="term-program" placeholder="Ruta del programa (Ej: D:/Scripts/mi_app.exe)" style="flex:1;min-width:150px;background:#0a0a1a;color:#e6e6fa;border:1px solid #4b0082;padding:4px 8px;border-radius:3px">
                    <button id="term-start-btn" class="act small" style="background:#008800;border-color:#00cc44">▶️ Ejecutar</button>
                    <button id="term-stop-btn" class="act small danger" style="display:none">⏹ Detener</button>
                    <button id="term-clear-btn" class="act small" onclick="document.getElementById('term-output').innerHTML=''">🗑️ Limpiar</button>
                    <span id="term-status" style="color:#9370db;font-size:11px">Detenido</span>
                </div>
                <pre id="term-output" style="flex:1;margin:0;padding:10px;overflow-y:auto;color:#0f0;font-family:'Consolas',monospace;font-size:13px;white-space:pre-wrap;word-wrap:break-word;min-height:200px">📋 Listo para ejecutar programas...</pre>
                <div style="padding:8px;background:#0a0a1a;border-top:1px solid #4b0082;display:flex">
                    <span style="color:#0f0;margin-right:8px;font-family:monospace">$</span>
                    <input id="term-input" style="flex:1;background:transparent;color:#0f0;border:none;outline:none;font-family:monospace;font-size:13px" placeholder="Escribe aquí..." disabled>
                </div>
            </div>
        `;
        
        this.setupEvents();
    }
    
    setupEvents() {
        const startBtn = document.getElementById('term-start-btn');
        const stopBtn = document.getElementById('term-stop-btn');
        const programInput = document.getElementById('term-program');
        const termInput = document.getElementById('term-input');
        const output = document.getElementById('term-output');
        const status = document.getElementById('term-status');
        
        // Configurar callbacks de la terminal
        this.terminal.on('onStart', (data) => {
            status.textContent = `🟢 PID: ${data.pid}`;
            startBtn.style.display = 'none';
            stopBtn.style.display = 'inline-block';
            termInput.disabled = false;
            termInput.focus();
            output.innerHTML += `\x1b[32m▶️ ${data.message}\x1b[0m\n`;
        });
        
        this.terminal.on('onOutput', (data) => {
            output.innerHTML += data;
            output.scrollTop = output.scrollHeight;
        });
        
        this.terminal.on('onExit', (code) => {
            status.textContent = `🔴 Terminado (código ${code})`;
            startBtn.style.display = 'inline-block';
            stopBtn.style.display = 'none';
            termInput.disabled = true;
            output.innerHTML += `\x1b[33m📋 Proceso terminado con código ${code}\x1b[0m\n`;
        });
        
        this.terminal.on('onError', (error) => {
            output.innerHTML += `\x1b[31m❌ Error: ${error}\x1b[0m\n`;
            status.textContent = '❌ Error';
            startBtn.style.display = 'inline-block';
            stopBtn.style.display = 'none';
            termInput.disabled = true;
        });
        
        this.terminal.on('onClose', () => {
            status.textContent = '⏹ Detenido';
            startBtn.style.display = 'inline-block';
            stopBtn.style.display = 'none';
            termInput.disabled = true;
        });
        
        // Eventos
        startBtn.addEventListener('click', () => {
            const program = programInput.value.trim();
            if (!program) {
                output.innerHTML += `\x1b[31m❌ Ingresa la ruta del programa\x1b[0m\n`;
                return;
            }
            output.innerHTML += `\x1b[36m⏳ Iniciando: ${program}\x1b[0m\n`;
            this.terminal.start(program);
        });
        
        stopBtn.addEventListener('click', () => {
            this.terminal.stop();
        });
        
        termInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const input = termInput.value;
                if (input.trim()) {
                    this.terminal.sendInput(input);
                    output.innerHTML += `\n${input}\n`;
                }
                termInput.value = '';
            }
        });
        
        // Ejecutar con Enter en el campo de programa
        programInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') startBtn.click();
        });
    }
}

// Inicializar cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    // Crear la terminal virtual si existe el contenedor
    const container = document.getElementById('virtual-terminal-container');
    if (container) {
        window.virtualTerminal = new VirtualTerminalUI('virtual-terminal-container');
    }
});