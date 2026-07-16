#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║  KALM OS v4.3 - Detención Mejorada + Monitor de Red      ║
║  Dark Fantasy Edition - Safe for Work                    ║
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
    UI_PORT, DNS_PORT, PROXY_PORT, ROOT_USER, ROOT_PASS, USER_USER, USER_PASS
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
║     v4.3 - Network Monitor + Improved Process Kill       ║
║     Dark Fantasy Edition                                 ║
╚══════════════════════════════════════════════════════════╝
    """)


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
    
    # ═══ INICIAR MONITOR DE RED ═══
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
    log(f"\n👥 Usuarios:")
    log(f"   👑 root  / {ROOT_PASS}")
    log(f"   👤 user  / {USER_PASS}")
    log("=" * 60)
    log("\n💡 NUEVO en v4.3:")
    log("   • Detención mejorada: mata proceso + todos sus hijos")
    log("   • Monitor de red: velocidad de subida/bajada en tiempo real")
    log("   • Job Objects: procesos aislados en contenedores Windows")
    log("   • Botón '⏹ Detener Todo' en Servidores")
    log("\n💡 Presiona Ctrl+C para apagar Kalm OS")
    
    try:
        time.sleep(1)
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