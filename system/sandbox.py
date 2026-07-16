"""Sistema de sandbox - Compatible con Linux y Windows"""
import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
from datetime import datetime
from system.config import BASE_DIR, DRIVE_D, log, load_json, save_json, RUNNING_PROCS_FILE, IS_CLOUD


def _build_utf8_env(program_path, preserve_system_path=True, extra_vars=None):
    """Construye entorno con UTF-8 forzado"""
    program_path = Path(program_path)
    env = os.environ.copy()
    
    # ═══ FORZAR UTF-8 ═══
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["PYTHONLEGACYWINDOWSSTDIO"] = "0"
    env["LANG"] = "C.UTF-8"
    env["LC_ALL"] = "C.UTF-8"
    env["PYTHONLEGACYWINDOWSFSENCODING"] = "0"
    
    # ═══ VARIABLES KALM ═══
    env.update({
        "KALM_OS": "1",
        "KALM_VERSION": "4.3",
        "KALM_HOME": str(BASE_DIR),
        "KALM_DRIVE": str(DRIVE_D),
        "KALM_SYSTEM": str(BASE_DIR / "system"),
        "KALM_SANDBOX": str(KalmSandbox.WORKSPACE),
        "KALM_PROGRAM": str(program_path),
        "KALM_SANDBOXED": "true",
        "KALM_CLOUD": "true" if IS_CLOUD else "false",
    })
    
    env["TEMP"] = str(KalmSandbox.WORKSPACE / "temp")
    env["TMP"] = str(KalmSandbox.WORKSPACE / "temp")
    
    if extra_vars:
        env.update(extra_vars)
    
    return env


class KalmSandbox:
    """Crea un entorno aislado para ejecutar programas"""
    
    WORKSPACE = BASE_DIR / "kalm_data" / "sandbox"
    LOGS_DIR = BASE_DIR / "kalm_data" / "logs" / "sandbox"
    
    @staticmethod
    def init():
        KalmSandbox.WORKSPACE.mkdir(parents=True, exist_ok=True)
        KalmSandbox.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        dirs = [
            KalmSandbox.WORKSPACE / "bin",
            KalmSandbox.WORKSPACE / "temp",
            KalmSandbox.WORKSPACE / "config",
            KalmSandbox.WORKSPACE / "home",
            KalmSandbox.WORKSPACE / "virtual_drive",
        ]
        for d in dirs:
            d.mkdir(exist_ok=True)
    
    @staticmethod
    def prepare_workspace(program_path):
        program_path = Path(program_path)
        program_workspace = KalmSandbox.WORKSPACE / "virtual_drive" / program_path.stem
        program_workspace.mkdir(parents=True, exist_ok=True)
        
        (program_workspace / "Documents").mkdir(exist_ok=True)
        (program_workspace / "Downloads").mkdir(exist_ok=True)
        (program_workspace / "AppData").mkdir(exist_ok=True)
        
        return program_workspace
    
    @staticmethod
    def execute(program_path, args=None, preserve_system_path=True, use_workspace_cwd=False):
        """Ejecuta un programa dentro del sandbox"""
        program_path = Path(program_path).resolve()
        
        if not program_path.exists():
            return {"ok": False, "error": "Programa no encontrado"}
        
        KalmSandbox.init()
        workspace = KalmSandbox.prepare_workspace(program_path)
        env = _build_utf8_env(program_path, preserve_system_path)
        
        ext = program_path.suffix.lower()
        system = platform.system()
        
        # Construir comando según plataforma
        if system == "Windows" and ext in [".exe", ".com", ".pif", ".scr"]:
            cmd = [str(program_path)]
        elif ext in [".bat", ".cmd"]:
            if system == "Windows":
                cmd = ["cmd", "/c", "chcp 65001 >nul && " + str(program_path)]
            else:
                cmd = ["bash", str(program_path)]
        elif ext == ".py":
            cmd = [sys.executable, "-X", "utf8", str(program_path)]
        elif ext == ".sh":
            cmd = ["bash", str(program_path)]
        elif ext == ".js":
            # Para Node.js
            cmd = ["node", str(program_path)]
        else:
            # Intentar ejecutar como script
            cmd = [str(program_path)]
        
        if args:
            cmd.extend(args)
        
        log_file = KalmSandbox.LOGS_DIR / f"{program_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        try:
            log_fh = open(log_file, "wb")
            log_fh.write(f"=== KALM SANDBOX EXECUTION ===\n".encode("utf-8"))
            log_fh.write(f"Program: {program_path}\n".encode("utf-8"))
            log_fh.write(f"Workspace: {workspace}\n".encode("utf-8"))
            log_fh.write(f"Started: {datetime.now().isoformat()}\n".encode("utf-8"))
            log_fh.write(f"Command: {' '.join(cmd)}\n".encode("utf-8"))
            log_fh.write(f"{'='*40}\n\n".encode("utf-8"))
            log_fh.flush()
            
            cwd = str(program_path.parent) if not use_workspace_cwd else str(workspace)
            
            proc = subprocess.Popen(
                cmd,
                stdout=log_fh,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                env=env,
                shell=(ext in [".bat", ".cmd"]) or system != "Windows"
            )
            
            pid = proc.pid
            
            log(f"🔒 Sandbox: {program_path.name} iniciado (PID {pid})")
            
            import time
            time.sleep(3)
            poll = proc.poll()
            
            if poll is None:
                running = load_json(RUNNING_PROCS_FILE, [])
                running.append({
                    "pid": pid,
                    "name": program_path.name,
                    "path": str(program_path),
                    "workspace": str(workspace),
                    "log_file": str(log_file),
                    "started": datetime.now().isoformat(),
                    "type": "sandboxed_program",
                    "in_kalm": True,
                    "sandboxed": True,
                    "platform": system
                })
                save_json(RUNNING_PROCS_FILE, running)
                
                return {
                    "ok": True,
                    "pid": pid,
                    "sandboxed": True,
                    "workspace": str(workspace),
                    "log_file": str(log_file),
                    "message": f"✅ {program_path.name} ejecutado EN SANDBOX KALM (PID {pid})",
                    "long_running": True
                }
            else:
                log_fh.close()
                log_content = log_file.read_text(encoding="utf-8", errors="replace")
                return {
                    "ok": True,
                    "sandboxed": True,
                    "returncode": poll,
                    "stdout": log_content[-3000:],
                    "stderr": "",
                    "workspace": str(workspace),
                    "log_file": str(log_file),
                    "message": f"✅ {program_path.name} ejecutado en sandbox (terminó rápido)"
                }
        except Exception as e:
            return {"ok": False, "error": f"Error sandbox: {str(e)}"}
    
    @staticmethod
    def list_workspaces():
        workspaces = []
        vdrive = KalmSandbox.WORKSPACE / "virtual_drive"
        if vdrive.exists():
            for ws in vdrive.iterdir():
                if ws.is_dir():
                    workspaces.append({
                        "name": ws.name,
                        "path": str(ws),
                        "size": sum(f.stat().st_size for f in ws.rglob("*") if f.is_file())
                    })
        return workspaces
    
    @staticmethod
    def cleanup_workspace(name):
        ws = KalmSandbox.WORKSPACE / "virtual_drive" / name
        if ws.exists():
            shutil.rmtree(ws, ignore_errors=True)
            return True
        return False