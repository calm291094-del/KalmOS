// KALM OS v4.3 - Internal Browser (Versión Corregida - Sin sandbox para same-origin)

window.browserTabs = window.browserTabs || [];
window.activeTabId = window.activeTabId || null;
window.tabCounter = window.tabCounter || 0;
window.bookmarksLoadedFlag = window.bookmarksLoadedFlag || false;
window.bookmarksLoading = window.bookmarksLoading || false;

// ═══ INYECTAR CSS MODERNO ═══
function injectBrowserCSS() {
    if (document.getElementById('browser-custom-css')) return;
    const style = document.createElement('style');
    style.id = 'browser-custom-css';
    style.textContent = `
        /* ═══ NUNCA poner display en #win-browser para no romper minimize/close ═══ */
        /* Aplicar flex solo al window-body del navegador ═══ */
        #win-browser > .window-body {
            display: flex !important;
            flex-direction: column !important;
            overflow: hidden !important;
            min-height: 0 !important;
        }

        .browser-tabs-container {
            display: flex; background: rgba(20, 10, 40, 0.95); padding: 8px 8px 0 8px; gap: 4px;
            border-bottom: 1px solid #4b0082; overflow-x: auto; flex-shrink: 0;
        }
        .browser-tabs-container::-webkit-scrollbar { height: 3px; }
        .browser-tabs-container::-webkit-scrollbar-thumb { background: #6a0dad; border-radius: 2px; }
        .browser-tab {
            display: flex; align-items: center; background: rgba(75, 0, 130, 0.3); color: #d8bfd8;
            padding: 8px 12px; border-radius: 8px 8px 0 0; font-size: 12px; cursor: pointer;
            max-width: 200px; min-width: 100px; border: 1px solid transparent;
            transition: all 0.2s; flex-shrink: 0;
        }
        .browser-tab.active {
            background: rgba(106, 13, 173, 0.6); color: #fff; border-color: #6a0dad;
            border-bottom-color: rgba(106, 13, 173, 0.6);
        }
        .browser-tab:hover:not(.active) { background: rgba(75, 0, 130, 0.5); }
        .tab-icon { margin-right: 6px; flex-shrink: 0; }
        .tab-title { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .tab-close {
            margin-left: 8px; padding: 2px 6px; border-radius: 4px;
            font-size: 14px; line-height: 1; flex-shrink: 0;
        }
        .tab-close:hover { background: rgba(255, 68, 68, 0.3); color: #ff4444; }
        .browser-new-tab-btn {
            display: flex; align-items: center; justify-content: center;
            width: 28px; height: 28px; background: rgba(75, 0, 130, 0.3);
            color: #d8bfd8; border-radius: 6px; cursor: pointer;
            font-size: 18px; margin-bottom: 4px; flex-shrink: 0; transition: all 0.2s;
        }
        .browser-new-tab-btn:hover { background: rgba(75, 0, 130, 0.6); color: #fff; }

        .browser-iframe-container {
            flex: 1 1 0% !important;
            position: relative !important;
            background: #fff !important;
            overflow: hidden !important;
            min-height: 0 !important;
        }
        .browser-iframe {
            width: 100% !important;
            height: 100% !important;
            border: none !important;
            background: #fff !important;
            position: absolute !important;
            top: 0 !important; left: 0 !important;
            right: 0 !important; bottom: 0 !important;
            display: block !important;
        }

        .browser-error-overlay {
            position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: #0a0514; display: flex; flex-direction: column;
            align-items: center; justify-content: center; color: #9370db;
            font-size: 14px; padding: 20px; text-align: center; z-index: 5;
        }
        .browser-error-overlay .error-icon { font-size: 48px; margin-bottom: 12px; }
        .browser-error-overlay .error-msg { color: #ff4444; margin: 8px 0; font-size: 12px; max-width: 400px; }
        .browser-error-overlay .error-retry {
            margin-top: 16px; padding: 8px 20px; background: #6a0dad; color: #fff;
            border: none; border-radius: 6px; cursor: pointer; font-size: 13px;
        }
        .browser-error-overlay .error-retry:hover { background: #9b59b6; }
    `;
    document.head.appendChild(style);
}

