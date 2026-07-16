"""Detector de programas portables en system/program/"""
from pathlib import Path
from datetime import datetime
from system.config import PROGRAM_DIR, PROGRAMS_CACHE, save_json, load_json, log

class ProgramDetector:
    EXECUTABLE_EXTS = {'.exe', '.bat', '.cmd', '.py', '.sh', '.com', '.msi', '.pif', '.scr', '.jar', '.js'}
    
    def __init__(self):
        self.program_dir = PROGRAM_DIR
        self.cache_file = PROGRAMS_CACHE
    
    def scan(self):
        """Escanea system/program/ buscando ejecutables"""
        programs = []
        
        if not self.program_dir.exists():
            log(f"📁 Creando directorio de programas: {self.program_dir}")
            self.program_dir.mkdir(parents=True, exist_ok=True)
            return programs
        
        log(f"🔍 Escaneando {self.program_dir}...")
        
        try:
            for item in self.program_dir.rglob('*'):
                if item.is_file() and item.suffix.lower() in self.EXECUTABLE_EXTS:
                    try:
                        stat = item.stat()
                        programs.append({
                            "name": item.stem,
                            "filename": item.name,
                            "path": str(item),
                            "relative_path": str(item.relative_to(self.program_dir)),
                            "ext": item.suffix.lower(),
                            "size": stat.st_size,
                            "size_fmt": self._format_size(stat.st_size),
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "type": self._detect_type(item.suffix.lower(), item),
                            "category": self._categorize(item),
                            "icon": self._get_icon(item.suffix.lower())
                        })
                    except Exception as e:
                        log(f"⚠️ Error escaneando {item}: {e}", "WARN")
            
            log(f"✅ {len(programs)} programas detectados en {self.program_dir}")
            
        except Exception as e:
            log(f"❌ Error escaneando programas: {e}", "ERROR")
        
        save_json(self.cache_file, programs)
        return programs
    
    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def _detect_type(self, ext, path):
        name_lower = path.stem.lower()
        if ext == '.exe':
            if 'portable' in name_lower or 'port' in name_lower:
                return "portable"
            if 'server' in name_lower or 'httpd' in name_lower or 'nginx' in name_lower:
                return "server"
            if 'install' in name_lower or 'setup' in name_lower:
                return "installer"
            return "application"
        elif ext in ['.bat', '.cmd']:
            return "batch"
        elif ext == '.py':
            return "python"
        elif ext == '.js':
            return "nodejs"
        elif ext == '.sh':
            return "shell"
        elif ext == '.jar':
            return "java"
        else:
            return "other"
    
    def _categorize(self, path):
        name_lower = path.stem.lower()
        categories = {
            "browser": ['firefox', 'chrome', 'brave', 'edge', 'opera', 'vivaldi'],
            "editor": ['code', 'notepad', 'sublime', 'atom', 'vim', 'nano', 'edit'],
            "media": ['vlc', 'mpv', 'audacity', 'obs', 'ffmpeg', 'media'],
            "dev": ['python', 'node', 'git', 'docker', 'gcc', 'java', 'maven'],
            "server": ['apache', 'nginx', 'mysql', 'postgres', 'mongo', 'redis'],
            "office": ['libreoffice', 'word', 'excel', 'powerpoint', 'pdf'],
            "utility": ['7zip', 'winrar', 'ccleaner', 'defrag', 'disk', 'backup'],
            "game": ['game', 'play', 'steam', 'epic', 'minecraft']
        }
        for cat, keywords in categories.items():
            if any(k in name_lower for k in keywords):
                return cat
        return "other"
    
    def _get_icon(self, ext):
        icons = {
            '.exe': '⚙️',
            '.bat': '📜',
            '.cmd': '📜',
            '.py': '🐍',
            '.js': '📦',
            '.sh': '🐚',
            '.com': '💻',
            '.msi': '📦',
            '.pif': '📎',
            '.scr': '🖥️',
            '.jar': '☕'
        }
        return icons.get(ext, '📄')
    
    def get_cached(self):
        cached = load_json(self.cache_file, [])
        if not cached:
            return self.scan()
        return cached
    
    def refresh(self):
        return self.scan()