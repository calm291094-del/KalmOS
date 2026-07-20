// KALM OS v4.3 - Internal Browser (COMPLETO Y CORREGIDO)

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

// ═══ SOPORTE PARA RUTAS LOCALES ═══
function isLocalPath(url) {
    return url.startsWith('/') || url.startsWith('#') || url.startsWith('?');
}

// ═══ VALIDAR Y CORREGIR URL ═══
function sanitizeUrl(url) {
    if (!url || url.trim() === '') return null;
    
    url = url.trim();
    
    // Si ya tiene http:// o https://, devolverlo
    if (url.startsWith('http://') || url.startsWith('https://')) {
        return url;
    }
    
    // Si es una ruta local (empieza con /)
    if (isLocalPath(url)) {
        return url;
    }
    
    // Si es un dominio sin protocolo
    if (url.includes('.')) {
        return 'https://' + url;
    }
    
    // Si es solo una palabra (ej: google), agregar .com
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
    
    // Sanitizar URL
    const url = sanitizeUrl(rawUrl);
    if (!url) {
        if (status) status.textContent = '❌ URL inválida';
        return;
    }
    
    // Actualizar barra con URL corregida
    urlInput.value = url;
    
    // Si es una ruta local
    if (isLocalPath(url)) {
        frame.src = url;
        if (status) status.textContent = '✅ Cargando local: ' + url;
        browserHistory.push(url);
        browserIndex = browserHistory.length - 1;
        
        // Si es /api/kalm/, verificar estado
        if (url.startsWith('/api/kalm')) {
            if (status) status.textContent = '🧠 Cargando Kalm AI...';
            setTimeout(function() {
                if (typeof checkKalmAIStatus === 'function') {
                    checkKalmAIStatus();
                }
            }, 2000);
        }
        return;
    }
    
    // Verificar si la URL es válida
    try {
        new URL(url);
    } catch (e) {
        if (status) status.textContent = '❌ URL inválida: ' + url;
        return;
    }
    
    // ═══ VERIFICAR SI EL SITIO ESTÁ BLOQUEADO EN IFRAME ═══
    if (isBlockedInIframe(url)) {
        // Mostrar mensaje en el iframe
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
        
        // Guardar en historial
        browserHistory.push(url);
        browserIndex = browserHistory.length - 1;
        return;
    }
    
    // Guardar en historial
    browserHistory.push(url);
    browserIndex = browserHistory.length - 1;
    
    if (status) status.textContent = '⏳ Cargando...';
    
    // Mostrar mensaje si es HTTP
    if (url.startsWith('http://')) {
        if (status) status.textContent = '⚠️ Cargando contenido HTTP (no seguro)...';
    }
    
    // Cargar directamente en el iframe
    frame.src = url;
    
    // Intentar cargar via proxy
    fetch('/api/browser/fetch?url=' + encodeURIComponent(url))
        .then(r => {
            if (!r.ok) throw new Error('Error en la respuesta');
            return r.json();
        })
        .then(data => {
            if (data.ok && data.content) {
                // Si el proxy devuelve contenido, mostrarlo
                frame.srcdoc = data.content;
                if (status) status.textContent = `✅ Cargado (${data.size || 0} bytes)`;
            }
        })
        .catch(() => {
            // El iframe ya está cargando la URL
            if (status) status.textContent = `🌐 Cargando...`;
        });
}

// ═══ VERIFICAR ESTADO DE KALM AI DESDE EL NAVEGADOR ═══
function checkKalmAIStatus() {
    let attempts = 0;
    const maxAttempts = 30;
    const status = document.getElementById('browser-status');
    
    if (status) {
        status.textContent = '🧠 Verificando Kalm AI...';
        status.style.color = '#ffaa00';
    }
    
    const checkInterval = setInterval(() => {
        attempts++;
        fetch('/api/kalm/health')
            .then(r => {
                if (r.ok) {
                    clearInterval(checkInterval);
                    if (status) {
                        status.textContent = '🧠 Kalm AI - Listo';
                        status.style.color = '#00cc66';
                    }
                    // Recargar el frame
                    const frame = document.getElementById('browser-frame');
                    if (frame && frame.src.includes('/api/kalm/')) {
                        frame.src = '/api/kalm/';
                    }
                    if (typeof showNotification === 'function') {
                        showNotification('✅ Kalm AI listo', 'success');
                    }
                } else if (attempts >= maxAttempts) {
                    clearInterval(checkInterval);
                    if (status) {
                        status.textContent = '⚠️ Kalm AI no responde';
                        status.style.color = '#ffaa00';
                    }
                    // Mostrar mensaje en el iframe
                    const frame = document.getElementById('browser-frame');
                    if (frame) {
                        frame.srcdoc = `
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <meta charset="UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <title>🧠 Kalm AI</title>
                                <style>
                                    body {
                                        background: #0a0514;
                                        color: #e6e6fa;
                                        font-family: 'Segoe UI', sans-serif;
                                        display: flex;
                                        justify-content: center;
                                        align-items: center;
                                        height: 100vh;
                                        flex-direction: column;
                                        padding: 20px;
                                    }
                                    .icon { font-size: 64px; margin-bottom: 20px; }
                                    h2 { color: #da70d6; }
                                    p { color: #9370db; }
                                    .btn {
                                        background: linear-gradient(135deg, #6a0dad, #9370db);
                                        color: white;
                                        border: none;
                                        padding: 12px 30px;
                                        border-radius: 10px;
                                        font-size: 16px;
                                        cursor: pointer;
                                        margin-top: 20px;
                                        transition: all 0.3s;
                                    }
                                    .btn:hover { transform: scale(1.05); }
                                </style>
                            </head>
                            <body>
                                <div class="icon">🧠</div>
                                <h2>Kalm AI no está disponible</h2>
                                <p>Haz clic en "Kalm AI" en el escritorio para iniciarlo</p>
                                <button class="btn" onclick="window.location.href='/desktop'">🏰 Ir al escritorio</button>
                            </body>
                            </html>
                        `;
                    }
                }
            })
            .catch(() => {
                if (attempts >= maxAttempts) {
                    clearInterval(checkInterval);
                    if (status) {
                        status.textContent = '⚠️ Kalm AI no disponible';
                        status.style.color = '#ff4444';
                    }
                }
            });
    }, 2000);
}

// ═══ LIMPIAR URL AL PRESIONAR ENTER ═══
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

// ═══ Cargar marcadores ═══
function loadBrowserBookmarks() {
    const container = document.getElementById('browser-bookmarks');
    if (!container) return;
    
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
            // Mostrar página de inicio
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

// Exportar funciones
window.browserNavigate = browserNavigate;
window.browserBack = browserBack;
window.browserForward = browserForward;
window.browserReload = browserReload;
window.browserOpenExternal = browserOpenExternal;
window.loadBrowserBookmarks = loadBrowserBookmarks;
window.sanitizeUrl = sanitizeUrl;
window.isBlockedInIframe = isBlockedInIframe;
window.isLocalPath = isLocalPath;
window.checkKalmAIStatus = checkKalmAIStatus;

console.log('🌐 Internal Browser cargado - Sitios bloqueados en iframe manejados');