// ═══ DETERMINAR SI ES SAME-ORIGIN ═══
function isSameOrigin(url) {
    if (!url) return true;
    if (url.startsWith('/') || url.startsWith('#')) return true;
    try {
        const parsed = new URL(url, window.location.origin);
        return parsed.origin === window.location.origin;
    } catch (e) {
        return false;
    }
}

// ═══ GESTIÓN DE PESTAÑAS ═══
function createTab(url, title, setActive) {
    url = url || '/api/kalm/';
    title = title || '🧠 Kalm AI';
    if (setActive === undefined) setActive = true;

    window.tabCounter++;
    const tabId = 'tab-' + window.tabCounter;
    window.browserTabs.push({ id: tabId, url: url, title: title, active: false });
    renderTabs();
    createIframeForTab(tabId, url);
    if (setActive) switchTab(tabId);
    return tabId;
}

function closeTab(tabId, event) {
    if (event) event.stopPropagation();
    const index = window.browserTabs.findIndex(function(t) { return t.id === tabId; });
    if (index === -1) return;

    // Limpiar iframe
    const iframe = document.getElementById('iframe-' + tabId);
    if (iframe) {
        iframe.src = 'about:blank';
        iframe.remove();
    }

    window.browserTabs.splice(index, 1);

    if (window.activeTabId === tabId) {
        if (window.browserTabs.length > 0) {
            var newIndex = Math.min(index, window.browserTabs.length - 1);
            switchTab(window.browserTabs[newIndex].id);
        } else {
            createTab('/api/kalm/', '🧠 Kalm AI', true);
        }
    }
    renderTabs();
}

function switchTab(tabId) {
    window.activeTabId = tabId;
    var tab = window.browserTabs.find(function(t) { return t.id === tabId; });
    if (!tab) return;

    // Ocultar todos los iframes
    document.querySelectorAll('.browser-iframe').forEach(function(iframe) {
        iframe.style.display = 'none';
    });
    // Ocultar todos los overlays de error
    document.querySelectorAll('.browser-error-overlay').forEach(function(el) {
        el.style.display = 'none';
    });

    var activeIframe = document.getElementById('iframe-' + tabId);
    if (!activeIframe) {
        createIframeForTab(tabId, tab.url);
        activeIframe = document.getElementById('iframe-' + tabId);
    }
    if (activeIframe) {
        activeIframe.style.display = 'block';
    }

    // Mostrar overlay de error si existe para esta tab
    var errorOverlay = document.getElementById('error-' + tabId);
    if (errorOverlay) {
        errorOverlay.style.display = 'flex';
    }

    var urlInput = document.getElementById('browser-url');
    if (urlInput) urlInput.value = tab.url;
    renderTabs();
}

function updateTabTitle(tabId, title) {
    var tab = window.browserTabs.find(function(t) { return t.id === tabId; });
    if (tab) {
        tab.title = title;
        renderTabs();
    }
}

function renderTabs() {
    var tabContainer = document.getElementById('browser-tabs-container');
    if (!tabContainer) {
        var browserWin = document.getElementById('win-browser');
        if (browserWin) {
            // Insertar después de la barra de navegación (toolbar)
            var toolbar = browserWin.querySelector('.browser-toolbar, .win-toolbar');
            tabContainer = document.createElement('div');
            tabContainer.id = 'browser-tabs-container';
            tabContainer.className = 'browser-tabs-container';
            if (toolbar && toolbar.nextSibling) {
                browserWin.insertBefore(tabContainer, toolbar.nextSibling);
            } else {
                browserWin.insertBefore(tabContainer, browserWin.firstChild);
            }
        }
    }
    if (!tabContainer) return;

    tabContainer.innerHTML = '';
    window.browserTabs.forEach(function(tab) {
        var tabEl = document.createElement('div');
        tabEl.className = 'browser-tab' + (tab.id === window.activeTabId ? ' active' : '');
        tabEl.setAttribute('data-tab-id', tab.id);
        tabEl.onclick = function() { switchTab(tab.id); };
        tabEl.innerHTML = '<span class="tab-icon">🌐</span><span class="tab-title">' + escapeHtml(tab.title) + '</span><span class="tab-close" onclick="closeTab(\'' + tab.id + '\', event)">✕</span>';
        tabContainer.appendChild(tabEl);
    });

    var newTabBtn = document.createElement('div');
    newTabBtn.className = 'browser-new-tab-btn';
    newTabBtn.innerHTML = '+';
    newTabBtn.title = 'Nueva Pestaña';
    newTabBtn.onclick = function() { createTab('/api/kalm/', '🧠 Kalm AI', true); };
    tabContainer.appendChild(newTabBtn);
}

