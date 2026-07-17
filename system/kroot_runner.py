"""
Kroot Corp - Ejecutar en el mismo proceso que Kalm OS
"""
import os
import sys
import threading
import time
from pathlib import Path

# Ruta al proyecto Kroot Corp
KROOT_DIR = Path(__file__).parent / "Program" / "kroot_corp"
KROOT_APP_DIR = KROOT_DIR / "app"

def start_kroot_server():
    """Inicia el servidor de Kroot Corp en un hilo separado"""
    if not KROOT_DIR.exists():
        print("❌ Kroot Corp no encontrado en:", KROOT_DIR)
        return False
    
    try:
        # Agregar al path
        sys.path.insert(0, str(KROOT_DIR))
        
        # Verificar dependencias
        try:
            import fastapi
            import uvicorn
        except ImportError:
            print("📦 Instalando dependencias de Kroot Corp...")
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", 
                          str(KROOT_DIR / "requirements.txt")], capture_output=True)
        
        # Importar la app
        from app.main import app
        import uvicorn
        
        print("🏢 Kroot Corp IA iniciado en puerto 8000")
        
        # Ejecutar en un hilo
        def run():
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return True
        
    except Exception as e:
        print(f"❌ Error iniciando Kroot Corp: {e}")
        return False

# Iniciar automáticamente al importar
start_kroot_server()