"""Proxy inverso completo con soporte HTTP/HTTPS/WebSocket"""
import urllib.parse
import urllib.request
import urllib.error
import socket
import threading
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from system.config import PROXY_FILE, load_json, save_json, log


class KalmProxy:
    def __init__(self, port):
        self.port = port
        self.rules = load_json(PROXY_FILE, {
            "api.kalm.local": "http://127.0.0.1:8080",
            "d.local": "http://127.0.0.1:8080"
        })
        self.running = False
        self.request_log = []
        self.max_log_size = 100
    
    def get_rules(self):
        return self.rules
    
    def get_log(self):
        return self.request_log[-self.max_log_size:]
    
    def clear_log(self):
        self.request_log = []
    
    def add_rule(self, domain, backend):
        # Normalizar backend
        if not backend.startswith("http://") and not backend.startswith("https://"):
            backend = "http://" + backend
        
        # Verificar si ya existe
        if domain in self.rules:
            old_backend = self.rules[domain]
            log(f"🔄 Actualizando proxy: {domain} de {old_backend} a {backend}")
        else:
            log(f"➕ Agregando proxy: {domain} -> {backend}")
        
        self.rules[domain] = backend
        save_json(PROXY_FILE, self.rules)
        
        # Regenerar PAC
        try:
            from system.pac_generator import PACGenerator
            PACGenerator.generate_pac()
        except Exception as e:
            log(f"⚠️ Error regenerando PAC: {e}", "WARN")
    
    def remove_rule(self, domain):
        if domain in self.rules:
            backend = self.rules[domain]
            del self.rules[domain]
            save_json(PROXY_FILE, self.rules)
            log(f"🗑️ Eliminando proxy: {domain} -> {backend}")
            
            try:
                from system.pac_generator import PACGenerator
                PACGenerator.generate_pac()
            except:
                pass
            return True
        return False
    
    def _log_request(self, method, host, path, backend, status, size=0):
        entry = {
            "time": datetime.datetime.now().isoformat(),
            "method": method,
            "host": host,
            "path": path,
            "backend": backend or "NO_RULE",
            "status": status,
            "size": size
        }
        self.request_log.append(entry)
        if len(self.request_log) > self.max_log_size * 2:
            self.request_log = self.request_log[-self.max_log_size:]
    
    def _make_handler(self):
        rules = self.rules
        proxy_ref = self
        
        class ProxyHandler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass
            
            def do_GET(self): self._proxy("GET")
            def do_POST(self): self._proxy("POST")
            def do_PUT(self): self._proxy("PUT")
            def do_DELETE(self): self._proxy("DELETE")
            def do_PATCH(self): self._proxy("PATCH")
            def do_OPTIONS(self): self._proxy("OPTIONS")
            def do_HEAD(self): self._proxy("HEAD")
            
            def do_CONNECT(self):
                """Soporte para HTTPS y WebSocket"""
                host_header = self.path
                if ":" in host_header:
                    host, port = host_header.split(":")
                    port = int(port)
                else:
                    host = host_header
                    port = 443
                
                backend = rules.get(host)
                
                if not backend:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"No rule for " + host.encode())
                    proxy_ref._log_request("CONNECT", host, "", None, 404)
                    return
                
                # Parsear backend
                parsed = urllib.parse.urlparse(backend)
                target_host = parsed.hostname or "127.0.0.1"
                target_port = parsed.port or port
                
                try:
                    self.send_response(200, "Connection Established")
                    self.end_headers()
                    
                    backend_sock = socket.create_connection((target_host, target_port), timeout=10)
                    
                    def forward(src, dst):
                        try:
                            while True:
                                data = src.recv(8192)
                                if not data:
                                    break
                                dst.sendall(data)
                        except:
                            pass
                        finally:
                            try: src.close()
                            except: pass
                            try: dst.close()
                            except: pass
                    
                    t1 = threading.Thread(target=forward, args=(self.connection, backend_sock), daemon=True)
                    t2 = threading.Thread(target=forward, args=(backend_sock, self.connection), daemon=True)
                    t1.start()
                    t2.start()
                    
                    proxy_ref._log_request("CONNECT", host, f":{port}", backend, 200)
                except Exception as e:
                    log(f"CONNECT error: {e}", "ERROR")
                    proxy_ref._log_request("CONNECT", host, f":{port}", backend, 502)
            
            def _proxy(self, method):
                host = self.headers.get("Host", "").split(":")[0]
                backend = rules.get(host)
                
                if not backend:
                    # Intentar con www.
                    if host.startswith("www."):
                        backend = rules.get(host[4:])
                
                if not backend:
                    self.send_response(404)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("X-Kalm-Proxy", "true")
                    self.end_headers()
                    self.wfile.write(f"""
                    <!DOCTYPE html>
                    <html><head><title>Kalm Proxy - Sin Regla</title>
                    <style>
                        body {{ background: #0a0514; color: #da70d6; font-family: 'Segoe UI', sans-serif;
                               padding: 50px; text-align: center; }}
                        h1 {{ font-size: 48px; margin-bottom: 20px; }}
                        .box {{ background: rgba(75,0,130,0.3); padding: 20px; border-radius: 10px;
                               border: 1px solid #6a0dad; max-width: 600px; margin: 20px auto; }}
                        code {{ background: #1a0033; padding: 2px 8px; border-radius: 3px; color: #fff; }}
                    </style></head><body>
                    <h1>🏰 Kalm Proxy</h1>
                    <div class="box">
                        <p>No hay regla para: <code>{host}</code></p>
                        <p>Agrega una regla en el panel de <b>🔒 Proxy</b> de Kalm OS.</p>
                        <hr style="border-color:#4b0082;margin:20px 0">
                        <p style="font-size:12px;color:#9370db">
                        Ruta solicitada: <code>{self.path}</code><br>
                        Método: <code>{method}</code>
                        </p>
                    </div>
                    </body></html>
                    """.encode())
                    proxy_ref._log_request(method, host, self.path, None, 404)
                    return
                
                url = backend.rstrip("/") + self.path
                hdrs = {}
                for k, v in self.headers.items():
                    if k.lower() not in ("host", "connection", "keep-alive", "proxy-connection"):
                        hdrs[k] = v
                
                # Agregar headers de proxy
                hdrs["X-Forwarded-For"] = self.client_address[0]
                hdrs["X-Forwarded-Host"] = host
                hdrs["X-Forwarded-Proto"] = "http"
                hdrs["X-Kalm-Proxy"] = "true"
                
                body = None
                if method in ["POST", "PUT", "PATCH"]:
                    l = int(self.headers.get("Content-Length", 0))
                    if l > 0:
                        body = self.rfile.read(l)
                
                try:
                    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        content = resp.read()
                        self.send_response(resp.status)
                        for k, v in resp.getheaders():
                            if k.lower() not in ("transfer-encoding", "connection", "keep-alive"):
                                self.send_header(k, v)
                        self.send_header("X-Kalm-Proxy", "true")
                        self.end_headers()
                        self.wfile.write(content)
                        proxy_ref._log_request(method, host, self.path, backend, resp.status, len(content))
                except urllib.error.HTTPError as e:
                    self.send_response(e.code)
                    for k, v in e.headers.items():
                        if k.lower() not in ("transfer-encoding", "connection"):
                            self.send_header(k, v)
                    self.end_headers()
                    if e.fp:
                        content = e.fp.read()
                        self.wfile.write(content)
                        proxy_ref._log_request(method, host, self.path, backend, e.code, len(content))
                    else:
                        proxy_ref._log_request(method, host, self.path, backend, e.code, 0)
                except Exception as e:
                    log(f"Proxy error [{host}]: {e}", "ERROR")
                    self.send_response(502)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(f"""
                    <!DOCTYPE html>
                    <html><head><title>Kalm Proxy - Error</title>
                    <style>
                        body {{ background: #0a0514; color: #ff4444; font-family: 'Segoe UI', sans-serif;
                               padding: 50px; text-align: center; }}
                        h1 {{ font-size: 48px; }}
                        .box {{ background: rgba(139,0,0,0.3); padding: 20px; border-radius: 10px;
                               border: 1px solid #8b0000; max-width: 600px; margin: 20px auto; }}
                        code {{ background: #1a0033; padding: 2px 8px; border-radius: 3px; color: #fff; }}
                    </style></head><body>
                    <h1>⚠️ Bad Gateway</h1>
                    <div class="box">
                        <p>Backend: <code>{backend}</code></p>
                        <p>Error: <code>{e}</code></p>
                        <p style="font-size:12px;color:#9370db">
                        Verifica que el servicio esté corriendo dentro de Kalm OS.
                        </p>
                    </div>
                    </body></html>
                    """.encode())
                    proxy_ref._log_request(method, host, self.path, backend, 502, 0)
        
        return ProxyHandler
    
    def run(self):
        self.running = True
        srv = HTTPServer(("0.0.0.0", self.port), self._make_handler())
        srv.timeout = 1
        log(f"🔒 Proxy en puerto {self.port}")
        while self.running:
            srv.handle_request()
        srv.server_close()
    
    def stop(self):
        self.running = False