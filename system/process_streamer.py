"""Gestor de procesos con streaming de salida en tiempo real"""
import subprocess
import threading
import queue
import time
import uuid
from pathlib import Path
from datetime import datetime
from system.config import log

class ProcessStreamer:
    """Ejecuta procesos y transmite su salida en tiempo real"""
    
    active_processes = {}  # {session_id: {process, queue, thread}}
    
    @classmethod
    def start_process(cls, program_path, args=None, cwd=None, env=None):
        """
        Inicia un proceso y retorna un session_id para streaming
        """
        program_path = Path(program_path).resolve()
        if not program_path.exists():
            return {"ok": False, "error": f"Programa no encontrado: {program_path}"}
        
        session_id = str(uuid.uuid4())
        output_queue = queue.Queue()
        
        # Preparar comando
        ext = program_path.suffix.lower()
        
        if ext in [".exe", ".com", ".pif", ".scr"]:
            cmd = [str(program_path)]
        elif ext in [".bat", ".cmd"]:
            cmd = ["cmd", "/c", "chcp 65001 >nul && " + str(program_path)]
        elif ext == ".py":
            cmd = ["python", "-X", "utf8", str(program_path)]
        elif ext == ".js":
            node = cls._find_node()
            if not node:
                return {"ok": False, "error": "Node.js no encontrado"}
            cmd = [node, str(program_path)]
        elif ext == ".sh":
            cmd = ["bash", str(program_path)]
        else:
            return {"ok": False, "error": f"Tipo no soportado: {ext}"}
        
        if args:
            cmd.extend(args)
        
        # Crear proceso con pipes para capturar salida
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                cwd=str(cwd or program_path.parent),
                env=env or os.environ.copy(),
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1  # Línea por línea
            )
            
            # Hilo para leer la salida
            def read_output():
                try:
                    for line in iter(proc.stdout.readline, ''):
                        if line:
                            output_queue.put({
                                "type": "output",
                                "data": line,
                                "timestamp": datetime.now().isoformat()
                            })
                except Exception as e:
                    output_queue.put({
                        "type": "error",
                        "data": f"Error leyendo salida: {e}",
                        "timestamp": datetime.now().isoformat()
                    })
                finally:
                    proc.stdout.close()
                    # Esperar a que termine
                    proc.wait()
                    output_queue.put({
                        "type": "exit",
                        "code": proc.returncode,
                        "timestamp": datetime.now().isoformat()
                    })
            
            reader_thread = threading.Thread(target=read_output, daemon=True)
            reader_thread.start()
            
            cls.active_processes[session_id] = {
                "process": proc,
                "queue": output_queue,
                "thread": reader_thread,
                "program": str(program_path),
                "started": datetime.now().isoformat()
            }
            
            log(f"🔒 Proceso iniciado: {program_path.name} (PID {proc.pid})")
            
            return {
                "ok": True,
                "session_id": session_id,
                "pid": proc.pid,
                "program": str(program_path),
                "message": f"✅ {program_path.name} iniciado (PID {proc.pid})"
            }
            
        except Exception as e:
            return {"ok": False, "error": f"Error iniciando proceso: {str(e)}"}
    
    @classmethod
    def get_output(cls, session_id, timeout=0.5):
        """Obtiene la salida disponible del proceso"""
        if session_id not in cls.active_processes:
            return {"ok": False, "error": "Sesión no encontrada"}
        
        proc_info = cls.active_processes[session_id]
        queue = proc_info["queue"]
        
        outputs = []
        try:
            while True:
                item = queue.get(timeout=timeout)
                outputs.append(item)
                if item.get("type") in ["exit", "error"]:
                    break
        except queue.Empty:
            pass
        
        return {
            "ok": True,
            "outputs": outputs,
            "is_alive": proc_info["process"].poll() is None
        }
    
    @classmethod
    def send_input(cls, session_id, data):
        """Envía entrada al proceso"""
        if session_id not in cls.active_processes:
            return {"ok": False, "error": "Sesión no encontrada"}
        
        proc_info = cls.active_processes[session_id]
        proc = proc_info["process"]
        
        try:
            proc.stdin.write(data + "\n")
            proc.stdin.flush()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    @classmethod
    def stop_process(cls, session_id):
        """Detiene un proceso"""
        if session_id not in cls.active_processes:
            return {"ok": False, "error": "Sesión no encontrada"}
        
        proc_info = cls.active_processes[session_id]
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
            del cls.active_processes[session_id]
    
    @classmethod
    def list_active(cls):
        """Lista procesos activos"""
        return [
            {
                "session_id": sid,
                "pid": info["process"].pid,
                "program": info["program"],
                "started": info["started"],
                "is_alive": info["process"].poll() is None
            }
            for sid, info in cls.active_processes.items()
        ]
    
    @classmethod
    def _find_node(cls):
        """Busca Node.js en el sistema"""
        import shutil
        return shutil.which('node') or shutil.which('nodejs')