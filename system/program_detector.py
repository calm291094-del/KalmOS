"""Detector de programas portables en system/Program/"""
from pathlib import Path
from datetime import datetime
from system.config import BASE_DIR, PROGRAM_DIR, PROGRAMS_CACHE, save_json, load_json, log
import os

class ProgramDetector:
    EXECUTABLE_EXTS = {'.exe', '.bat', '.cmd', '.py', '.sh', '.com', '.msi', '.pif', '.scr', '.jar', '.js'}
    
    # Mapeo de nombres de archivo a categorías
    CATEGORY_MAP = {
        # Juegos
        'snake': 'game',
        'buscaminas': 'game',
        'sokoban': 'game',
        'blackjack': 'game',
        'ajedrez': 'game',
        'ajedrez-ia-basica': 'game',
        'cartas': 'game',
        'gato': 'game',
        'memoria': 'game',
        'piedra_papel_tijera': 'game',
        'ahorcado': 'game',
        # Herramientas
        'herramientas': 'utility',
        'calculadora': 'utility',
        'calculadora_cientifica': 'utility',
        'conversor_unidades': 'utility',
        'generador_passwords': 'utility',
        'analizador_texto': 'utility',
        'editor_texto': 'utility',
        'gestor_archivos': 'utility',
        'ordenar_archivos': 'utility',
        'tareas': 'utility',
        'temporizador': 'utility',
        'reloj': 'utility',
        'lector_rss': 'utility',
        'explorador_red': 'utility',
        'clima': 'utility',
        'reproductor_musica': 'media',
        # Otros
        'prueba': 'other'
    }
    
    def __init__(self):
        self.program_dir = PROGRAM_DIR
        self.cache_file = PROGRAMS_CACHE
    
    def scan(self):
        """Escanea system/Program/ buscando ejecutables"""
        programs = []
        
        log(f"📂 BASE_DIR: {BASE_DIR}")
        log(f"📂 PROGRAM_DIR: {self.program_dir}")
        log(f"📂 PROGRAM_DIR existe: {self.program_dir.exists()}")
        
        if not self.program_dir.exists():
            log(f"📁 Creando directorio de programas: {self.program_dir}")
            try:
                self.program_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                log(f"❌ Error creando directorio: {e}", "ERROR")
            return programs
        
        # Listar archivos
        try:
            all_items = list(self.program_dir.iterdir())
            log(f"📂 Archivos en {self.program_dir}: {[f.name for f in all_items if f.is_file()]}")
        except Exception as e:
            log(f"❌ Error listando directorio: {e}", "ERROR")
        
        log(f"🔍 Escaneando {self.program_dir}...")
        
        try:
            for item in self.program_dir.rglob('*'):
                if item.is_file():
                    ext = item.suffix.lower()
                    if ext in self.EXECUTABLE_EXTS:
                        try:
                            stat = item.stat()
                            stem = item.stem.lower()
                            
                            # Determinar categoría
                            category = self.CATEGORY_MAP.get(stem, 'other')
                            
                            # Si es un juego, asegurar categoría game
                            if 'game' in stem or 'juego' in stem:
                                category = 'game'
                            # Si es una herramienta
                            if any(key in stem for key in ['calculadora', 'conversor', 'generador', 'analizador', 'editor', 'gestor', 'ordenar', 'tareas', 'temporizador', 'reloj', 'lector', 'explorador', 'clima', 'herramientas']):
                                category = 'utility'
                            
                            programs.append({
                                "name": item.stem,
                                "filename": item.name,
                                "path": str(item),
                                "relative_path": str(item.relative_to(self.program_dir)),
                                "ext": ext,
                                "size": stat.st_size,
                                "size_fmt": self._format_size(stat.st_size),
                                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                "type": self._detect_type(ext, item),
                                "category": category,
                                "icon": self._get_icon(ext)
                            })
                            log(f"   ✅ Detectado: {item.name} (categoría: {category})")
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