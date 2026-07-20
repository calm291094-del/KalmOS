// KALM OS v4.3 - Internal Browser (COMPLETO Y FUNCIONAL)

let browserHistory = [];
let browserIndex = -1;

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
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>⛔ Sitio no compatible</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body {
                        background: #0a0514;
                        color: #e6e6fa;
                        font-family: 'Segoe UI', sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        padding: 20px;
                    }
                    .container {
                        background: rgba(26,0,51,0.8);
                        border: 2px solid #6a0dad;
                        border-radius: 16px;
                        padding: 40px;
                        max-width: 500px;
                        text-align: center;
                    }
                    .icon { font-size: 64px; margin-bottom: 20px; }
                    h2 { color: #da70d6; margin-bottom: 15px; }
                    p { color: #9370db; margin-bottom: 20px; line-height: 1.6; }
                    .url-box {
                        background: #0a0a1a;
                        padding: 12px;
                        border-radius: 8px;
                        word-break: break-all;
                        font-family: monospace;
                        color: #0f0;
                        font-size: 13px;
                        margin-bottom: 20px;
                    }
                    button {
                        background: #4b0082;
                        color: #fff;
                        border: 1px solid #9370db;
                        padding: 10px 24px;
                        border-radius: 8px;
                        cursor: pointer;
                        font-size: 14px;
                        transition: all 0.3s;
                        margin: 5px;
                    }
                    button:hover {
                        background: #6a0dad;
                        transform: scale(1.05);
                    }
                    .btn-external {
                        background: #008800;
                        border-color: #00cc44;
                    }
                    .btn-external:hover {
                        background: #00aa00;
                    }
                    .btn-back {
                        background: #4b0082;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">🔒</div>
                    <h2>Este sitio no se puede cargar en el navegador interno</h2>
                    <p>${url} utiliza medidas de seguridad que impiden su visualización en iframes.</p>
                    <div class="url-box">${url}</div>
                    <div>
                        <button class="btn-external" onclick="window.open('${url}', '_blank')">🔗 Abrir en nueva pestaña</button>
                        <button class="btn-back" onclick="history.back()">◀ Volver</button>
                    </div>
                    <p style="font-size:11px;color:#6a0dad;margin-top:20px">💡 Puedes configurar el proxy para redirigir este dominio</p>
                </div>
            </body>
            </html>
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
                container.innerHTML = '<span style="color:#9370db;font-size:11px">📖 Marcadores</span>';
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
                container.innerHTML = '<span style="color:#9370db;font-size:11px">📖 Sin marcadores</span>';
            }
            bookmarksLoading = false;
            bookmarksLoadedFlag = true;
        })
        .catch(err => {
            console.error('Error cargando bookmarks:', err);
            container.innerHTML = '<span style="color:#9370db;font-size:11px">📖 Marcadores</span>';
            bookmarksLoading = false;
            bookmarksLoadedFlag = true;
        });
}

document.addEventListener('DOMContentLoaded', function() {
    setupBrowserUrlInput();
    
    const observer = new MutationObserver(() => {
        const win = document.getElementById('win-browser');
        if (win && win.style.display !== 'none') {
            setTimeout(loadBrowserBookmarks, 300);
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    
    setTimeout(() => {
        const urlInput = document.getElementById('browser-url');
        if (urlInput && !urlInput.value) {
            const frame = document.getElementById('browser-frame');
            if (frame) {
                frame.srcdoc = `
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>🏰 Kalm Browser</title>
                        <style>
                            * { margin: 0; padding: 0; box-sizing: border-box; }
                            body {
                                background: linear-gradient(135deg, #0a0514 0%, #1a0033 100%);
                                color: #e6e6fa;
                                font-family: 'Segoe UI', sans-serif;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                height: 100vh;
                                padding: 20px;
                            }
                            .container {
                                text-align: center;
                                max-width: 600px;
                            }
                            .logo { font-size: 80px; margin-bottom: 20px; }
                            h1 { color: #da70d6; font-size: 28px; margin-bottom: 10px; }
                            p { color: #9370db; font-size: 14px; margin-bottom: 30px; }
                            .tips {
                                background: rgba(75,0,130,0.2);
                                border: 1px solid #4b0082;
                                border-radius: 12px;
                                padding: 20px;
                                text-align: left;
                            }
                            .tips h3 { color: #da70d6; margin-bottom: 10px; font-size: 14px; }
                            .tips li { color: #d8bfd8; margin: 8px 0; list-style: none; font-size: 13px; }
                            .tips li::before { content: "🔹 "; }
                            .info { color: #6a0dad; font-size: 11px; margin-top: 20px; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="logo">🏰</div>
                            <h1>Kalm Internal Browser</h1>
                            <p>Navegador integrado de Kalm OS v4.3</p>
                            <div class="tips">
                                <h3>💡 Consejos:</h3>
                                <li>Escribe una URL en la barra superior</li>
                                <li>Ej: <b>google.com</b> o <b>github.com</b></li>
                                <li>Usa marcadores para acceder rápido</li>
                                <li>Sitios como Google se abren en nueva pestaña</li>
                            </div>
                            <div class="info">🔒 Siempre seguro - Proxy integrado</div>
                        </div>
                    </body>
                    </html>
                `;
            }
            urlInput.value = 'https://kalmos.onrender.com';
        }
    }, 500);
});

window.browserNavigate = browserNavigate;
window.browserBack = browserBack;
window.browserForward = browserForward;
window.browserReload = browserReload;
window.browserOpenExternal = browserOpenExternal;
window.loadBrowserBookmarks = loadBrowserBookmarks;
window.sanitizeUrl = sanitizeUrl;
window.isBlockedInIframe = isBlockedInIframe;
window.isLocalPath = isLocalPath;

console.log('🌐 Internal Browser cargado');
