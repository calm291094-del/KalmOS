// KALM OS v4.3 - Internal Browser (Versión Firefox-Style Profesional)

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
        .browser-tabs-container {
            display: flex; background: rgba(20, 10, 40, 0.95); padding: 8px 8px 0 8px; gap: 4px; border-bottom: 1px solid #4b0082;
        }
        .browser-tab {
            display: flex; align-items: center; background: rgba(75, 0, 130, 0.3); color: #d8bfd8; padding: 8px 12px;
            border-radius: 8px 8px 0 0; font-size: 12px; cursor: pointer; max-width: 200px; min-width: 120px;
            border: 1px solid transparent; transition: all 0.2s;
        }
        .browser-tab.active { background: rgba(106, 13, 173, 0.6); color: #fff; border-color: #6a0dad; border-bottom-color: rgba(106, 13, 173, 0.6); }
        .browser-tab:hover:not(.active) { background: rgba(75, 0, 130, 0.5); }
        .tab-icon { margin-right: 6px; }
        .tab-title { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .tab-close { margin-left: 8px; padding: 2px 6px; border-radius: 4px; font-size: 14px; line-height: 1; }
        .tab-close:hover { background: rgba(255, 68, 68, 0.3); color: #ff4444; }
        .browser-new-tab-btn {
            display: flex; align-items: center; justify-content: center; width: 28px; height: 28px;
            background: rgba(75, 0, 130, 0.3); color: #d8bfd8; border-radius: 6px; cursor: pointer; font-size: 18px; margin-bottom: 4px;
        }
        .browser-new-tab-btn:hover { background: rgba(75, 0, 130, 0.6); color: #fff; }
        .browser-iframe-container { flex: 1; position: relative; background: #fff; }
        .browser-iframe { width: 100%; height: 100%; border: none; background: #fff; }
    `;
    document.head.appendChild(style);
}

// ═══ GESTIÓN DE PESTAÑAS ═══
function createTab(url = '/api/kalm/', title = '🧠 Kalm AI', setActive = true) {
    window.tabCounter++;
    const tabId = `tab-${window.tabCounter}`;
    window.browserTabs.push({ id: tabId, url: url, title: title, active: false });
    renderTabs();
    createIframeForTab(tabId, url);
    if (setActive) switchTab(tabId);
    return tabId;
}

function closeTab(tabId, event) {
    if (event) event.stopPropagation();
    const index = window.browserTabs.findIndex(t => t.id === tabId);
    if (index === -1) return;
    
    const iframe = document.getElementById(`iframe-${tabId}`);
    if (iframe) iframe.remove();
    window.browserTabs.splice(index, 1);
    
    if (window.activeTabId === tabId) {
        if (window.browserTabs.length > 0) {
            switchTab(window.browserTabs[Math.min(index, window.browserTabs.length - 1)].id);
        } else {
            createTab('/api/kalm/', '🧠 Kalm AI', true);
        }
    }
    renderTabs();
}

function switchTab(tabId) {
    window.activeTabId = tabId;
    const tab = window.browserTabs.find(t => t.id === tabId);
    if (!tab) return;
    
    document.querySelectorAll('.browser-iframe').forEach(iframe => iframe.style.display = 'none');
    
    let activeIframe = document.getElementById(`iframe-${tabId}`);
    if (!activeIframe) createIframeForTab(tabId, tab.url);
    document.getElementById(`iframe-${tabId}`).style.display = 'block';
    
    const urlInput = document.getElementById('browser-url');
    if (urlInput) urlInput.value = tab.url;
    renderTabs();
}

function updateTabTitle(tabId, title) {
    const tab = window.browserTabs.find(t => t.id === tabId);
    if (tab) { tab.title = title; renderTabs(); }
}

function renderTabs() {
    let tabContainer = document.getElementById('browser-tabs-container');
    if (!tabContainer) {
        const browserWin = document.getElementById('win-browser');
        if (browserWin) {
            tabContainer = document.createElement('div');
            tabContainer.id = 'browser-tabs-container';
            tabContainer.className = 'browser-tabs-container';
            browserWin.insertBefore(tabContainer, browserWin.firstChild);
        }
    }
    if (!tabContainer) return;
    
    tabContainer.innerHTML = '';
    window.browserTabs.forEach(tab => {
        const tabEl = document.createElement('div');
        tabEl.className = `browser-tab ${tab.id === window.activeTabId ? 'active' : ''}`;
        tabEl.onclick = () => switchTab(tab.id);
        tabEl.innerHTML = `<span class="tab-icon">🌐</span><span class="tab-title">${tab.title}</span><span class="tab-close" onclick="closeTab('${tab.id}', event)">✕</span>`;
        tabContainer.appendChild(tabEl);
    });
    
    const newTabBtn = document.createElement('div');
    newTabBtn.className = 'browser-new-tab-btn';
    newTabBtn.innerHTML = '+';
    newTabBtn.title = 'Nueva Pestaña';
    newTabBtn.onclick = () => createTab('/api/kalm/', '🧠 Kalm AI', true);
    tabContainer.appendChild(newTabBtn);
}

function createIframeForTab(tabId, url) {
    let iframeContainer = document.getElementById('browser-iframe-container');
    if (!iframeContainer) {
        const browserWin = document.getElementById('win-browser');
        if (browserWin) {
            iframeContainer = document.createElement('div');
            iframeContainer.id = 'browser-iframe-container';
            iframeContainer.className = 'browser-iframe-container';
            browserWin.appendChild(iframeContainer);
        }
    }
    if (!iframeContainer) return;
    
    const iframe = document.createElement('iframe');
    iframe.id = `iframe-${tabId}`;
    iframe.className = 'browser-iframe';
    iframe.style.display = 'none';
    // Sandbox permisivo CRUCIAL para que /api/kalm/ ejecute su JS
    iframe.sandbox = 'allow-scripts allow-same-origin allow-forms allow-popups allow-downloads';
    iframe.src = url;
    
    iframe.onload = function() {
        try {
            const title = iframe.contentDocument.title || 'Kalm Browser';
            updateTabTitle(tabId, title);
        } catch (e) {} // Cross-origin
    };
    iframeContainer.appendChild(iframe);
}

// ═══ NAVEGACIÓN ═══
function browserNavigate() {
    const urlInput = document.getElementById('browser-url');
    if (!urlInput || !window.activeTabId) return;
    
    let url = urlInput.value.trim();
    if (!url) return;
    if (!url.startsWith('http://') && !url.startsWith('https://') && !url.startsWith('/')) {
        url = url.includes('.') ? 'https://' + url : '/api/kalm/';
    }
    urlInput.value = url;
    
    const tab = window.browserTabs.find(t => t.id === window.activeTabId);
    if (tab) {
        tab.url = url;
        let iframe = document.getElementById(`iframe-${window.activeTabId}`);
        if (iframe) iframe.src = url;
        else createIframeForTab(window.activeTabId, url);
    }
}

function browserBack() {
    const iframe = document.getElementById(`iframe-${window.activeTabId}`);
    if (iframe?.contentWindow) { try { iframe.contentWindow.history.back(); } catch (e) {} }
}

function browserForward() {
    const iframe = document.getElementById(`iframe-${window.activeTabId}`);
    if (iframe?.contentWindow) { try { iframe.contentWindow.history.forward(); } catch (e) {} }
}

function browserReload() {
    const iframe = document.getElementById(`iframe-${window.activeTabId}`);
    if (iframe) iframe.src = iframe.src;
}

function browserOpenExternal() {
    const urlInput = document.getElementById('browser-url');
    if (urlInput?.value) window.open(urlInput.value.trim(), '_blank');
}

// ═══ INICIALIZACIÓN ═══
document.addEventListener('DOMContentLoaded', function() {
    injectBrowserCSS();
    if (window.browserTabs.length === 0) createTab('/api/kalm/', '🧠 Kalm AI', true);
    
    const urlInput = document.getElementById('browser-url');
    if (urlInput) {
        urlInput.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); browserNavigate(); } });
    }
    renderTabs();
    loadBrowserBookmarks();
});

function loadBrowserBookmarks() {
    const container = document.getElementById('browser-bookmarks');
    if (!container || window.bookmarksLoadedFlag || window.bookmarksLoading) return;
    window.bookmarksLoading = true;
    
    fetch('/api/browser/bookmarks').then(r => r.ok ? r.json() : null).then(bookmarks => {
        container.innerHTML = '';
        if (bookmarks?.length > 0) {
            bookmarks.forEach(bm => {
                const btn = document.createElement('button');
                btn.className = 'act small';
                btn.textContent = `${bm.icon || '🌐'} ${bm.name}`;
                btn.style.cssText = 'background:rgba(75,0,130,0.3);border-color:#6a0dad;margin:2px;cursor:pointer;';
                btn.onclick = function() {
                    const urlInput = document.getElementById('browser-url');
                    if (urlInput) {
                        let url = bm.url || bm.domain;
                        if (url && !url.startsWith('http') && !url.startsWith('/')) url = 'https://' + url;
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
    }).catch(() => {
        container.innerHTML = '<span style="color:#9370db;font-size:11px">📖 Marcadores</span>';
        window.bookmarksLoading = false;
        window.bookmarksLoadedFlag = true;
    });
}

window.createTab = createTab;
window.closeTab = closeTab;
window.switchTab = switchTab;
window.browserNavigate = browserNavigate;
window.browserBack = browserBack;
window.browserForward = browserForward;
window.browserReload = browserReload;
window.browserOpenExternal = browserOpenExternal;
window.loadBrowserBookmarks = loadBrowserBookmarks;

console.log('🌐 Internal Browser v2.0 (Firefox-Style) cargado');
