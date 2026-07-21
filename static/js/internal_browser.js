// KALM OS v4.3 - Internal Browser (COMPLETO Y FUNCIONAL)

let browserHistory = [];
let browserIndex = -1;
let bookmarksLoadedFlag = false;
let bookmarksLoading = false;

// ═══ SITIOS QUE NO FUNCIONAN EN IFRAME ═══
const BLOCKED_IFRAME_SITES = [
    'google.com', 'google.es', 'google.', 'www.google',
    'youtube.com', 'youtu.be',
    'facebook.com', 'fb.com',
    'twitter.com', 'x.com',
    'instagram.com',
    'linkedin.com',
    'gmail.com', 'mail.google.com',
    'drive.google.com',
    'docs.google.com',
    'accounts.google.com',
    'play.google.com',
    'maps.google.com',
    'calendar.google.com'
];

function isBlockedInIframe(url) {
    if (!url) return false;
    const urlLower = url.toLowerCase();
    for (const site of BLOCKED_IFRAME_SITES) {
        if (urlLower.includes(site)) {
            return true;
        }
    }
    return false;
}

function isLocalPath(url) {
    return url.startsWith('/') || url.startsWith('#') || url.startsWith('?');
}

function sanitizeUrl(url) {
    if (!url || url.trim() === '') return null;
    
    url = url.trim();
    
    if (url.startsWith('http://') || url.startsWith('https://')) {
        return url;
    }
    
    if (isLocalPath(url)) {
        return url;
    }
    
    if (url.includes('.')) {
        return 'https://' + url;
    }
    
    return 'https://' + url + '.com';
}

function browserNavigate() {
    const urlInput = document.getElementById('browser-url');
    const frame = document.getElementById('browser-frame');
    const status = document.getElementById('browser-status');
    
    if (!urlInput || !frame) return;
    
    let rawUrl = urlInput.value.trim();
    if (!rawUrl) {
        if (status) status.textContent = '⚠️ Ingresa una URL';
        return;
    }
    
    const url = sanitizeUrl(rawUrl);
    if (!url) {
        if (status) status.textContent = '❌ URL inválida';
        return;
    }
    
    urlInput.value = url;
    
    if (isLocalPath(url)) {
        frame.src = url;
        if (status) status.textContent = '✅ Cargando local: ' + url;
        browserHistory.push(url);
        browserIndex = browserHistory.length - 1;
        return;
    }
    
    try {
        new URL(url);
    } catch (e) {
        if (status) status.textContent = '❌ URL inválida: ' + url;
        return;
    }
    
    if (isBlockedInIframe(url)) {
        frame.srcdoc = `
            <div style="text-align:center; padding: 40px; font-family: sans-serif;">
                <h2>🔒 Este sitio no se puede cargar en el navegador interno</h2>
                <p><strong>${url}</strong> utiliza medidas de seguridad que impiden su visualización en iframes.</p>
                <br>
                <a href="${url}" target="_blank" style="padding: 10px 20px; background: #6a0dad; color: white; text-decoration: none; border-radius: 5px;">🔗 Abrir en nueva pestaña</a>
                <br><br>
                <button onclick="window.history.back()" style="padding: 8px 16px; cursor: pointer;">◀ Volver</button>
                <br><br>
                <small>💡 Puedes configurar el proxy para redirigir este dominio</small>
            </div>
        `;
        if (status) status.textContent = '⛔ Sitio no compatible con iframe';
        browserHistory.push(url);
        browserIndex = browserHistory.length - 1;
        return;
    }
    
    browserHistory.push(url);
    browserIndex = browserHistory.length - 1;
    
    if (status) status.textContent = '⏳ Cargando...';
    if (url.startsWith('http://')) {
        if (status) status.textContent = '⚠️ Cargando contenido HTTP (no seguro)...';
    }
    
    frame.src = url;
    
    fetch('/api/browser/fetch?url=' + encodeURIComponent(url))
        .then(r => {
            if (!r.ok) throw new Error('Error en la respuesta');
            return r.json();
        })
        .then(data => {
            if (data.ok && data.content) {
                frame.srcdoc = data.content;
                if (status) status.textContent = `✅ Cargado (${data.size || 0} bytes)`;
            }
        })
        .catch(() => {
            if (status) status.textContent = `🌐 Cargando...`;
        });
}

function setupBrowserUrlInput() {
    const urlInput = document.getElementById('browser-url');
    if (!urlInput) return;
    
    urlInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            browserNavigate();
        }
    });
    
    urlInput.addEventListener('blur', function() {
        if (this.value.trim()) {
            const sanitized = sanitizeUrl(this.value.trim());
            if (sanitized && sanitized !== this.value) {
                this.value = sanitized;
            }
        }
    });
}

function browserBack() {
    if (browserIndex > 0) {
        browserIndex--;
        const url = browserHistory[browserIndex];
        const urlInput = document.getElementById('browser-url');
        if (urlInput) urlInput.value = url;
        browserNavigate();
    } else {
        const frame = document.getElementById('browser-frame');
        if (frame && frame.contentWindow) {
            try {
                frame.contentWindow.history.back();
            } catch (e) {}
        }
    }
}

