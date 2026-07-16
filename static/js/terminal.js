// KALM OS v4.3 - Terminal

let termHistory = [];
let termIndex = -1;

function termExec() {
    const input = document.getElementById('term-in');
    const output = document.getElementById('term-out');
    if (!input || !output) return;
    
    const cmd = input.value.trim();
    if (!cmd) return;
    
    // Agregar al historial
    termHistory.push(cmd);
    termIndex = termHistory.length;
    input.value = '';
    
    // Mostrar comando
    output.innerHTML += `<span style="color:#0f0">kalm@os:~$</span> <span style="color:#fff">${cmd}</span>\n`;
    
    // Procesar comando
    processCommand(cmd, output);
    
    // Scroll al final
    output.scrollTop = output.scrollHeight;
}

function processCommand(cmd, output) {
    const parts = cmd.split(' ');
    const command = parts[0].toLowerCase();
    const args = parts.slice(1);
    
    switch (command) {
        case 'help':
            showHelp(output);
            break;
        case 'ls':
        case 'dir':
            listFiles(output, args);
            break;
        case 'cd':
            changeDir(output, args);
            break;
        case 'pwd':
            output.innerHTML += `<span style="color:#9370db">${currentPath || '/D'}</span>\n`;
            break;
        case 'clear':
        case 'cls':
            output.innerHTML = '';
            break;
        case 'echo':
            output.innerHTML += args.join(' ') + '\n';
            break;
        case 'whoami':
            output.innerHTML += '<span style="color:#0f0">kalm@os</span>\n';
            break;
        case 'date':
            output.innerHTML += new Date().toString() + '\n';
            break;
        case 'run':
            if (args.length > 0) {
                openVirtualFile(args[0]);
                output.innerHTML += `<span style="color:#ffa500">▶️ Ejecutando: ${args[0]}</span>\n`;
            } else {
                output.innerHTML += '<span style="color:#ff6b6b">❌ Especifica un archivo</span>\n';
            }
            break;
        case 'open':
            if (args.length > 0) {
                window.open(args[0], '_blank');
                output.innerHTML += `<span style="color:#ffa500">🌐 Abriendo: ${args[0]}</span>\n`;
            }
            break;
        case 'stats':
            fetch('/api/system-stats')
                .then(r => r.json())
                .then(data => {
                    output.innerHTML += `
                        <span style="color:#9370db">📊 Estadísticas del sistema:</span>
                        🖥️ CPU: ${data.cpu}%
                        💾 RAM: ${data.ram_used} / ${data.ram_total}
                        💿 Disco: ${data.disk_used} / ${data.disk_total}
                        ⚙️ Procesos: ${data.processes}
                    `.replace(/\n/g, ' ').replace(/\s+/g, ' ') + '\n';
                });
            break;
        case 'exit':
            output.innerHTML += '<span style="color:#9370db">👋 Hasta luego!</span>\n';
            setTimeout(() => closeWin('console'), 1000);
            break;
        default:
            output.innerHTML += `<span style="color:#ff6b6b">❌ Comando no encontrado: ${command}</span>\n`;
            output.innerHTML += '<span style="color:#9370db">💡 Escribe "help" para ver los comandos disponibles</span>\n';
    }
}

function showHelp(output) {
    output.innerHTML += `
        <span style="color:#da70d6;font-weight:bold">📖 Comandos disponibles:</span>
        <span style="color:#9370db">help</span> - Muestra esta ayuda
        <span style="color:#9370db">ls / dir</span> - Lista archivos
        <span style="color:#9370db">cd [carpeta]</span> - Cambia de directorio
        <span style="color:#9370db">pwd</span> - Muestra el directorio actual
        <span style="color:#9370db">echo [texto]</span> - Muestra texto
        <span style="color:#9370db">whoami</span> - Muestra el usuario
        <span style="color:#9370db">date</span> - Muestra la fecha y hora
        <span style="color:#9370db">run [archivo]</span> - Ejecuta un archivo
        <span style="color:#9370db">open [url]</span> - Abre URL en navegador
        <span style="color:#9370db">stats</span> - Muestra estadísticas del sistema
        <span style="color:#9370db">clear / cls</span> - Limpia la terminal
        <span style="color:#9370db">exit</span> - Cierra la terminal
    `.replace(/\n/g, ' ').replace(/\s+/g, ' ') + '\n';
}

function listFiles(output, args) {
    const path = args[0] || currentPath || '/D';
    
    fetch(`/api/files?path=${encodeURIComponent(path)}`)
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                output.innerHTML += `<span style="color:#ff6b6b">❌ ${data.error}</span>\n`;
                return;
            }
            
            if (!data.items || data.items.length === 0) {
                output.innerHTML += '<span style="color:#9370db">📂 Carpeta vacía</span>\n';
                return;
            }
            
            let html = '';
            data.items.forEach(item => {
                const icon = item.is_dir ? '📁' : (item.icon || '📄');
                const size = item.is_dir ? '<DIR>' : (item.size_fmt || '-');
                html += `${icon} ${item.name} <span style="color:#9370db">${size}</span>\n`;
            });
            output.innerHTML += html;
        })
        .catch(() => {
            output.innerHTML += '<span style="color:#ff6b6b">❌ Error listando archivos</span>\n';
        });
}

function changeDir(output, args) {
    if (args.length === 0) {
        output.innerHTML += '<span style="color:#9370db">📁 Directorio actual</span>\n';
        return;
    }
    
    const path = args[0];
    if (path === '..') {
        if (currentPath) {
            const parts = currentPath.split('/');
            parts.pop();
            currentPath = parts.join('/') || '/D';
            loadFiles(currentPath);
            output.innerHTML += `<span style="color:#9370db">📁 ${currentPath}</span>\n`;
        }
        return;
    }
    
    // Verificar si existe
    fetch(`/api/files?path=${encodeURIComponent(path)}`)
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                output.innerHTML += `<span style="color:#ff6b6b">❌ ${data.error}</span>\n`;
            } else {
                currentPath = path;
                loadFiles(path);
                output.innerHTML += `<span style="color:#9370db">📁 ${path}</span>\n`;
            }
        });
}

// ═══ Historial con flechas ═══
document.addEventListener('keydown', (e) => {
    const input = document.getElementById('term-in');
    if (!input || document.activeElement !== input) return;
    
    if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (termIndex > 0) {
            termIndex--;
            input.value = termHistory[termIndex] || '';
        }
    } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (termIndex < termHistory.length - 1) {
            termIndex++;
            input.value = termHistory[termIndex] || '';
        } else {
            termIndex = termHistory.length;
            input.value = '';
        }
    }
});

// ═══ Autocompletar ═══
document.addEventListener('keydown', (e) => {
    const input = document.getElementById('term-in');
    if (!input || document.activeElement !== input || e.key !== 'Tab') return;
    
    e.preventDefault();
    const cmd = input.value.trim();
    if (!cmd) return;
    
    const commands = ['help', 'ls', 'dir', 'cd', 'pwd', 'clear', 'cls', 'echo', 'whoami', 'date', 'run', 'open', 'stats', 'exit'];
    const matches = commands.filter(c => c.startsWith(cmd));
    
    if (matches.length === 1) {
        input.value = matches[0] + ' ';
    } else if (matches.length > 1) {
        // Mostrar sugerencias
        const output = document.getElementById('term-out');
        output.innerHTML += `<span style="color:#9370db">Sugerencias: ${matches.join(', ')}</span>\n`;
        output.scrollTop = output.scrollHeight;
    }
});