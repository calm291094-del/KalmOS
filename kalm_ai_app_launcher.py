#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KALM AI APP - Launcher para Render/Cloud
Ejecuta kalm_ai_app.py con el flag --kalm y mantiene el proceso vivo
"""
import sys
import os
import subprocess
import time
import threading
from pathlib import Path

possible_paths = [
    Path(__file__).parent / "system" / "Program" / "kalm_ai_app.py",
    Path(__file__).parent / "kalm_ai_app.py",
    Path("/app/system/Program/kalm_ai_app.py"),
    Path("/app/kalm_ai_app.py"),
]

def find_kalm_ai_app():
    """Busca kalm_ai_app.py en varias ubicaciones"""
    for p in possible_paths:
        if p.exists():
            return p
    return None

def run_kalm_ai():
    """Ejecuta kalm_ai_app.py con --kalm"""
    app_path = find_kalm_ai_app()
    
    if not app_path:
        print("❌ No se encontró kalm_ai_app.py")
        print("   Buscado en:", [str(p) for p in possible_paths])
        return
    
    print(f"🚀 Iniciando Kalm AI desde: {app_path}")
    print(f"📂 Directorio: {app_path.parent}")
    
    # Cambiar al directorio del proyecto para resolver imports
    os.chdir(str(Path(__file__).parent))
    
    # Ejecutar con el flag --kalm
    cmd = [sys.executable, str(app_path), "--kalm"]
    print(f"📝 Comando: {' '.join(cmd)}")
    sys.stdout.flush()
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando Kalm AI: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Kalm AI detenido")
        sys.exit(0)

if __name__ == "__main__":
    run_kalm_ai()
