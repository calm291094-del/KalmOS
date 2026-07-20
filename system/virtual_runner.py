"""Ejecutor virtual de programas - Con mejor captura de salida"""
import os
import sys
import subprocess
import threading
import queue
import time
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from system.config import BASE_DIR, DRIVE_D, log

class VirtualRunner:
    VIRTUAL_ENV = BASE_DIR / "kalm_data" / "virtual_env"
    OUTPUT_DIR = VIRTUAL_ENV / "output"
    VIEWER_DIR = VIRTUAL_ENV / "viewer"
    
    _active_processes = {}
    _initialized = False
    
    @classmethod
    def init(cls):
        if cls._initialized:
            return
        dirs = [cls.VIRTUAL_ENV, cls.OUTPUT_DIR, cls.VIEWER_DIR]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
        cls._initialized = True
    
    @classmethod
    def resolve_path(cls, path):
        """Resuelve una ruta - Busca en system/program/ y D:/"""
        if not path:
            return None
        
        path_str = str(path)
        path_obj = Path(path_str)
        
        # ═══ 1. Si la ruta ya existe, devolverla ═══
        if path_obj.exists():
            return path_obj
        
        # ═══ 2. Buscar en system/program/ ═══
        program_dir = BASE_DIR / "system" / "Program"
        
        if path_str.startswith("system/program/") or path_str.startswith("/system/program/"):
            rel_path = path_str.replace("system/program/", "").replace("/system/program/", "")
            test_path = program_dir / rel_path
            if test_path.exists():
                return test_path
        
        if path_str.startswith("D:/") or path_str.startswith("D:\\"):
            filename = Path(path_str).name
            if filename:
                test_path = program_dir / filename
                if test_path.exists():
                    return test_path
                for ext in ['.py', '.sh', '.js', '.bat', '.cmd']:
                    test_path = program_dir / f"{filename}{ext}"
                    if test_path.exists():
                        return test_path
        
        if path_obj.parent == Path(".") or path_obj.parent == Path("/"):
            test_path = program_dir / path_str
            if test_path.exists():
                return test_path
            for ext in ['.py', '.sh', '.js', '.bat', '.cmd']:
                test_path = program_dir / f"{path_str}{ext}"
                if test_path.exists():
                    return test_path
        
        filename = path_obj.name
        if filename:
            for ext in ['', '.py', '.sh', '.js', '.bat', '.cmd']:
                test_path = program_dir / f"{filename}{ext}"
                if test_path.exists():
                    return test_path
        
        # ═══ 3. Buscar en D:/ ═══
        if DRIVE_D.exists():
            test_path = DRIVE_D / "Scripts" / path_str
            if test_path.exists():
                return test_path
            test_path = DRIVE_D / "Apps" / path_str
            if test_path.exists():
                return test_path
            test_path = DRIVE_D / "Projects" / path_str
            if test_path.exists():
                return test_path
            
            filename = path_obj.name
            if filename:
                for base in ["Scripts", "Apps", "Projects"]:
                    test_path = DRIVE_D / base / filename
                    if test_path.exists():
                        return test_path
        
        log(f"⚠️ No se encontró el archivo: {path_str}", "WARN")
        return path_obj
    
    @classmethod
    def execute(cls, program_path, args=None):
        """Ejecuta un programa"""
        cls.init()
        
        resolved = cls.resolve_path(program_path)
        if not resolved:
            return {"ok": False, "error": f"Ruta inválida: {program_path}"}
        
        if not resolved.exists():
            return {"ok": False, "error": f"Programa no encontrado: {resolved}"}
        
        ext = resolved.suffix.lower()
        log(f"🔍 Ejecutando: {resolved} (ext: {ext})")
        
        # ═══ DOCUMENTOS ═══
        if ext == ".pdf":
            return cls._open_pdf(resolved)
        if ext in [".txt", ".md", ".log", ".json", ".xml", ".yaml", ".yml", ".csv"]:
            return cls._view_text(resolved)
        if ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico"]:
            return cls._view_image(resolved)
        
        # ═══ PROGRAMAS PYTHON ═══
        if ext == ".py":
            return cls._run_python(resolved, args)
        
        # ═══ SCRIPTS ═══
        if ext in [".sh", ".bash"]:
            return cls._run_bash(resolved, args)
        
        if ext in [".js"]:
            return cls._run_node(resolved, args)
        
        # ═══ EJECUTABLES WINDOWS ═══
        if ext in [".exe", ".bat", ".cmd"]:
            return cls._run_native(resolved, args)
        
        return {"ok": False, "error": f"Tipo no soportado: {ext}"}
    
    @classmethod
    def _run_python(cls, py_path, args=None):
        """Ejecuta un script Python y captura su salida en tiempo real"""
        try:
            if not py_path.exists():
                return {"ok": False, "error": f"Python script no encontrado: {py_path}"}
            
            env = os.environ.copy()
            env.update({
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUTF8": "1",
                "PYTHONUNBUFFERED": "1"
            })
            
            python_exe = sys.executable
            cmd = [python_exe, "-u", str(py_path)]
            
            if args:
                if isinstance(args, list):
                    cmd.extend(args)
                elif isinstance(args, str):
                    cmd.append(args)
            
            log(f"▶️ Ejecutando Python: {' '.join(cmd)}")
            
            session_id = str(uuid.uuid4())
            output_queue = queue.Queue()
            
            log_file = cls.OUTPUT_DIR / f"{py_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            project_root = Path(__file__).parent.parent.parent
            
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                cwd=str(project_root),
                env=env,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1
            )
            
            stdout_capture = []
            
            def read_output():
                try:
                    for line in iter(proc.stdout.readline, ''):
                        if line:
                            stdout_capture.append(line)
                            output_queue.put({"type": "output", "data": line})
                            with open(log_file, 'a', encoding='utf-8') as f:
                                f.write(line)
                except Exception as e:
                    output_queue.put({"type": "error", "data": str(e)})
                finally:
                    proc.stdout.close()
                    proc.wait()
                    output_queue.put({"type": "exit", "code": proc.returncode})
            
            reader_thread = threading.Thread(target=read_output, daemon=True)
            reader_thread.start()
            
            cls._active_processes[session_id] = {
                "process": proc,
                "queue": output_queue,
                "thread": reader_thread,
                "program": str(py_path),
                "started": datetime.now().isoformat(),
                "log_file": str(log_file)
            }
            
            output_queue.put({"type": "output", "data": f"▶️ Iniciando {py_path.name}...\n"})
            
            log(f"✅ {py_path.name} ejecutado (PID {proc.pid})")
            
            stdout_text = ''.join(stdout_capture)
            
            return {
                "ok": True,
                "session_id": session_id,
                "pid": proc.pid,
                "is_alive": True,
                "log_file": str(log_file),
                "message": f"✅ {py_path.name} ejecutado (PID {proc.pid})",
                "type": "python",
                "stdout": stdout_text
            }
            
        except Exception as e:
            log(f"❌ Error ejecutando Python: {e}", "ERROR")
            return {"ok": False, "error": f"Error ejecutando Python: {str(e)}"}
    
    @classmethod
    def _run_bash(cls, sh_path, args=None):
        try:
            if not sh_path.exists():
                return {"ok": False, "error": f"Bash script no encontrado: {sh_path}"}
            
            env = os.environ.copy()
            cmd = ['bash', str(sh_path)]
            if args:
                cmd.extend(args)
            
            session_id = str(uuid.uuid4())
            output_queue = queue.Queue()
            log_file = cls.OUTPUT_DIR / f"{sh_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            
            project_root = Path(__file__).parent.parent.parent
            
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                cwd=str(project_root),
                env=env,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1
            )
            
            stdout_capture = []
            
            def read_output():
                try:
                    for line in iter(proc.stdout.readline, ''):
                        if line:
                            stdout_capture.append(line)
                            output_queue.put({"type": "output", "data": line})
                            with open(log_file, 'a', encoding='utf-8') as f:
                                f.write(line)
                except Exception as e:
                    output_queue.put({"type": "error", "data": str(e)})
                finally:
                    proc.stdout.close()
                    proc.wait()
                    output_queue.put({"type": "exit", "code": proc.returncode})
            
            reader_thread = threading.Thread(target=read_output, daemon=True)
            reader_thread.start()
            
            cls._active_processes[session_id] = {
                "process": proc,
                "queue": output_queue,
                "thread": reader_thread,
                "program": str(sh_path),
                "started": datetime.now().isoformat(),
                "log_file": str(log_file)
            }
            
            stdout_text = ''.join(stdout_capture)
            
            return {
                "ok": True,
                "session_id": session_id,
                "pid": proc.pid,
                "is_alive": True,
                "log_file": str(log_file),
                "message": f"✅ {sh_path.name} ejecutado (PID {proc.pid})",
                "type": "bash",
                "stdout": stdout_text
            }
            
        except Exception as e:
            return {"ok": False, "error": f"Error ejecutando bash: {str(e)}"}
    
    @classmethod
    def _run_node(cls, js_path, args=None):
        try:
            if not js_path.exists():
                return {"ok": False, "error": f"Node.js script no encontrado: {js_path}"}
            
            node_path = shutil.which('node')
            if not node_path:
                return {"ok": False, "error": "Node.js no está instalado"}
            
            env = os.environ.copy()
            cmd = [node_path, str(js_path)]
            if args:
                cmd.extend(args)
            
            session_id = str(uuid.uuid4())
            output_queue = queue.Queue()
            log_file = cls.OUTPUT_DIR / f"{js_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            
            project_root = Path(__file__).parent.parent.parent
            
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                cwd=str(project_root),
                env=env,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1
            )
            
            stdout_capture = []
            
            def read_output():
                try:
                    for line in iter(proc.stdout.readline, ''):
                        if line:
                            stdout_capture.append(line)
                            output_queue.put({"type": "output", "data": line})
                            with open(log_file, 'a', encoding='utf-8') as f:
                                f.write(line)
                except Exception as e:
                    output_queue.put({"type": "error", "data": str(e)})
                finally:
                    proc.stdout.close()
                    proc.wait()
                    output_queue.put({"type": "exit", "code": proc.returncode})
            
            reader_thread = threading.Thread(target=read_output, daemon=True)
            reader_thread.start()
            
            cls._active_processes[session_id] = {
                "process": proc,
                "queue": output_queue,
                "thread": reader_thread,
                "program": str(js_path),
                "started": datetime.now().isoformat(),
                "log_file": str(log_file)
            }
            
            stdout_text = ''.join(stdout_capture)
            
            return {
                "ok": True,
                "session_id": session_id,
                "pid": proc.pid,
                "is_alive": True,
                "log_file": str(log_file),
                "message": f"✅ {js_path.name} ejecutado (PID {proc.pid})",
                "type": "nodejs",
                "stdout": stdout_text
            }
            
        except Exception as e:
            return {"ok": False, "error": f"Error ejecutando Node.js: {str(e)}"}
    
    @classmethod
    def _run_native(cls, file_path, args=None):
        try:
            import platform
            if platform.system() != "Windows":
                return {"ok": False, "error": "Este programa solo funciona en Windows"}
            
            if not file_path.exists():
                return {"ok": False, "error": f"Archivo no encontrado: {file_path}"}
            
            cmd = [str(file_path)]
            if args:
                cmd.extend(args)
            
            session_id = str(uuid.uuid4())
            output_queue = queue.Queue()
            log_file = cls.OUTPUT_DIR / f"{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            
            project_root = Path(__file__).parent.parent.parent
            
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                cwd=str(project_root),
                shell=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            stdout_capture = []
            
            def read_output():
                try:
                    for line in iter(proc.stdout.readline, ''):
                        if line:
                            stdout_capture.append(line)
                            output_queue.put({"type": "output", "data": line})
                            with open(log_file, 'a', encoding='utf-8') as f:
                                f.write(line)
                except Exception as e:
                    output_queue.put({"type": "error", "data": str(e)})
                finally:
                    proc.stdout.close()
                    proc.wait()
                    output_queue.put({"type": "exit", "code": proc.returncode})
            
            reader_thread = threading.Thread(target=read_output, daemon=True)
            reader_thread.start()
            
            cls._active_processes[session_id] = {
                "process": proc,
                "queue": output_queue,
                "thread": reader_thread,
                "program": str(file_path),
                "started": datetime.now().isoformat(),
                "log_file": str(log_file)
            }
            
            stdout_text = ''.join(stdout_capture)
            
            return {
                "ok": True,
                "session_id": session_id,
                "pid": proc.pid,
                "is_alive": True,
                "log_file": str(log_file),
                "message": f"✅ {file_path.name} ejecutado (PID {proc.pid})",
                "type": "native",
                "stdout": stdout_text
            }
            
        except Exception as e:
            return {"ok": False, "error": f"Error ejecutando: {str(e)}"}
    
    @classmethod
    def _open_pdf(cls, pdf_path):
        import base64
        
        try:
            with open(pdf_path, "rb") as f:
                pdf_data = base64.b64encode(f.read()).decode("utf-8")
            
            html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📄 {pdf_path.name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ height: 100%; background: #0a0514; font-family: 'Segoe UI', sans-serif; }}
        .container {{ width: 100%; height: 100%; display: flex; flex-direction: column; }}
        .toolbar {{
            background: linear-gradient(to right, #1a0033, #2e0854);
            padding: 8px 16px;
            border-bottom: 1px solid #6a0dad;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            min-height: 48px;
            flex-shrink: 0;
        }}
        .toolbar h3 {{ color: #da70d6; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 50%; }}
        .toolbar .actions {{ display: flex; gap: 6px; flex-wrap: wrap; }}
        .toolbar button {{
            background: #4b0082;
            color: #fff;
            border: 1px solid #9370db;
            padding: 4px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
        }}
        .toolbar button:hover {{ background: #6a0dad; }}
        .toolbar .btn-close {{ background: #8b0000; border-color: #ff0000; }}
        .toolbar .btn-close:hover {{ background: #cc0000; }}
        .pdf-viewer {{
            flex: 1;
            background: #1a1a2e;
            overflow: auto;
            padding: 10px;
            display: flex;
            justify-content: center;
            align-items: flex-start;
        }}
        .pdf-viewer embed {{
            width: 100%;
            height: 100%;
            min-height: 600px;
            border: none;
            border-radius: 4px;
        }}
        @media (max-width: 768px) {{
            .toolbar h3 {{ font-size: 11px; max-width: 40%; }}
            .toolbar button {{ font-size: 10px; padding: 3px 8px; }}
            .pdf-viewer embed {{ min-height: 400px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="toolbar">
            <h3>📄 {pdf_path.name}</h3>
            <div class="actions">
                <button onclick="window.print()">🖨️ Imprimir</button>
                <button onclick="window.close()" class="btn-close">✕ Cerrar</button>
            </div>
        </div>
        <div class="pdf-viewer">
            <embed src="data:application/pdf;base64,{pdf_data}" type="application/pdf">
        </div>
    </div>
</body>
</html>'''
            
            viewer_file = cls.VIEWER_DIR / f"pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            viewer_file.write_text(html_content, encoding="utf-8")
            
            return {
                "ok": True,
                "type": "pdf",
                "viewer_path": str(viewer_file),
                "message": f"📄 {pdf_path.name} abierto en visor"
            }
            
        except Exception as e:
            return {"ok": False, "error": f"Error abriendo PDF: {e}"}
    
    @classmethod
    def _view_text(cls, text_path):
        try:
            content = text_path.read_text(encoding="utf-8", errors="replace")
            if len(content) > 100000:
                content = content[:100000] + "\n\n... (archivo truncado)"
            
            html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📝 {text_path.name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ height: 100%; background: #0a0514; font-family: 'Segoe UI', monospace; }}
        .container {{ width: 100%; height: 100%; display: flex; flex-direction: column; background: #0a0a1a; }}
        .toolbar {{
            background: linear-gradient(to right, #1a0033, #2e0854);
            padding: 8px 16px;
            border-bottom: 1px solid #6a0dad;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            min-height: 48px;
            flex-shrink: 0;
        }}
        .toolbar h3 {{ color: #da70d6; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 50%; }}
        .toolbar .info {{ color: #9370db; font-size: 12px; }}
        .toolbar .btn-close {{
            background: #8b0000;
            border: 1px solid #ff0000;
            color: #fff;
            padding: 4px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }}
        .toolbar .btn-close:hover {{ background: #cc0000; }}
        .content {{
            flex: 1;
            padding: 16px;
            overflow: auto;
            background: #0a0a1a;
            color: #e6e6fa;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            white-space: pre-wrap;
            word-wrap: break-word;
            line-height: 1.6;
        }}
        @media (max-width: 768px) {{
            .content {{ font-size: 12px; padding: 10px; }}
            .toolbar h3 {{ font-size: 12px; max-width: 40%; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="toolbar">
            <h3>📝 {text_path.name}</h3>
            <span class="info">{len(content)} caracteres • <button onclick="window.close()" class="btn-close">✕ Cerrar</button></span>
        </div>
        <div class="content">{content}</div>
    </div>
</body>
</html>'''
            
            viewer_file = cls.VIEWER_DIR / f"text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            viewer_file.write_text(html_content, encoding="utf-8")
            
            return {
                "ok": True,
                "type": "text",
                "viewer_path": str(viewer_file),
                "message": f"📝 {text_path.name} abierto en visor"
            }
            
        except Exception as e:
            return {"ok": False, "error": f"Error abriendo texto: {e}"}
    
    @classmethod
    def _view_image(cls, image_path):
        import base64
        
        try:
            with open(image_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode("utf-8")
            
            ext = image_path.suffix.lower()[1:]
            mime = {
                'jpg': 'jpeg', 'jpeg': 'jpeg', 'png': 'png',
                'gif': 'gif', 'bmp': 'bmp', 'webp': 'webp',
                'svg': 'svg+xml', 'ico': 'x-icon'
            }.get(ext, ext)
            
            html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🖼️ {image_path.name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ height: 100%; background: #0a0514; font-family: 'Segoe UI', sans-serif; }}
        .container {{ width: 100%; height: 100%; display: flex; flex-direction: column; }}
        .toolbar {{
            background: linear-gradient(to right, #1a0033, #2e0854);
            padding: 8px 16px;
            border-bottom: 1px solid #6a0dad;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            min-height: 48px;
            flex-shrink: 0;
        }}
        .toolbar h3 {{ color: #da70d6; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 50%; }}
        .toolbar .btn-close {{
            background: #8b0000;
            border: 1px solid #ff0000;
            color: #fff;
            padding: 4px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }}
        .toolbar .btn-close:hover {{ background: #cc0000; }}
        .image-container {{
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #0a0a1a;
            padding: 16px;
        }}
        .image-container img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: 8px;
            box-shadow: 0 0 50px rgba(106,13,173,0.3);
        }}
        @media (max-width: 768px) {{
            .toolbar h3 {{ font-size: 12px; max-width: 40%; }}
            .image-container {{ padding: 10px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="toolbar">
            <h3>🖼️ {image_path.name}</h3>
            <div>
                <button onclick="window.close()" class="btn-close">✕ Cerrar</button>
            </div>
        </div>
        <div class="image-container">
            <img src="data:image/{mime};base64,{img_data}" alt="{image_path.name}">
        </div>
    </div>
</body>
</html>'''
            
            viewer_file = cls.VIEWER_DIR / f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            viewer_file.write_text(html_content, encoding="utf-8")
            
            return {
                "ok": True,
                "type": "image",
                "viewer_path": str(viewer_file),
                "message": f"🖼️ {image_path.name} abierto en visor"
            }
            
        except Exception as e:
            return {"ok": False, "error": f"Error abriendo imagen: {e}"}
    
    @classmethod
    def get_output(cls, session_id, timeout=0.3):
        """Obtiene la salida disponible de un proceso"""
        if session_id not in cls._active_processes:
            return {"ok": False, "error": "Sesión no encontrada"}
        
        proc_info = cls._active_processes[session_id]
        output_queue = proc_info["queue"]
        
        outputs = []
        try:
            while True:
                item = output_queue.get(timeout=timeout)
                outputs.append(item)
                if item.get("type") in ["exit", "error"]:
                    break
        except queue.Empty:
            pass
        
        is_alive = proc_info["process"].poll() is None
        
        return {
            "ok": True,
            "outputs": outputs,
            "is_alive": is_alive
        }
    
    @classmethod
    def send_input(cls, session_id, data):
        if session_id not in cls._active_processes:
            return {"ok": False, "error": "Sesión no encontrada"}
        
        proc_info = cls._active_processes[session_id]
        proc = proc_info["process"]
        
        try:
            proc.stdin.write(data + "\n")
            proc.stdin.flush()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    @classmethod
    def stop_process(cls, session_id):
        if session_id not in cls._active_processes:
            return {"ok": False, "error": "Sesión no encontrada"}
        
        proc_info = cls._active_processes[session_id]
        proc = proc_info["process"]
        
        try:
            proc.terminate()
            proc.wait(timeout=5)
            return {"ok": True, "message": "Proceso detenido"}
        except Exception as e:
            try:
                proc.kill()
                return {"ok": True, "message": "Proceso forzado"}
            except:
                return {"ok": False, "error": str(e)}
        finally:
            if session_id in cls._active_processes:
                del cls._active_processes[session_id]
    
    @classmethod
    def list_active(cls):
        return [
            {
                "session_id": sid,
                "pid": info["process"].pid,
                "program": info["program"],
                "started": info["started"],
                "log_file": info.get("log_file"),
                "is_alive": info["process"].poll() is None
            }
            for sid, info in cls._active_processes.items()
        ]
