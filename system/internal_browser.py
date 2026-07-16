"""Navegador interno de Kalm OS"""
import urllib.parse
import urllib.request
from pathlib import Path
from system.config import log

class InternalBrowser:
    
    @staticmethod
    def fetch_url(url, method="GET", headers=None, body=None):
        try:
            req = urllib.request.Request(url, method=method)
            
            default_headers = {
                "User-Agent": "KalmOS-InternalBrowser/4.2",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
                "X-Kalm-Internal": "true"
            }
            
            if headers:
                default_headers.update(headers)
            
            for k, v in default_headers.items():
                req.add_header(k, v)
            
            if body:
                req.data = body.encode("utf-8") if isinstance(body, str) else body
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read()
                content_type = resp.headers.get("Content-Type", "")
                
                try:
                    text = content.decode("utf-8")
                except:
                    try:
                        text = content.decode("latin-1")
                    except:
                        text = f"[Contenido binario - {len(content)} bytes]"
                
                return {
                    "ok": True,
                    "status": resp.status,
                    "content_type": content_type,
                    "content": text,
                    "size": len(content),
                    "url": url
                }
        except urllib.error.HTTPError as e:
            return {
                "ok": False,
                "status": e.code,
                "error": str(e),
                "content": e.read().decode("utf-8", errors="replace") if e.fp else ""
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "content": ""
            }
    
    @staticmethod
    def build_service_url(domain, path="/", port=None):
        from system.config import PROXY_PORT
        if port:
            return f"http://{domain}:{port}{path}"
        return f"http://{domain}:{PROXY_PORT}{path}"
    
    @staticmethod
    def get_bookmarks():
        """Retorna marcadores de servicios configurados"""
        bookmarks = [
            {"name": "🏰 Inicio", "domain": "kalm.local", "url": "/desktop", "icon": "🏰"},
            {"name": "💾 Disco D:", "domain": "d.local", "url": "/D", "icon": "💾"},
            {"name": "📊 Task Manager", "domain": "task", "url": "#", "icon": "📊"},
            {"name": "🌐 DNS", "domain": "dns", "url": "#", "icon": "🌐"},
            {"name": "🔒 Proxy", "domain": "proxy", "url": "#", "icon": "🔒"},
        ]
        
        try:
            from system.registry import get_proxy_server
            proxy = get_proxy_server()
            if proxy:
                rules = proxy.get_rules() if proxy else {}
                for domain, backend in list(rules.items())[:5]:
                    bookmarks.append({
                        "name": f"🌐 {domain}",
                        "domain": domain,
                        "backend": backend,
                        "url": f"http://{domain}/",
                        "icon": "🌐"
                    })
        except Exception as e:
            log(f"Error obteniendo reglas proxy: {e}", "WARN")
        
        return bookmarks
    
    @staticmethod
    def generate_iframe_html(url, title="Kalm Browser"):
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ height: 100%; overflow: hidden; background: #0a0514; font-family: 'Segoe UI', sans-serif; }}
        .toolbar {{
            height: 40px;
            background: linear-gradient(to right, #1a0033, #2e0854);
            border-bottom: 1px solid #6a0dad;
            display: flex;
            align-items: center;
            padding: 0 10px;
            gap: 8px;
            flex-shrink: 0;
        }}
        .toolbar button {{
            background: #4b0082;
            color: #fff;
            border: 1px solid #9370db;
            padding: 4px 10px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
        }}
        .toolbar button:hover {{ background: #6a0dad; }}
        .toolbar .btn-close {{
            background: #8b0000;
            border-color: #ff0000;
        }}
        .toolbar .btn-close:hover {{ background: #cc0000; }}
        .url-bar {{
            flex: 1;
            background: #1a0033;
            color: #e6e6fa;
            border: 1px solid #6a0dad;
            padding: 5px 10px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 12px;
            min-width: 100px;
        }}
        iframe {{
            width: 100%;
            height: calc(100% - 40px);
            border: none;
            background: #fff;
        }}
        .status {{
            position: absolute;
            bottom: 5px;
            right: 10px;
            color: #9370db;
            font-size: 10px;
            background: rgba(10,5,20,0.8);
            padding: 2px 8px;
            border-radius: 3px;
        }}
        @media (max-width: 768px) {{
            .toolbar {{ height: 36px; padding: 0 6px; gap: 4px; }}
            .toolbar button {{ font-size: 10px; padding: 3px 6px; }}
            .url-bar {{ font-size: 10px; padding: 3px 6px; }}
        }}
    </style>
</head>
<body>
    <div class="toolbar">
        <button onclick="history.back()">◀</button>
        <button onclick="history.forward()">▶</button>
        <button onclick="location.reload()">🔄</button>
        <input type="text" class="url-bar" id="url-bar" value="{url}" 
               onkeydown="if(event.key==='Enter')navigate()">
        <button onclick="navigate()">Ir</button>
        <button onclick="openExternal()">🔗</button>
        <button onclick="window.close()" class="btn-close">✕</button>
    </div>
    <iframe id="frame" src="{url}"></iframe>
    <div class="status">🏰 Kalm Internal Browser</div>
    <script>
        function navigate() {{
            const url = document.getElementById('url-bar').value;
            document.getElementById('frame').src = url;
        }}
        function openExternal() {{
            const url = document.getElementById('url-bar').value;
            window.open(url, '_blank');
        }}
    </script>
</body>
</html>'''