function browserForward() {
    if (browserIndex < browserHistory.length - 1) {
        browserIndex++;
        const url = browserHistory[browserIndex];
        const urlInput = document.getElementById('browser-url');
        if (urlInput) urlInput.value = url;
        browserNavigate();
    } else {
        const frame = document.getElementById('browser-frame');
        if (frame && frame.contentWindow) {
            try {
                frame.contentWindow.history.forward();
            } catch (e) {}
        }
    }
}

function browserReload() {
    const frame = document.getElementById('browser-frame');
    if (frame) {
        const currentSrc = frame.src;
        if (currentSrc && currentSrc !== 'about:blank') {
            frame.src = currentSrc;
        } else {
            const urlInput = document.getElementById('browser-url');
            if (urlInput && urlInput.value.trim()) {
                browserNavigate();
            }
        }
    }
}

function browserOpenExternal() {
    const urlInput = document.getElementById('browser-url');
    if (urlInput && urlInput.value) {
        const url = sanitizeUrl(urlInput.value.trim());
        if (url) {
            window.open(url, '_blank');
        }
    }
}

function loadBrowserBookmarks() {
    const container = document.getElementById('browser-bookmarks');
    if (!container) return;
    
    if (bookmarksLoadedFlag) return;
    if (bookmarksLoading) return;
     
    bookmarksLoading = true;
    
    fetch('/api/browser/bookmarks')
        .then(r => {
            if (!r.ok) {
                container.innerHTML = '📖 Marcadores';
                bookmarksLoading = false;
                bookmarksLoadedFlag = true;
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
                            let url = bm.url || bm.domain;
                            if (url && !url.startsWith('http://') && !url.startsWith('https://') && !isLocalPath(url)) {
                                url = 'https://' + url;
                            }
                            urlInput.value = url;
                            browserNavigate();
                        }
                    };
                    container.appendChild(btn);
                });
            } else {
                container.innerHTML = '📖 Sin marcadores';
            }
            bookmarksLoading = false;
            bookmarksLoadedFlag = true;
        })
        .catch(err => {
            console.error('Error cargando bookmarks:', err);
            container.innerHTML = '📖 Marcadores';
            bookmarksLoading = false;
            bookmarksLoadedFlag = true;
        });
}

// ═══ Inicializar ═══
document.addEventListener('DOMContentLoaded', function() {
    setupBrowserUrlInput();
    
    const observer = new MutationObserver(() => {
        const win = document.getElementById('win-browser');
        if (win && win.style.display !== 'none') {
            setTimeout(loadBrowserBookmarks, 300);
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
});

// ═══ FUNCIÓN PARA FORZAR CARGA DE KALM AI ═══
function forceLoadKalmAI() {
    console.log('🔄 Force loading Kalm AI...');
    
    const frame = document.getElementById('browser-frame');
    const urlInput = document.getElementById('browser-url');
    const status = document.getElementById('browser-status');
    
    if (!frame) {
        console.error('❌ Frame no encontrado');
        return;
    }
    
    // ═══ USAR /api/kalm/ QUE FUNCIONABA ANTES ═══
    const kalmUrl = '/api/kalm/';
    
    if (urlInput) {
        urlInput.value = kalmUrl;
    }
    
    if (status) {
        status.textContent = '🧠 Cargando Kalm AI...';
        status.style.color = '#ffaa00';
    }
    
    frame.srcdoc = '';
    frame.src = 'about:blank';
    
    setTimeout(function() {
        frame.src = kalmUrl;
        console.log('✅ Frame cargado con ' + kalmUrl);
    }, 200);
    
    setTimeout(function() {
        if (frame.contentDocument && frame.contentDocument.body) {
            var bodyText = frame.contentDocument.body.innerText || '';
            if (bodyText.includes('Kalm AI') || bodyText.includes('Chat Academico')) {
                if (status) {
                    status.textContent = '✅ Kalm AI cargado';
                    status.style.color = '#00cc66';
                }
            }
        }
    }, 3000);
    
    fetch('/api/kalm/health')
        .then(function(r) {
            if (r.ok) {
                console.log('✅ Kalm AI health check OK');
                if (status) {
                    status.textContent = '✅ Kalm AI - Listo';
                    status.style.color = '#00cc66';
                }
            }
        })
        .catch(function() {
            console.log('⚠️ Kalm AI health check falló');
        });
}

window.browserNavigate = browserNavigate;
window.browserBack = browserBack;
window.browserForward = browserForward;
window.browserReload = browserReload;
window.browserOpenExternal = browserOpenExternal;
window.loadBrowserBookmarks = loadBrowserBookmarks;
window.sanitizeUrl = sanitizeUrl;
window.isBlockedInIframe = isBlockedInIframe;
window.isLocalPath = isLocalPath;
window.forceLoadKalmAI = forceLoadKalmAI;

console.log('🌐 Internal Browser cargado');