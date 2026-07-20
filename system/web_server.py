"""Servidor web principal de Kalm OS v4.3 - CON KALM AI INTEGRADO"""
import json
import mimetypes
import urllib.parse
import urllib.request
import urllib.error
import threading
import time
import os
import shutil
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

from system.config import (
    BASE_DIR, VIEWS_DIR, STATIC_DIR, BG_FILE, DRIVE_D, DATA_DIR, log, IS_CLOUD
)
from system.auth import auth_system
from system.task_manager import TaskManager, network_monitor
from system.file_manager import FileManager
from system.program_detector import ProgramDetector
from system.registry import get_dns_server, get_proxy_server
from system.script_runner import ScriptRunner

try:
    from system.Program.kalm_ai_app import kalm_ai_app
    KALM_AI_AVAILABLE = True
    log("Kalm AI App importada correctamente", "INFO")
except Exception as e:
    KALM_AI_AVAILABLE = False
    log(f"No se pudo importar Kalm AI App: {e}", "WARN")

_kalm_ai_thread = None
_kalm_ai_port = 5001

def start_kalm_ai_thread():
    global _kalm_ai_thread
    if not KALM_AI_AVAILABLE:
        log("Kalm AI no disponible para iniciar", "WARN")
        return False
    
    if _kalm_ai_thread and _kalm_ai_thread.is_alive():
        log("Kalm AI ya esta corriendo", "INFO")
        return True
    
    def run_kalm_ai():
        try:
            log(f"Iniciando Kalm AI en puerto {_kalm_ai_port}", "INFO")
            kalm_ai_app.run(host='127.0.0.1', port=_kalm_ai_port, debug=False, use_reloader=False)
        except Exception as e:
            log(f"Error en Kalm AI thread: {e}", "ERROR")
    
    _kalm_ai_thread = threading.Thread(target=run_kalm_ai, daemon=True)
    _kalm_ai_thread.start()
    
    time.sleep(2)
    log(f"Kalm AI thread iniciado en puerto {_kalm_ai_port}", "INFO")
    return True


