#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║  KALM OS v4.3 - Cloud Ready                            ║
║  Dark Fantasy Edition - Safe for Work                  ║
╚══════════════════════════════════════════════════════════╝
"""

import sys
import os
import threading
import webbrowser
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from system.config import (
    ensure_structure, log,
    UI_PORT, DNS_PORT, PROXY_PORT, ROOT_USER, ROOT_PASS, USER_USER, USER_PASS, IS_CLOUD
)
from system.dns_server import KalmDNSServer
from system.proxy import KalmProxy
from system.web_server import ThreadedHTTPServer, KalmWebHandler
from system.program_detector import ProgramDetector
from system.registry import set_dns_server, set_proxy_server, set_web_server
from system.task_manager import network_monitor


def banner():
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ██╗  ██╗ █████╗ ██╗     ██╗     ███╗   ███╗           ║
║   ██║  ██║██╔══██╗██║     ██║     ████╗ ████║           ║
║   ███████║███████║██║     ██║     ██╔████╔██║           ║
║   ██╔══██║██╔══██║██║     ██║     ██║╚██╔╝██║           ║
║   ██║  ██║██║  ██║███████╗███████╗██║ ╚═╝ ██║           ║
║   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝           ║
║                                                          ║
║     v4.3 - Cloud Ready                                  ║
║     Dark Fantasy Edition                                 ║
╚══════════════════════════════════════════════════════════╝
    """)


def start_kroot_server():
    """Inicia el servidor de Kroot Corp en un hilo separado"""
    try:
        KROOT_DIR = BASE_DIR / "system" / "Program" / "kroot_corp"
        
        if not KROOT_DIR.exists():
            log("⚠️ Kroot Corp no encontrado en: " + str(KROOT_DIR), "WARN")
            return False
        
        log("🏢 Iniciando Kroot Corp IA...")
        
        # Agregar al path
        sys.path.insert(0, str(KROOT_DIR))
        
        # Verificar dependencias
        try:
            import fastapi
            import uvicorn
        except ImportError:
            log("📦 Instalando dependencias de Kroot Corp...")
            import subprocess
            req_file = KROOT_DIR / "requirements.txt"
            if req_file.exists():
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], 
                              capture_output=True, text=True)
        
        # Importar la app
        try:
            from app.main import app
            import uvicorn
            
            log("🏢 Kroot Corp IA iniciado en puerto 8000")
            log("   Usuario: kroot")
            log("   Contraseña: K4815162342")
            
            # Ejecutar en un hilo
            def run_kroot():
                try:
                    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")
                except Exception as e:
                    log(f"❌ Error en servidor Kroot Corp: {e}", "ERROR")
            
            thread = threading.Thread(target=run_kroot, daemon=True)
            thread.start()
            return True
            
        except Exception as e:
            log(f"❌ Error importando Kroot Corp: {e}", "ERROR")
            return False
            
    except Exception as e:
        log(f"❌ Error iniciando Kroot Corp: {e}", "ERROR")
        return False


def main():
    banner()
    
    ensure_structure()
    
    log("🔍 Detectando programas en system/program/...")
    detector = ProgramDetector()
    programs = detector.scan()
    log(f"   ✅ {len(programs)} programas detectados")
    
    log("\n🚀 Iniciando servicios...")
    
    dns_server = KalmDNSServer(DNS_PORT)
    set_dns_server(dns_server)
    threading.Thread(target=dns_server.run, daemon=True).start()
    
    proxy_server = KalmProxy(PROXY_PORT)
    set_proxy_server(proxy_server)
    threading.Thread(target=proxy_server.run, daemon=True).start()
    
    web_server = ThreadedHTTPServer(("0.0.0.0", UI_PORT), KalmWebHandler)
    set_web_server(web_server)
    threading.Thread(target=web_server.serve_forever, daemon=True).start()
    
    # ═══ INICIAR KROOT CORP EN SEGUNDO PLANO ═══
    log("🏢 Iniciando Kroot Corp IA...")
    kroot_thread = threading.Thread(target=start_kroot_server, daemon=True)
    kroot_thread.start()
    
    # Iniciar monitor de red
    log("🌐 Iniciando monitor de red...")
    network_monitor.start()
    
    try:
        from system.pac_generator import PACGenerator
        pac_file = PACGenerator.generate_pac()
        log(f"📄 PAC generado: {pac_file}")
    except Exception as e:
        log(f"⚠️ Error generando PAC: {e}", "WARN")
    
    log("\n" + "=" * 60)
    log("🖥️  KALM OS v4.3 INICIADO")
    log("=" * 60)
    log(f"   🌐 UI:         http://localhost:{UI_PORT}")
    log(f"   🌍 DNS:        puerto {DNS_PORT}")
    log(f"   🔒 Proxy:      puerto {PROXY_PORT}")
    log(f"   💾 Disco D:    {BASE_DIR / 'D'}")
    log(f"   📦 Programs:   {BASE_DIR / 'system' / 'program'}")
    log(f"   🌐 Red:        Monitor activo (ver widget superior)")
    log(f"   ☁️  Cloud:      {'Sí' if IS_CLOUD else 'No'}")
    log(f"\n🏢 Kroot Corp:   http://localhost:8000/dashboard")
    log(f"   👤 Usuario:    kroot")
    log(f"   🔒 Contraseña: K4815162342")
    log(f"\n👥 Usuarios Kalm OS:")
    log(f"   👑 root  / {ROOT_PASS}")
    log(f"   👤 user  / {USER_PASS}")
    log("=" * 60)
    log("\n💡 Presiona Ctrl+C para apagar Kalm OS")
    
    try:
        time.sleep(2)
        if not IS_CLOUD:
            webbrowser.open(f"http://localhost:{UI_PORT}")
    except Exception as e:
        log(f"⚠️ No se pudo abrir navegador: {e}", "WARN")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("\n⏻ Apagando Kalm OS...")
        network_monitor.stop()
        dns_server.stop()
        proxy_server.stop()
        web_server.shutdown()
        log("✅ Kalm OS detenido correctamente")
        sys.exit(0)


if __name__ == "__main__":
    main()
