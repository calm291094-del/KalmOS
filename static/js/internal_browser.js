// KALM OS v4.3 - Internal Browser (COMPLETO Y CORREGIDO)

let browserHistory = [];
let browserIndex = -1;

// Usar las variables globales de app.js
// bookmarksLoadedFlag y bookmarksLoading

function browserNavigate() {
    const urlInput = document.getElementById('browser-url');
    const frame = document.getElementById('browser-frame');
    const status = document.getElementById('browser-status');
    
    if (!urlInput || !frame) return;
    
    let url = urlInput.value.trim();
    if (!url) return;
    
    // Si es una ruta local, cargar directamente
    if (url.startsWith('/') || url.startsWith('#')) {
        frame.src = url;
        if (status) status.textContent = '✅ Cargado';
        return;
    }
    
    // Añadir http:// si no tiene protocolo
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'http://' + url;
    }
    
    // Guardar en historial
    browserHistory.push(url);
    browserIndex = browserHistory.length - 1;
    
    if (status) status.textContent = '⏳ Cargando...';
    
    // Cargar directamente en el iframe
    frame.src = url;
    
    // Intentar cargar via proxy para contenido
    fetch('/api/browser/fetch?url=' + encodeURIComponent(url))
        .then(r => r.json())
        .then(data => {
            if (data.ok) {
                frame.srcdoc = data.content;
                if (status) status.textContent = `✅ Cargado (${data.size || 0} bytes)`;
            } else {
                if (status) status.textContent = `⚠️ Cargando directamente`;
            }
        })
        .catch(() => {
            if (status) status.textContent = `⚠️ Cargando directamente`;
        });
}

function browserBack() {
    if (browserIndex > 0) {
        browserIndex--;
        const url = browserHistory[browserIndex];
        document.getElementById('browser-url').value = url;
        browserNavigate();
    } else {
        const frame = document.getElementById('browser-frame');
        if (frame && frame.contentWindow) {
            frame.contentWindow.history.back();
        }
    }
}

function browserForward() {
    if (browserIndex < browserHistory.length - 1) {
        browserIndex++;
        const url = browserHistory[browserIndex];
        document.getElementById('browser-url').value = url;
        browserNavigate();
    } else {
        const frame = document.getElementById('browser-frame');
        if (frame && frame.contentWindow) {
            frame.contentWindow.history.forward();
        }
    }
}

function browserReload() {
    const frame = document.getElementById('browser-frame');
    if (frame) {
        frame.src = frame.src;
    }
}

function browserOpenExternal() {
    const urlInput = document.getElementById('browser-url');
    if (urlInput && urlInput.value) {
        window.open(urlInput.value, '_blank');
    }
}

// ═══ Cargar marcadores (usa variables globales de app.js) ═══
function loadBrowserBookmarks() {
    const container = document.getElementById('browser-bookmarks');
    if (!container) return;
    
    // Usar las variables globales de app.js
    if (typeof bookmarksLoadedFlag !== 'undefined' && bookmarksLoadedFlag) return;
    if (typeof bookmarksLoading !== 'undefined' && bookmarksLoading) return;
    
    if (typeof bookmarksLoading !== 'undefined') {
        bookmarksLoading = true;
    }
    
    fetch('/api/browser/bookmarks')
        .then(r => {
            if (!r.ok) {
                container.innerHTML = '<span style="color:#9370db;font-size:11px">📖 Marcadores</span>';
                if (typeof bookmarksLoading !== 'undefined') bookmarksLoading = false;
                if (typeof bookmarksLoadedFlag !== 'undefined') bookmarksLoadedFlag = true;
                return;
            }
            return r.json();
        })
        .then(bookmarks => {
            container.innerHTML = '';
            
            if (bookmarks && bookmarks.length > 0) {
                bookmarks.forEach(bm => {
                    const btn = document.createElement('button');
                    btn.className = 'act small';
                    btn.textContent = `${bm.icon || '🌐'} ${bm.name}`;
                    btn.style.cssText = 'background:rgba(75,0,130,0.3);border-color:#6a0dad;margin:2px';
                    btn.onclick = function() {
                        const urlInput = document.getElementById('browser-url');
                        if (urlInput) {
                            urlInput.value = bm.url || bm.domain;
                            browserNavigate();
                        }
                    };
                    container.appendChild(btn);
                });
            } else {
                container.innerHTML = '<span style="color:#9370db;font-size:11px">📖 Sin marcadores</span>';
            }
            if (typeof bookmarksLoading !== 'undefined') bookmarksLoading = false;
            if (typeof bookmarksLoadedFlag !== 'undefined') bookmarksLoadedFlag = true;
        })
        .catch(err => {
            console.error('Error cargando bookmarks:', err);
            container.innerHTML = '<span style="color:#9370db;font-size:11px">📖 Marcadores</span>';
            if (typeof bookmarksLoading !== 'undefined') bookmarksLoading = false;
            if (typeof bookmarksLoadedFlag !== 'undefined') bookmarksLoadedFlag = true;
        });
}

// ═══ Inicializar ═══
document.addEventListener('DOMContentLoaded', function() {
    // Cargar marcadores cuando se abre la ventana
    const observer = new MutationObserver(() => {
        const win = document.getElementById('win-browser');
        if (win && win.style.display !== 'none') {
            setTimeout(loadBrowserBookmarks, 300);
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Cargar URL por defecto
    setTimeout(() => {
        const urlInput = document.getElementById('browser-url');
        if (urlInput && !urlInput.value) {
            urlInput.value = '/desktop';
        }
    }, 500);
});