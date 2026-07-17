"""Persistencia usando GitHub como almacenamiento (gratuito)"""
import json
import base64
import os
import subprocess
from pathlib import Path
from datetime import datetime
from system.config import BASE_DIR, DATA_DIR, log

class GitHubPersistence:
    """Guarda datos en GitHub mediante commits automáticos"""
    
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
    GITHUB_REPO = os.environ.get("GITHUB_REPO", "")
    GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")
    
    @classmethod
    def is_available(cls):
        """Verifica si GitHub está configurado"""
        return bool(cls.GITHUB_TOKEN and cls.GITHUB_REPO)
    
    @classmethod
    def save_data(cls, name, data):
        """Guarda datos en GitHub"""
        if not cls.is_available():
            log("⚠️ GitHub no configurado, guardando localmente", "WARN")
            return cls._save_local(name, data)
        
        try:
            # Preparar datos
            file_path = DATA_DIR / "persistence" / f"{name}.json"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            
            # Hacer commit a GitHub
            return cls._git_commit_and_push(file_path, f"📝 Actualizar {name}")
        except Exception as e:
            log(f"❌ Error guardando en GitHub: {e}", "ERROR")
            return cls._save_local(name, data)
    
    @classmethod
    def load_data(cls, name, default=None):
        """Carga datos desde GitHub (o local si no hay conexión)"""
        # Primero intentar cargar local
        local_file = DATA_DIR / "persistence" / f"{name}.json"
        if local_file.exists():
            try:
                return json.loads(local_file.read_text(encoding="utf-8"))
            except:
                pass
        
        # Si no existe local, intentar desde GitHub
        if cls.is_available():
            try:
                data = cls._fetch_from_github(name)
                if data:
                    # Guardar localmente para futuros usos
                    local_file.parent.mkdir(parents=True, exist_ok=True)
                    local_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                    return data
            except Exception as e:
                log(f"⚠️ Error cargando desde GitHub: {e}", "WARN")
        
        return default
    
    @classmethod
    def _save_local(cls, name, data):
        """Guarda localmente (fallback)"""
        file_path = DATA_DIR / "persistence" / f"{name}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        log(f"💾 Datos guardados localmente: {name}")
        return True
    
    @classmethod
    def _fetch_from_github(cls, name):
        """Obtiene datos desde GitHub usando la API"""
        import requests
        
        url = f"https://api.github.com/repos/{cls.GITHUB_REPO}/contents/kalm_data/persistence/{name}.json?ref={cls.GITHUB_BRANCH}"
        headers = {
            "Authorization": f"token {cls.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            data = base64.b64decode(content["content"]).decode("utf-8")
            return json.loads(data)
        return None
    
    @classmethod
    def _git_commit_and_push(cls, file_path, message):
        """Hace commit y push a GitHub usando git"""
        try:
            # Asegurar que git está configurado
            os.chdir(str(BASE_DIR))
            
            # Configurar usuario
            subprocess.run(["git", "config", "user.email", "kalm-bot@local"], 
                         capture_output=True, text=True)
            subprocess.run(["git", "config", "user.name", "Kalm OS Bot"], 
                         capture_output=True, text=True)
            
            # Hacer add del archivo
            subprocess.run(["git", "add", str(file_path)], capture_output=True, text=True)
            
            # Hacer commit
            result = subprocess.run(
                ["git", "commit", "-m", f"{message} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
                capture_output=True, text=True
            )
            
            # Hacer push
            if cls.GITHUB_TOKEN:
                # Usar token para autenticación
                repo_url = f"https://{cls.GITHUB_TOKEN}@github.com/{cls.GITHUB_REPO}.git"
                subprocess.run(
                    ["git", "push", repo_url, cls.GITHUB_BRANCH],
                    capture_output=True, text=True
                )
            else:
                subprocess.run(["git", "push"], capture_output=True, text=True)
            
            log(f"✅ Datos guardados en GitHub: {file_path.name}")
            return True
            
        except Exception as e:
            log(f"❌ Error en git commit: {e}", "ERROR")
            return cls._save_local(file_path.stem, json.loads(file_path.read_text(encoding="utf-8")))