function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

function createIframeForTab(tabId, url) {
    // Buscar el contenedor existente (ya está en desktop.html)
    var iframeContainer = document.getElementById('browser-iframe-container');
    if (!iframeContainer) {
        // Fallback: buscar dentro de win-browser
        var browserWin = document.getElementById('win-browser');
        if (browserWin) {
            var winBody = browserWin.querySelector('.window-body');
            if (winBody) {
                iframeContainer = document.createElement('div');
                iframeContainer.id = 'browser-iframe-container';
                iframeContainer.className = 'browser-iframe-container';
                // Insertar ANTES de la barra de estado (último hijo del window-body)
                var statusBar = winBody.lastElementChild;
                if (statusBar) {
                    winBody.insertBefore(iframeContainer, statusBar);
                } else {
                    winBody.appendChild(iframeContainer);
                }
            }
        }
    }
    if (!iframeContainer) return;

    // Eliminar iframe previo si existe
    var prevIframe = document.getElementById('iframe-' + tabId);
    if (prevIframe) prevIframe.remove();

    var iframe = document.createElement('iframe');
    iframe.id = 'iframe-' + tabId;
    iframe.className = 'browser-iframe';
    iframe.style.display = 'none';

    // Sin sandbox para same-origin (permite fetch, etc.)
    if (!isSameOrigin(url)) {
        iframe.sandbox = 'allow-scripts allow-forms allow-popups';
    }

    iframe.src = url;

    iframe.onload = function() {
        try {
            var docTitle = iframe.contentDocument.title;
            if (docTitle) updateTabTitle(tabId, docTitle);
            var errorOverlay = document.getElementById('error-' + tabId);
            if (errorOverlay) errorOverlay.style.display = 'none';
        } catch (e) {}
    };

    iframe.onerror = function() {
        showTabError(tabId, url, 'No se pudo cargar la página');
    };

    iframeContainer.appendChild(iframe);
}

function showTabError(tabId, url, message) {
    var iframeContainer = document.getElementById('browser-iframe-container');
    if (!iframeContainer) return;

    // Eliminar error previo
    var prevError = document.getElementById('error-' + tabId);
    if (prevError) prevError.remove();

    var overlay = document.createElement('div');
    overlay.id = 'error-' + tabId;
    overlay.className = 'browser-error-overlay';
    if (window.activeTabId !== tabId) {
        overlay.style.display = 'none';
    }
    overlay.innerHTML =
        '<div class="error-icon">⚠️</div>' +
        '<div>Error al cargar</div>' +
        '<div class="error-msg">' + escapeHtml(message) + '</div>' +
        '<div style="margin-top:8px;font-size:11px;color:#6a5acd;word-break:break-all;max-width:400px;">' + escapeHtml(url) + '</div>' +
        '<button class="error-retry" onclick="retryTab(\'' + tabId + '\')">🔄 Reintentar</button>';
    iframeContainer.appendChild(overlay);
}

function retryTab(tabId) {
    var tab = window.browserTabs.find(function(t) { return t.id === tabId; });
    if (!tab) return;

    // Eliminar error overlay
    var errorOverlay = document.getElementById('error-' + tabId);
    if (errorOverlay) errorOverlay.remove();

    // Recargar iframe
    var iframe = document.getElementById('iframe-' + tabId);
    if (iframe) {
        iframe.src = tab.url;
    } else {
        createIframeForTab(tabId, tab.url);
    }
}

