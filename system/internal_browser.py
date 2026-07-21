"""Navegador interno de Kalm OS - Versión Profesional"""
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
from system.config import log

class InternalBrowser:
    
    @staticmethod
    def fetch_url(url, method="GET", headers=None, body=None):
        try:
            req = urllib.request.Request(url, method=method)
            
            default_headers = { 
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
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
                except UnicodeDecodeError:
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
    def get_bookmarks():
        """Retorna marcadores de servicios configurados"""
        bookmarks = [
            {"name": "🏰 Inicio", "domain": "kalm.local", "url": "/desktop", "icon": "🏰"},
            {"name": "💾 Disco D:", "domain": "d.local", "url": "/D", "icon": "💾"},
            {"name": "🧠 Kalm AI", "domain": "kalm.ai", "url": "/api/kalm/", "icon": "🧠"},
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
