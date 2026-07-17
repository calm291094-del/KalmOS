#!/usr/bin/env python3
"""
Kroot Corp IA - Lanzador para Kalm OS
Ejecuta el servidor FastAPI en segundo plano y abre el navegador interno
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

# Obtener la ruta del directorio actual
BASE_DIR = Path(__file__).parent.resolve()
APP_DIR = BASE_DIR / "app"

# Añadir al path para que pueda importar los módulos
sys.path.insert(0, str(BASE_DIR))

# Determinar qué puerto usar (evitar conflictos con Kalm OS que usa 8080)
PORT = 8000

def start_server():
    """Inicia el servidor FastAPI en segundo plano"""
    os.chdir(str(BASE_DIR))
    
    # Instalar dependencias si no están instaladas
    try:
        import fastapi
        import uvicorn
    except ImportError:
        print("📦 Instalando dependencias de Kroot Corp...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      capture_output=True, text=True)
    
    # Importar uvicorn después de instalar
    import uvicorn
    
    # Ejecutar el servidor
    from app.main import app
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")

def open_browser():
    """Abre el navegador interno de Kalm OS"""
    time.sleep(2)  # Esperar a que el servidor arranque
    
    # Intentar abrir con el navegador interno de Kalm OS
    try:
        # Usar la función global de Kalm OS
        if 'openWin' in globals() or 'openWin' in dir(__builtins__):
            # Abrir el navegador interno con la URL
            openWin('browser')
            # Esperar a que se abra la ventana
            time.sleep(0.5)
            # Establecer la URL
            url_input = document.getElementById('browser-url')
            if url_input:
                url_input.value = f'http://localhost:{PORT}/dashboard'
                # Navegar
                if 'browserNavigate' in globals() or 'browserNavigate' in dir(__builtins__):
                    browserNavigate()
        else:
            # Fallback: abrir en navegador externo
            webbrowser.open(f'http://localhost:{PORT}/dashboard')
    except Exception as e:
        print(f"⚠️ No se pudo abrir el navegador interno: {e}")
        webbrowser.open(f'http://localhost:{PORT}/dashboard')
    
    print(f"🌐 Kroot Corp IA disponible en: http://localhost:{PORT}/dashboard")
    print("   Usuario: kroot")
    print("   Contraseña: K4815162342")

def main():
    print("🏢 Kroot Corp IA - Iniciando...")
    print(f"📂 Directorio: {BASE_DIR}")
    
    # Crear carpeta de informes si no existe
    informes_dir = Path("D/Informes")
    informes_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Informes guardados en: {informes_dir}")
    
    # Iniciar servidor en un hilo separado
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Abrir el navegador
    open_browser()
    
    # Mantener el script ejecutándose
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ Cerrando Kroot Corp IA...")
        sys.exit(0)

if __name__ == "__main__":
    main()