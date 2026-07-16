"""Ejecutor de scripts"""
from pathlib import Path
from system.config import log
from system.virtual_runner import VirtualRunner


class ScriptRunner:
    @staticmethod
    def run(file_path, args=None):
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            return {"ok": False, "error": f"Archivo no encontrado: {file_path}"}
        
        log(f"🔒 Ejecutando {file_path.name} en mini-OS")
        return VirtualRunner.execute(file_path, args)
    
    @staticmethod
    def get_output(session_id, timeout=0.5):
        return VirtualRunner.get_output(session_id, timeout)
    
    @staticmethod
    def send_input(session_id, data):
        return VirtualRunner.send_input(session_id, data)
    
    @staticmethod
    def stop_process(session_id):
        return VirtualRunner.stop_process(session_id)
    
    @staticmethod
    def list_running():
        return VirtualRunner.list_active()
    
    @staticmethod
    def get_last_log():
        logs = []
        output_dir = VirtualRunner.OUTPUT_DIR
        if output_dir.exists():
            log_files = sorted(output_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
            for f in log_files[:5]:
                try:
                    content = f.read_text(encoding="utf-8", errors="replace")
                    logs.append({
                        "name": f.name,
                        "path": str(f),
                        "content": content[-5000:]
                    })
                except:
                    pass
        
        if logs:
            return {"ok": True, **logs[0]}
        return {"ok": False, "error": "No hay logs disponibles"}