class KalmWebHandler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass
    
    def get_session(self):
        for c in self.headers.get("Cookie", "").split(";"):
            c = c.strip()
            if c.startswith("session_id="):
                return auth_system.validate_session(c.split("=", 1)[1])
        return None
    
    def require_auth(self):
        s = self.get_session()
        if not s:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "No autenticado"}).encode())
            return None
        return s
    
    def _serve_static(self, path):
        file_path = STATIC_DIR / path.lstrip('/')
        if not file_path.exists() or not file_path.is_file():
            self.send_response(404)
            self.end_headers()
            return
        mime, _ = mimetypes.guess_type(str(file_path))
        self.send_response(200)
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Cache-Control", "public, max-age=3600")
        self.end_headers()
        with open(file_path, "rb") as f:
            self.wfile.write(f.read())
    
    def _serve_view(self, view_name):
        file_path = VIEWS_DIR / view_name
        if not file_path.exists():
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        with open(file_path, "r", encoding="utf-8") as f:
            self.wfile.write(f.read().encode("utf-8"))
    
    def _json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    
    def _parse_mp(self, body, boundary):
        for part in body.split(("--" + boundary).encode()):
            if b'filename="' in part:
                he = part.find(b"\r\n\r\n")
                if he != -1:
                    for line in part[:he].decode('utf-8', errors='ignore').split('\r\n'):
                        if 'filename=' in line:
                            fn = line.split('filename=')[1].strip('"').strip("'")
                            data = part[he+4:]
                            return (data[:-2] if data.endswith(b"\r\n") else data), fn
        return None, None
    
    def _proxy_kalm_ai(self, path):
        global _kalm_ai_thread
        
        if not _kalm_ai_thread or not _kalm_ai_thread.is_alive():
            log("Iniciando Kalm AI por primera vez...", "INFO")
            start_kalm_ai_thread()
            time.sleep(3)
        
        kalm_path = path[9:] if path.startswith("/kalm-ai") else "/"
        if not kalm_path or kalm_path == "":
            kalm_path = "/"
        elif not kalm_path.startswith("/"):
            kalm_path = "/" + kalm_path
        
        target_url = f"http://127.0.0.1:{_kalm_ai_port}{kalm_path}"
        if self.path and '?' in self.path:
            target_url += "?" + self.path.split('?', 1)[1]
        
        log(f"Proxy Kalm AI: {self.path} -> {target_url}", "DEBUG")
        
        try:
            req = urllib.request.Request(target_url, method=self.command)
            req.add_header("User-Agent", "KalmOS-Internal/1.0")
            
            for header in ["Content-Type", "Accept", "Accept-Language"]:
                if header in self.headers:
                    req.add_header(header, self.headers[header])
            
            if self.command in ["POST", "PUT", "PATCH"]:
                content_length = int(self.headers.get("Content-Length", 0))
                if content_length > 0:
                    body = self.rfile.read(content_length)
                    req.data = body
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                content = resp.read()
                content_type = resp.headers.get("Content-Type", "text/html; charset=utf-8")
                
                self.send_response(resp.status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content)
                log(f"Kalm AI proxy OK: {kalm_path}", "DEBUG")
                
        except urllib.error.URLError as e:
            log(f"Error en proxy Kalm AI: {e}", "WARN")
            self.send_response(503)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Kalm AI</title>
                <style>
                    body {
                        background: #0a0514;
                        font-family: 'Segoe UI', sans-serif;
                        min-height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        color: #e6e6fa;
                        padding: 20px;
                    }
                    .container {
                        max-width: 500px;
                        background: rgba(26, 0, 51, 0.8);
                        border-radius: 20px;
                        border: 1px solid rgba(106, 13, 173, 0.3);
                        padding: 40px;
                        text-align: center;
                    }
                    .icon { font-size: 64px; margin-bottom: 15px; }
                    h1 { color: #da70d6; font-size: 24px; }
                    .status {
                        display: inline-block;
                        padding: 6px 16px;
                        border-radius: 20px;
                        background: rgba(255,170,0,0.2);
                        border: 1px solid #ffaa00;
                        color: #ffaa00;
                        margin: 10px 0;
                        font-size: 13px;
                    }
                    .loading {
                        display: inline-block;
                        width: 30px;
                        height: 30px;
                        border: 4px solid rgba(106, 13, 173, 0.3);
                        border-radius: 50%;
                        border-top-color: #da70d6;
                        animation: spin 0.8s linear infinite;
                        margin: 15px auto;
                    }
                    @keyframes spin { to { transform: rotate(360deg); } }
                    .btn {
                        background: linear-gradient(135deg, #6a0dad, #9370db);
                        color: white;
                        border: none;
                        padding: 10px 24px;
                        border-radius: 8px;
                        font-size: 14px;
                        cursor: pointer;
                        margin-top: 10px;
                    }
                    .btn:hover { transform: scale(1.05); }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">🧠</div>
                    <h1>Kalm AI</h1>
                    <div class="status">Starting...</div>
                    <div class="loading"></div>
                    <p style="font-size:13px;color:#9370db;">The server is starting in the background</p>
                    <p style="font-size:11px;color:#6a0dad;">Please wait a few seconds...</p>
                    <button class="btn" onclick="window.location.reload()">Retry</button>
                </div>
                <script>
                    let attempts = 0;
                    const checkInterval = setInterval(() => {
                        attempts++;
                        fetch('/kalm-ai/health')
                            .then(r => {
                                if (r.ok) {
                                    clearInterval(checkInterval);
                                    window.location.reload();
                                }
                            })
                            .catch(() => {
                                if (attempts > 15) {
                                    clearInterval(checkInterval);
                                    document.querySelector('.status').textContent = 'Not responding';
                                    document.querySelector('.status').style.borderColor = '#ff4444';
                                    document.querySelector('.status').style.color = '#ff4444';
                                    document.querySelector('.loading').style.display = 'none';
                                }
                            });
                    }, 2000);
                </script>
            </body>
            </html>
            """)
        except Exception as e:
            log(f"Error en _proxy_kalm_ai: {e}", "ERROR")
            self.send_response(500)
            self.end_headers()
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        p = parsed.path
        q = urllib.parse.parse_qs(parsed.query)
        
        if p == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        
        if p.startswith("/kalm-ai"):
            self._proxy_kalm_ai(p)
            return
        
        if p.startswith("/static/"):
            self._serve_static(p[8:])
            return
        
        if p.startswith("/static/pac/"):
            pac_file = DATA_DIR / "pac" / p[12:]
            if pac_file.exists():
                self.send_response(200)
                self.send_header("Content-Type", "application/x-ns-proxy-autoconfig")
                self.end_headers()
                with open(pac_file, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            return
        
        if p.startswith("/D/Music/"):
            rel_path = urllib.parse.unquote(p[8:])
            filename = os.path.basename(rel_path)
            music_dir = DRIVE_D / "Music"
            
            log(f"Buscando: {filename} en {music_dir}", "DEBUG")
            
            found_file = None
            if music_dir.exists():
                for f in music_dir.iterdir():
                    if f.is_file() and f.name.lower() == filename.lower():
                        found_file = f
                        break
            
            if not found_file:
                log(f"Archivo no encontrado: {filename}", "WARN")
                self.send_response(404)
                self.end_headers()
                return
            
            try:
                with open(found_file, "rb") as f:
                    file_content = f.read()
            except Exception as e:
                log(f"Error leyendo archivo: {e}", "ERROR")
                self.send_response(500)
                self.end_headers()
                return
            
            ext = found_file.suffix.lower()
            if ext == '.mp3':
                content_type = 'audio/mpeg'
            elif ext == '.wav':
                content_type = 'audio/wav'
            elif ext == '.ogg':
                content_type = 'audio/ogg'
            elif ext == '.flac':
                content_type = 'audio/flac'
            else:
                content_type = 'application/octet-stream'
            
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(file_content)))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Cache-Control", "public, max-age=3600")
            self.send_header("Content-Disposition", f"inline; filename=\"{found_file.name}\"")
            self.end_headers()
            self.wfile.write(file_content)
            return
        
        if p.startswith("/D/"):
            rel_path = p[3:]
            file_path = DRIVE_D / rel_path
            if file_path.exists() and file_path.is_file():
                mime, _ = mimetypes.guess_type(str(file_path))
                self.send_response(200)
                self.send_header("Content-Type", mime or "application/octet-stream")
                self.send_header("Content-Disposition", f"inline; filename=\"{file_path.name}\"")
                self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_response(404)
                self.end_headers()
                return
        
        if p in ["/", "/index.html", "/login"]:
            self._serve_view("login.html")
            return
        
        if p == "/desktop":
            if not self.get_session():
                self.send_response(302)
                self.send_header("Location", "/")
                self.end_headers()
                return
            self._serve_view("desktop.html")
            return
        
        if p == "/background":
            if BG_FILE.exists():
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                with open(BG_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            return
        
        if p == "/api/background-check":
            self._json({"exists": BG_FILE.exists()})
            return
        
        if p == "/api/whoami":
            session = self.get_session()
            if session:
                self._json({"username": session.get("username", "user"), "role": session.get("role", "user")})
            else:
                self._json({"username": "user", "role": "user"})
            return
        
        if p == "/api/music/list":
            try:
                music_dir = DRIVE_D / "Music"
                files = []
                if music_dir.exists():
                    for f in music_dir.iterdir():
                        if f.is_file() and f.suffix.lower() in ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac']:
                            file_size = f.stat().st_size
                            url_path = "/D/Music/" + urllib.parse.quote(f.name)
                            files.append({
                                "name": f.name,
                                "path": str(f),
                                "url": url_path,
                                "size": file_size
                            })
                            log(f"   {f.name} ({file_size} bytes)", "DEBUG")
                files.sort(key=lambda x: x["name"].lower())
                self._json({"ok": True, "files": files, "count": len(files)})
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return
        
        if p == "/api/viewer":
            viewer_path = q.get('path', [''])[0]
            if viewer_path and Path(viewer_path).exists():
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(viewer_path, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
            return
        
        if p == "/api/browser/bookmarks":
            try:
                from system.internal_browser import InternalBrowser
                bookmarks = InternalBrowser.get_bookmarks()
                self._json(bookmarks)
            except Exception as e:
                self._json([])
            return
        
        if p == "/api/browser/fetch":
            url = q.get('url', [''])[0]
            if not url:
                self._json({"ok": False, "error": "URL requerida"})
            else:
                try:
                    from system.internal_browser import InternalBrowser
                    result = InternalBrowser.fetch_url(url)
                    self._json(result)
                except Exception as e:
                    self._json({"ok": False, "error": str(e)})
            return
        
        if p.startswith("/api/process/stream/"):
            session = self.require_auth()
            if not session:
                return
            
            session_id = p.split("/")[-1]
            
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            
            try:
                self.wfile.write(f"data: {json.dumps({'type': 'connected', 'data': 'Conectado'})}\n\n".encode())
                self.wfile.flush()
                
                no_change_count = 0
                max_no_change = 60
                is_alive = True
                
                while is_alive:
                    result = ScriptRunner.get_output(session_id, timeout=0.5)
                    
                    if result.get("ok"):
                        outputs = result.get("outputs", [])
                        if outputs:
                            no_change_count = 0
                            for output in outputs:
                                self.wfile.write(f"data: {json.dumps(output)}\n\n".encode())
                                self.wfile.flush()
                        else:
                            no_change_count += 1
                        
                        is_alive = result.get("is_alive", False)
                        
                        if no_change_count > max_no_change and not is_alive:
                            self.wfile.write(f"data: {json.dumps({'type': 'exit', 'code': 0, 'data': 'Sin actividad'})}\n\n".encode())
                            self.wfile.flush()
                            break
                        
                        if not is_alive:
                            self.wfile.write(f"data: {json.dumps({'type': 'exit', 'code': 0})}\n\n".encode())
                            self.wfile.flush()
                            break
                    else:
                        self.wfile.write(f"data: {json.dumps({'type': 'error', 'data': result.get('error', 'Error')})}\n\n".encode())
                        self.wfile.flush()
                        break
                    
                    time.sleep(0.3)
                
            except (BrokenPipeError, ConnectionResetError):
                pass
            except Exception as e:
                log(f"Error en SSE: {e}", "ERROR")
            
            return
        
        session = self.require_auth()
        if not session:
            return
        
        if p == "/api/processes":
            self._json(TaskManager.list_processes())
            return
        
        if p == "/api/system-stats":
            self._json(TaskManager.get_system_stats())
            return
        
        if p == "/api/running-procs":
            self._json(ScriptRunner.list_running())
            return
        
        if p == "/api/process/list":
            self._json({"ok": True, "processes": ScriptRunner.list_running()})
            return
        
        if p == "/api/programs":
            detector = ProgramDetector()
            self._json(detector.get_cached())
            return
        
        if p == "/api/dns":
            dns = get_dns_server()
            self._json({"rules": dns.get_rules() if dns else {}})
            return
        
        if p == "/api/proxy":
            proxy = get_proxy_server()
            self._json({"rules": proxy.get_rules() if proxy else {}})
            return
        
        if p == "/api/proxy-log":
            proxy = get_proxy_server()
            self._json(proxy.get_log() if proxy else [])
            return
        
        if p == "/api/pac-info":
            try:
                from system.pac_generator import PACGenerator
                pac_url = PACGenerator.get_pac_url()
                instructions = PACGenerator.get_browser_config_instructions()
                self._json({
                    "ok": True,
                    "pac_url": pac_url,
                    "instructions": instructions
                })
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return
        
        if p == "/api/files":
            fp = q.get('path', [''])[0]
            if not fp or fp == "":
                fp = "/D"
            result = FileManager.list_directory(fp)
            self._json(result)
            return
        
        if p == "/api/files/search":
            self._json(FileManager.search(q.get('q', [''])[0]))
            return
        
        if p == "/api/last-log":
            log_data = ScriptRunner.get_last_log()
            if log_data:
                self._json({"ok": True, **log_data})
            else:
                self._json({"ok": False, "error": "No hay logs"})
            return
        
        self.send_response(404)
        self.end_headers()
    
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        parsed = urllib.parse.urlparse(self.path)
        p = parsed.path
        q = urllib.parse.parse_qs(parsed.query)
        
        if p.startswith("/kalm-ai"):
            self._proxy_kalm_ai(p)
            return
        
        if p == "/api/login":
            try:
                d = json.loads(body)
            except:
                self._json({"ok": False, "error": "JSON invalido"})
                return
            sid = auth_system.authenticate(d.get("username"), d.get("password"))
            if sid:
                self._json({"ok": True, "session_id": sid})
            else:
                self._json({"ok": False, "error": "Credenciales incorrectas"})
            return
        
        if p == "/api/logout":
            for c in self.headers.get("Cookie", "").split(";"):
                c = c.strip()
                if c.startswith("session_id="):
                    auth_system.logout(c.split("=", 1)[1])
            self._json({"ok": True})
            return
        
        session = self.require_auth()
        if not session:
            return
        
        if p.startswith("/api/kill/"):
            pid = int(p.split("/")[-1])
            self._json({"ok": TaskManager.kill_process(pid)})
            return
        
        if p.startswith("/api/stop-proc/"):
            pid = int(p.split("/")[-1])
            self._json({"ok": TaskManager.kill_process(pid)})
            return
        
        if p == "/api/stop-all":
            results = []
            for proc in ScriptRunner.list_running():
                result = ScriptRunner.stop_process(proc["session_id"])
                results.append(result)
            self._json({"ok": True, "stopped": len(results)})
            return
        
        if p == "/api/process/input":
            try:
                data = json.loads(body)
                session_id = data.get("session_id")
                input_data = data.get("input", "")
                result = ScriptRunner.send_input(session_id, input_data)
                self._json(result)
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return
        
        if p.startswith("/api/process/stop/"):
            session_id = p.split("/")[-1]
            result = ScriptRunner.stop_process(session_id)
            self._json(result)
            return
        
        if p == "/api/dns":
            dns = get_dns_server()
            if dns:
                try:
                    d = json.loads(body)
                    dns.add_rule(d["domain"], d["ip"])
                    self._json({"ok": True})
                except Exception as e:
                    self._json({"ok": False, "error": str(e)})
            else:
                self._json({"ok": False, "error": "DNS no disponible"})
            return
        
        if p.startswith("/api/dns/"):
            dns = get_dns_server()
            if dns:
                dns.remove_rule(p.split("/")[-1])
                self._json({"ok": True})
            else:
                self._json({"ok": False, "error": "DNS no disponible"})
            return
        
        if p == "/api/proxy":
            proxy = get_proxy_server()
            if proxy:
                try:
                    d = json.loads(body)
                    domain = d.get("domain", "").strip()
                    backend = d.get("backend", "").strip()
                    if not domain or not backend:
                        self._json({"ok": False, "error": "Dominio y backend requeridos"})
                        return
                    if not backend.startswith("http://") and not backend.startswith("https://"):
                        backend = "http://" + backend
                    proxy.add_rule(domain, backend)
                    self._json({"ok": True})
                except Exception as e:
                    self._json({"ok": False, "error": str(e)})
            else:
                self._json({"ok": False, "error": "Proxy no disponible"})
            return
        
        if p.startswith("/api/proxy/delete/"):
            proxy = get_proxy_server()
            if proxy:
                domain = p.split("/api/proxy/delete/")[-1]
                if proxy.remove_rule(domain):
                    self._json({"ok": True})
                else:
                    self._json({"ok": False})
            else:
                self._json({"ok": False, "error": "Proxy no disponible"})
            return
        
        if p == "/api/proxy/clear-log":
            proxy = get_proxy_server()
            if proxy:
                proxy.clear_log()
            self._json({"ok": True})
            return
        
        if p == "/api/pac/generate":
            try:
                from system.pac_generator import PACGenerator
                pac_file = PACGenerator.generate_pac()
                self._json({"ok": True, "file": pac_file, "url": PACGenerator.get_pac_url()})
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return

        if p == "/api/process/log":
            try:
                data = json.loads(body)
                session_id = data.get("session_id")
        
                log_dir = DATA_DIR / "virtual_env" / "output"
                log_file = None
        
                if log_dir.exists():
                    for f in log_dir.iterdir():
                        if f.is_file() and session_id in f.name:
                            log_file = f
                            break
        
                if log_file and log_file.exists():
                    content = log_file.read_text(encoding="utf-8", errors="replace")
                    if len(content) > 5000:
                        content = content[-5000:]
                    self._json({"ok": True, "content": content})
                else:
                    log_files = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
                    if log_files:
                        content = log_files[0].read_text(encoding="utf-8", errors="replace")
                        if len(content) > 5000:
                            content = content[-5000:]
                        self._json({"ok": True, "content": content, "file": str(log_files[0])})
                    else:
                        self._json({"ok": False, "error": "Log no encontrado"})
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return

        if p == "/api/read-signal":
            try:
                data = json.loads(body)
                file_path = data.get("file", "")
        
                if not file_path:
                    self._json({"ok": False, "error": "Ruta no especificada"})
                    return
        
                possible_paths = [
                    BASE_DIR / file_path,
                    DATA_DIR / file_path,
                    DATA_DIR / "persistence" / Path(file_path).name,
                    Path(file_path)
                ]
        
                found_content = None
                for path in possible_paths:
                    if path.exists():
                        try:
                            found_content = path.read_text(encoding="utf-8").strip()
                            log(f"Senal encontrada en: {path}", "DEBUG")
                            break
                        except:
                            pass
        
                if found_content:
                    self._json({"ok": True, "content": found_content})
                else:
                    self._json({"ok": False, "error": "Archivo no encontrado"})
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return
        
        if p == "/api/run":
            try:
                data = json.loads(body)
                path = data.get("path", "").strip()
                args = data.get("args", [])
                
                if not path:
                    self._json({"ok": False, "error": "Ruta requerida"})
                    return
                
                result = ScriptRunner.run(path, args)
                
                if result.get("ok") and result.get("viewer_path"):
                    viewer_path = result["viewer_path"]
                    viewer_url = f"/api/viewer?path={urllib.parse.quote(viewer_path)}"
                    result["viewer_url"] = viewer_url
                
                self._json(result)
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return
        
        if p == "/api/run-direct":
            try:
                data = json.loads(body)
                path = data.get("path", "").strip()
                args = data.get("args", [])
                
                if not path:
                    self._json({"ok": False, "error": "Ruta requerida"})
                    return
                
                from system.virtual_runner import VirtualRunner
                result = VirtualRunner.execute_detached(path, args)
                
                self._json(result)
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return
        
        if p == "/api/files/folder":
            try:
                d = json.loads(body)
                self._json(FileManager.create_folder(d["path"], d["name"]))
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return
        
        if p == "/api/files/delete":
            try:
                d = json.loads(body)
                self._json(FileManager.delete(d["path"]))
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return
        
        if p == "/api/files/upload":
            dp = q.get('path', [''])[0]
            if not dp:
                dp = str(DRIVE_D)
            ct = self.headers.get("Content-Type", "")
            if "multipart/form-data" in ct:
                boundary = ct.split("boundary=")[1]
                fd, fn = self._parse_mp(body, boundary)
                if fd and fn:
                    sp = Path(dp) / fn
                    sp.parent.mkdir(parents=True, exist_ok=True)
                    with open(sp, "wb") as f:
                        f.write(fd)
                    self._json({"ok": True, "path": str(sp)})
                else:
                    self._json({"ok": False, "error": "No file"})
            else:
                self._json({"ok": False, "error": "Invalid type"})
            return
        
        if p == "/api/background":
            ct = self.headers.get("Content-Type", "")
            if "multipart/form-data" in ct:
                boundary = ct.split("boundary=")[1]
                fd, _ = self._parse_mp(body, boundary)
                if fd:
                    with open(BG_FILE, "wb") as f:
                        f.write(fd)
                    self._json({"ok": True})
                else:
                    self._json({"ok": False, "error": "No file"})
            else:
                self._json({"ok": False, "error": "Invalid"})
            return
        
        if p == "/api/persistence/save":
            try:
                data = json.loads(body)
                name = data.get("name", "default")
                content = data.get("data", {})
                
                save_file = DATA_DIR / "persistence" / f"{name}.json"
                save_file.parent.mkdir(parents=True, exist_ok=True)
                save_file.write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding="utf-8")
                self._json({"ok": True})
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return
        
        if p == "/api/persistence/load":
            try:
                data = json.loads(body)
                name = data.get("name", "default")
                load_file = DATA_DIR / "persistence" / f"{name}.json"
                if load_file.exists():
                    content = json.loads(load_file.read_text(encoding="utf-8"))
                    self._json({"ok": True, "data": content})
                else:
                    self._json({"ok": True, "data": None})
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return
        
        if p == "/api/persistence/backups":
            try:
                backup_dir = DATA_DIR / "persistence" / "backups"
                if backup_dir.exists():
                    backups = [f.name for f in backup_dir.iterdir() if f.is_dir()]
                    self._json({"ok": True, "backups": sorted(backups, reverse=True)})
                else:
                    self._json({"ok": True, "backups": []})
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return
        
        if p == "/api/persistence/backup":
            try:
                import shutil
                backup_dir = DATA_DIR / "persistence" / "backups" / f"backup_{int(time.time())}"
                backup_dir.mkdir(parents=True, exist_ok=True)
                
                source_dir = DATA_DIR / "persistence"
                if source_dir.exists():
                    for item in source_dir.iterdir():
                        if item.name != "backups" and item.is_file():
                            shutil.copy2(item, backup_dir / item.name)
                
                self._json({"ok": True, "backup": backup_dir.name})
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return
        
        if p == "/api/persistence/restore":
            try:
                import shutil
                data = json.loads(body)
                backup_name = data.get("name", "")
                backup_dir = DATA_DIR / "persistence" / "backups" / backup_name
                
                if not backup_dir.exists():
                    self._json({"ok": False, "error": "Backup no encontrado"})
                    return
                
                dest_dir = DATA_DIR / "persistence"
                dest_dir.mkdir(parents=True, exist_ok=True)
                for item in backup_dir.iterdir():
                    if item.is_file():
                        shutil.copy2(item, dest_dir / item.name)
                
                self._json({"ok": True})
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return
        
        if p == "/api/shutdown":
            self._json({"ok": True})
            threading.Thread(target=lambda: (time.sleep(1), os._exit(0)), daemon=True).start()
            return
        
        self.send_response(404)
        self.end_headers()
    
    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        p = parsed.path
        
        if p.startswith("/api/proxy/"):
            session = self.require_auth()
            if not session:
                return
            proxy = get_proxy_server()
            if proxy:
                domain = urllib.parse.unquote(p.split("/api/proxy/")[-1])
                if proxy.remove_rule(domain):
                    self._json({"ok": True})
                else:
                    self._json({"ok": False})
            else:
                self._json({"ok": False, "error": "Proxy no disponible"})
            return
        
        if p.startswith("/api/dns/"):
            session = self.require_auth()
            if not session:
                return
            dns = get_dns_server()
            if dns:
                domain = urllib.parse.unquote(p.split("/api/dns/")[-1])
                dns.remove_rule(domain)
                self._json({"ok": True})
            else:
                self._json({"ok": False, "error": "DNS no disponible"})
            return
        
        self.send_response(404)
        self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS, PUT, PATCH")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


log("Iniciando Kalm AI integrado...", "INFO")
start_kalm_ai_thread()
log("Kalm AI integrado listo", "INFO")
