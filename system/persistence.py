"""Sistema de persistencia para entornos cloud"""
import json
import shutil
from pathlib import Path
from datetime import datetime
from system.config import BASE_DIR, DATA_DIR, log

class PersistenceManager:
    """Maneja la persistencia de datos entre sesiones"""
    
    # En Render, usar /tmp o /data
    PERSISTENCE_DIR = Path("/data/kalm_os") if Path("/data").exists() else (BASE_DIR / "kalm_data")
    BACKUP_DIR = PERSISTENCE_DIR / "backups"
    
    @classmethod
    def init(cls):
        """Inicializa el sistema de persistencia"""
        cls.PERSISTENCE_DIR.mkdir(parents=True, exist_ok=True)
        cls.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        log(f"💾 Persistencia: {cls.PERSISTENCE_DIR}")
    
    @classmethod
    def save_data(cls, name, data):
        """Guarda datos de forma persistente"""
        cls.init()
        file_path = cls.PERSISTENCE_DIR / f"{name}.json"
        file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    
    @classmethod
    def load_data(cls, name, default=None):
        """Carga datos persistentes"""
        cls.init()
        file_path = cls.PERSISTENCE_DIR / f"{name}.json"
        if file_path.exists():
            try:
                return json.loads(file_path.read_text(encoding="utf-8"))
            except:
                return default
        return default
    
    @classmethod
    def save_file(cls, name, file_path):
        """Guarda un archivo de forma persistente"""
        cls.init()
        dest = cls.PERSISTENCE_DIR / "files" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, dest)
        return str(dest)
    
    @classmethod
    def load_file(cls, name):
        """Carga un archivo persistente"""
        cls.init()
        file_path = cls.PERSISTENCE_DIR / "files" / name
        if file_path.exists():
            return file_path
        return None
    
    @classmethod
    def list_files(cls):
        """Lista archivos persistentes"""
        cls.init()
        files_dir = cls.PERSISTENCE_DIR / "files"
        if files_dir.exists():
            return [f.name for f in files_dir.iterdir() if f.is_file()]
        return []
    
    @classmethod
    def create_backup(cls):
        """Crea un backup de todos los datos"""
        cls.init()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = cls.BACKUP_DIR / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copiar todos los datos
        for item in cls.PERSISTENCE_DIR.iterdir():
            if item.name != "backups" and item.is_dir():
                shutil.copytree(item, backup_dir / item.name, dirs_exist_ok=True)
            elif item.is_file():
                shutil.copy2(item, backup_dir / item.name)
        
        log(f"💾 Backup creado: {backup_dir}")
        return str(backup_dir)
    
    @classmethod
    def restore_backup(cls, backup_name):
        """Restaura un backup"""
        cls.init()
        backup_dir = cls.BACKUP_DIR / backup_name
        if not backup_dir.exists():
            return False
        
        # Restaurar cada elemento
        for item in backup_dir.iterdir():
            dest = cls.PERSISTENCE_DIR / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
        
        log(f"💾 Backup restaurado: {backup_name}")
        return True
    
    @classmethod
    def list_backups(cls):
        """Lista backups disponibles"""
        cls.init()
        if cls.BACKUP_DIR.exists():
            return sorted([d.name for d in cls.BACKUP_DIR.iterdir() if d.is_dir()])
        return []