// ═══ NAVEGACIÓN ═══
function browserNavigate() {
    var urlInput = document.getElementById('browser-url');
    if (!urlInput || !window.activeTabId) return;

    var url = urlInput.value.trim();
    if (!url) return;

    // Normalizar URL
    if (!url.startsWith('http://') && !url.startsWith('https://') && !url.startsWith('/') && !url.startsWith('#')) {
        url = url.includes('.') ? 'https://' + url : '/api/kalm/';
    }

    urlInput.value = url;

    var tab = window.browserTabs.find(function(t) { return t.id === window.activeTabId; });
    if (tab) {
        tab.url = url;
        tab.title = url.startsWith('/') ? '🧠 Kalm OS' : url.replace(/^https?:\/\//, '').split('/')[0];
        var iframe = document.getElementById('iframe-' + window.activeTabId);
        if (iframe) {
            // Actualizar sandbox según el nuevo URL
            if (isSameOrigin(url)) {
                iframe.removeAttribute('sandbox');
            } else {
                iframe.sandbox = 'allow-scripts allow-forms allow-popups';
            }
            iframe.src = url;
        } else {
            createIframeForTab(window.activeTabId, url);
        }
    }
    renderTabs();
}

function browserBack() {
    var iframe = document.getElementById('iframe-' + window.activeTabId);
    if (iframe && iframe.contentWindow) {
        try { iframe.contentWindow.history.back(); } catch (e) {}
    }
}

function browserForward() {
    var iframe = document.getElementById('iframe-' + window.activeTabId);
    if (iframe && iframe.contentWindow) {
        try { iframe.contentWindow.history.forward(); } catch (e) {}
    }
}

function browserReload() {
    var tab = window.browserTabs.find(function(t) { return t.id === window.activeTabId; });
    if (!tab) return;
    var iframe = document.getElementById('iframe-' + window.activeTabId);
    if (iframe) {
        iframe.src = iframe.src;
    } else {
        createIframeForTab(window.activeTabId, tab.url);
    }
}

function browserOpenExternal() {
    var urlInput = document.getElementById('browser-url');
    if (urlInput && urlInput.value) {
        window.open(urlInput.value.trim(), '_blank');
    }
}

// ═══ INICIALIZACIÓN ═══
document.addEventListener('DOMContentLoaded', function() {
    injectBrowserCSS();
    if (window.browserTabs.length === 0) {
        createTab('/api/kalm/', '🧠 Kalm AI', true);
    }

    var urlInput = document.getElementById('browser-url');
    if (urlInput) {
        urlInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                browserNavigate();
            }
        });
    }
    renderTabs();
    loadBrowserBookmarks();
});

function loadBrowserBookmarks() {
    var container = document.getElementById('browser-bookmarks');
    if (!container || window.bookmarksLoadedFlag || window.bookmarksLoading) return;
    window.bookmarksLoading = true;

    fetch('/api/browser/bookmarks')
        .then(function(r) { return r.ok ? r.json() : null; })
        .then(function(bookmarks) {
            container.innerHTML = '';
            if (bookmarks && bookmarks.length > 0) {
                bookmarks.forEach(function(bm) {
                    var btn = document.createElement('button');
                    btn.className = 'act small';
                    btn.textContent = (bm.icon || '🌐') + ' ' + bm.name;
                    btn.style.cssText = 'background:rgba(75,0,130,0.3);border-color:#6a0dad;margin:2px;cursor:pointer;';
                    btn.onclick = function() {
                        var urlInput = document.getElementById('browser-url');
                        if (urlInput) {
                            var url = bm.url || bm.domain || '';
                            if (url && !url.startsWith('http') && !url.startsWith('/') && !url.startsWith('#')) {
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
            window.bookmarksLoading = false;
            window.bookmarksLoadedFlag = true;
        })
        .catch(function() {
            container.innerHTML = '<span style="color:#9370db;font-size:11px">📖 Marcadores</span>';
            window.bookmarksLoading = false;
            window.bookmarksLoadedFlag = true;
        });
}

// ═══ EXPORTAR FUNCIONES ═══
window.createTab = createTab;
window.closeTab = closeTab;
window.switchTab = switchTab;
window.browserNavigate = browserNavigate;
window.browserBack = browserBack;
window.browserForward = browserForward;
window.browserReload = browserReload;
window.browserOpenExternal = browserOpenExternal;
window.loadBrowserBookmarks = loadBrowserBookmarks;
window.retryTab = retryTab;

console.log('🌐 Internal Browser v3.0 (Corregido - Sin sandbox same-origin) cargado');
