#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KALM AI APP - Launcher simple que mantiene el proceso vivo
"""
import sys
import os
import subprocess
import time
import signal
from pathlib import Path

def find_kalm_ai_app():
    """Busca kalm_ai_app.py en varias ubicaciones"""
    possible_paths = [
        Path("/app/system/Program/kalm_ai_app.py"),
        Path("/app/kalm_ai_app.py"),
        Path(__file__).parent / "system" / "Program" / "kalm_ai_app.py",
        Path(__file__).parent / "kalm_ai_app.py",
    ]
    
    for p in possible_paths:
        if p.exists():
            return p
    return None

def run_kalm_ai():
    """Ejecuta kalm_ai_app.py con --kalm y mantiene el proceso"""
    app_path = find_kalm_ai_app()
    
    if not app_path:
        print("❌ No se encontró kalm_ai_app.py")
        sys.stdout.flush()
        return
    
    print(f"🚀 Iniciando Kalm AI desde: {app_path}")
    sys.stdout.flush()
    
    # Cambiar al directorio del proyecto
    os.chdir(str(Path(__file__).parent))
    
    # Ejecutar con el flag --kalm
    cmd = [sys.executable, str(app_path), "--kalm"]
    print(f"📝 Comando: {' '.join(cmd)}")
    sys.stdout.flush()
    
    # Iniciar el proceso
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    print(f"✅ Kalm AI iniciado con PID: {process.pid}")
    sys.stdout.flush()
    
    # Leer y mostrar la salida en tiempo real
    def read_output():
        for line in process.stdout:
            print(f"[Kalm AI] {line.strip()}")
            sys.stdout.flush()
    
    import threading
    output_thread = threading.Thread(target=read_output, daemon=True)
    output_thread.start()
    
    # Mantener el proceso vivo
    try:
        while True:
            time.sleep(1)
            if process.poll() is not None:
                print(f"❌ Kalm AI terminó con código: {process.poll()}")
                sys.stdout.flush()
                break
    except KeyboardInterrupt:
        print("\n⏹️ Deteniendo Kalm AI...")
        process.terminate()
        process.wait()
        sys.exit(0)

if __name__ == "__main__":
    run_kalm_ai()
