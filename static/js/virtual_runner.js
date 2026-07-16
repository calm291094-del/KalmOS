// Virtual Runner - UI para ejecutar y ver documentos

function openVirtualFile(path) {
    const ext = path.split('.').pop().toLowerCase();
    
    // Archivos de texto
    if (['txt', 'md', 'log', 'py', 'js', 'html', 'css', 'json', 'xml', 'yaml'].includes(ext)) {
        fetch(`/api/run?path=${encodeURIComponent(path)}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({path: path})
        })
        .then(r => r.json())
        .then(data => {
            if (data.ok && data.html_path) {
                window.open(`/api/viewer?path=${encodeURIComponent(data.html_path)}`, '_blank');
            } else {
                alert('Error abriendo archivo');
            }
        });
        return;
    }
    
    // PDF
    if (ext === 'pdf') {
        fetch(`/api/run?path=${encodeURIComponent(path)}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({path: path})
        })
        .then(r => r.json())
        .then(data => {
            if (data.ok && data.html_path) {
                window.open(`/api/viewer?path=${encodeURIComponent(data.html_path)}`, '_blank');
            } else {
                alert('Error abriendo PDF');
            }
        });
        return;
    }
    
    // Imágenes
    if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'].includes(ext)) {
        fetch(`/api/run?path=${encodeURIComponent(path)}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({path: path})
        })
        .then(r => r.json())
        .then(data => {
            if (data.ok && data.html_path) {
                window.open(`/api/viewer?path=${encodeURIComponent(data.html_path)}`, '_blank');
            } else {
                alert('Error abriendo imagen');
            }
        });
        return;
    }
    
    // Ejecutable
    if (['exe', 'bat', 'cmd', 'sh', 'py', 'com'].includes(ext)) {
        fetch(`/api/run?path=${encodeURIComponent(path)}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({path: path})
        })
        .then(r => r.json())
        .then(data => {
            if (data.ok) {
                alert(data.message || 'Programa ejecutado en entorno virtual');
                // Actualizar lista de procesos
                if (data.long_running) {
                    loadServers();
                }
            } else {
                alert('Error: ' + (data.error || 'desconocido'));
            }
        });
        return;
    }
    
    alert(`Tipo de archivo no soportado: ${ext}`);
}

// Botón para ejecutar en el explorador
function addVirtualRunButton(item) {
    if (item.is_dir) return;
    
    const ext = item.name.split('.').pop().toLowerCase();
    const executableExts = ['exe', 'bat', 'cmd', 'sh', 'py', 'com'];
    const viewableExts = ['txt', 'md', 'log', 'pdf', 'jpg', 'jpeg', 'png', 'gif'];
    
    if (executableExts.includes(ext) || viewableExts.includes(ext)) {
        return `<button class="act small" onclick="openVirtualFile('${item.path}')">
            ${executableExts.includes(ext) ? '▶️ Ejecutar' : '👁️ Ver'}
        </button>`;
    }
    return '';
}