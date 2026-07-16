"""Configuración global de Kalm OS"""
import json
import os
from pathlib import Path
from datetime import datetime

# ═══ Detectar psutil ═══
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("[!] psutil no instalado. Task Manager en modo limitado.")

# ═══ Detectar entorno (Render / Cloud) ═══
IS_CLOUD = os.environ.get("RENDER") == "true" or os.environ.get("KALM_CLOUD") == "true"

# ═══ Rutas base ═══
BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / "kalm_data"
DRIVE_D = BASE_DIR / "D"
SYSTEM_DIR = BASE_DIR / "system"
# ═══ IMPORTANTE: Usar "Program" con P mayúscula ═══
PROGRAM_DIR = SYSTEM_DIR / "Program"  # <-- CORREGIDO: Program con P mayúscula
VIEWS_DIR = BASE_DIR / "views"
STATIC_DIR = BASE_DIR / "static"

# ═══ En cloud, usar directorio temporal para datos ═══
if IS_CLOUD:
    CLOUD_DATA_DIR = Path("/tmp/kalm_os_data")
    DATA_DIR = CLOUD_DATA_DIR
    DRIVE_D = CLOUD_DATA_DIR / "D"
    SYSTEM_DIR = BASE_DIR / "system"
    PROGRAM_DIR = SYSTEM_DIR / "Program"  # <-- CORREGIDO: Program con P mayúscula
    VIEWS_DIR = BASE_DIR / "views"
    STATIC_DIR = BASE_DIR / "static"

# ═══ Archivos de datos ═══
DNS_FILE = DATA_DIR / "dns_rules.json"
PROXY_FILE = DATA_DIR / "proxy_rules.json"
BG_FILE = DATA_DIR / "background.jpg"
ENV_FILE = BASE_DIR / ".env"
SESSIONS_FILE = DATA_DIR / "sessions.json"
RUNNING_PROCS_FILE = DATA_DIR / "running_procs.json"
PROGRAMS_CACHE = DATA_DIR / "programs_cache.json"  # Este puede quedar igual

# ═══ Funciones de utilidad ═══
def load_env():
    env = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    for k in ["ROOT_USER", "ROOT_PASS", "USER_USER", "USER_PASS", 
              "UI_PORT", "DNS_PORT", "PROXY_PORT", "SESSION_TIMEOUT"]:
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
    except:
        return default

def log(msg, level="INFO"):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] {msg}")

def format_size(b):
    for u in ['B', 'KB', 'MB', 'GB', 'TB']:
        if b < 1024:
            return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} PB"

def get_file_icon(ext):
    icons = {
        '.txt': '📄', '.pdf': '📕', '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️',
        '.gif': '🖼️', '.mp3': '🎵', '.mp4': '🎬', '.zip': '📦', '.rar': '📦',
        '.exe': '⚙️', '.bat': '📜', '.cmd': '📜', '.sh': '🐚', '.py': '🐍',
        '.js': '📦', '.html': '🌐', '.css': '🎨', '.json': '📋', '.md': '📝',
        '.sql': '🗄️', '.db': '🗄️', '.msi': '📦', '.com': '💻', '.scr': '🖥️',
        '.jar': '☕', '.xml': '📋', '.yaml': '📋', '.yml': '📋', '.csv': '📊',
        '.ico': '🖼️', '.bmp': '🖼️', '.webp': '🖼️', '.svg': '🖼️'
    }
    return icons.get(ext.lower(), '📄')

# ═══ Verificar estructura ═══
def ensure_structure():
    log("🔍 Verificando estructura de carpetas...")
    dirs = [
        DATA_DIR, DRIVE_D,
        DRIVE_D / "Apps", DRIVE_D / "Projects", DRIVE_D / "Scripts",
        DRIVE_D / "Documents", DRIVE_D / "Media", DRIVE_D / "Servers",
        DRIVE_D / "Downloads", DRIVE_D / "Desktop",
        DATA_DIR / "logs", DATA_DIR / "temp",
        SYSTEM_DIR, PROGRAM_DIR,  # PROGRAM_DIR ahora es system/Program
        VIEWS_DIR, STATIC_DIR / "css", STATIC_DIR / "js", STATIC_DIR / "img"
    ]
    for d in dirs:
        try:
            d.mkdir(parents=True, exist_ok=True)
            log(f"   ✓ {d.relative_to(BASE_DIR)}")
        except Exception as e:
            log(f"   ⚠️ Error creando {d}: {e}", "WARN")
    
    if not ENV_FILE.exists():
        ENV_FILE.write_text("""# KALM OS v4.3 - Configuración
ROOT_USER=root
ROOT_PASS=Kalm*4815162342+-
USER_USER=user
USER_PASS=user*26
UI_PORT=8080
DNS_PORT=5353
PROXY_PORT=8888
SESSION_TIMEOUT=3600
""", encoding="utf-8")
        log("   ✅ .env creado")
    
    for f, default in [(SESSIONS_FILE, {}), (RUNNING_PROCS_FILE, []), (PROGRAMS_CACHE, [])]:
        if not f.exists():
            save_json(f, default)
    
    log("✅ Estructura lista\n")

# ═══ Cargar configuración ═══
ENV = load_env()
ROOT_USER = ENV.get("ROOT_USER", "root")
ROOT_PASS = ENV.get("ROOT_PASS", "Kalm*4815162342+-")
USER_USER = ENV.get("USER_USER", "user")
USER_PASS = ENV.get("USER_PASS", "user*26")
UI_PORT = int(ENV.get("UI_PORT", "8080"))
DNS_PORT = int(ENV.get("DNS_PORT", "5353"))
PROXY_PORT = int(ENV.get("PROXY_PORT", "8888"))
SESSION_TIMEOUT = int(ENV.get("SESSION_TIMEOUT", "3600"))

# Crear estructura al importar
ensure_structure()

log(f"🌍 Entorno: {'Cloud' if IS_CLOUD else 'Local'}")
log(f"📁 Datos: {DATA_DIR}")
log(f"📁 Programas: {PROGRAM_DIR}")