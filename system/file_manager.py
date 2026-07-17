"""Explorador de archivos - COMPLETO Y CORREGIDO"""
import shutil
import os
from pathlib import Path
from datetime import datetime
from system.config import DRIVE_D, format_size, get_file_icon, log

class FileManager:
    @staticmethod
    def clean_path(path):
        """Limpia y normaliza una ruta - SIEMPRE retorna string"""
        if not path:
            return str(DRIVE_D)
        
        if isinstance(path, Path):
            path = str(path)
        
        # Si es /D o /D/, convertir a DRIVE_D
        if path == "/D" or path == "/D/":
            return str(DRIVE_D)
        
        # Si empieza con /D/, reemplazar
        if path.startswith("/D/"):
            rel_path = path[3:]  # Quita "/D/"
            return str(DRIVE_D / rel_path)
        
        # Si es D: o D:/ o D:\, convertir a DRIVE_D
        if path in ["D:", "D:/", "D:\\"]:
            return str(DRIVE_D)
        
        # Si empieza con D: pero no tiene \, corregir
        if path.startswith("D:") and not path.startswith("D:\\"):
            path = path.replace("D:", str(DRIVE_D))
        
        return path
    
    @staticmethod
    def is_safe_path(path):
        """Verifica si una ruta está dentro de DRIVE_D"""
        try:
            clean = FileManager.clean_path(path)
            path_str = str(Path(clean).resolve()).lower().replace('/', '\\')
            drive_str = str(DRIVE_D.resolve()).lower().replace('/', '\\')
            return path_str.startswith(drive_str)
        except Exception as e:
            log(f"Error en is_safe_path: {e}", "ERROR")
            return False
    
    @staticmethod
    def list_directory(path):
        """Lista el contenido de un directorio"""
        try:
            clean_path = FileManager.clean_path(path)
            path_obj = Path(clean_path).resolve()
            
            if not FileManager.is_safe_path(str(path_obj)):
                return {"error": "Acceso denegado", "items": [], "path": str(path_obj)}
            
            if not path_obj.exists():
                return {"error": f"No existe: {path_obj}", "items": [], "path": str(path_obj)}
            
            if not path_obj.is_dir():
                return {"error": "No es un directorio", "items": [], "path": str(path_obj)}
            
            items = []
            for item in path_obj.iterdir():
                try:
                    is_dir = item.is_dir()
                    stat = item.stat() if item.exists() else None
                    
                    # Construir ruta para el frontend (usar /D/)
                    rel_path = str(item).replace(str(DRIVE_D), "/D").replace("\\", "/")
                    
                    items.append({
                        "name": item.name,
                        "path": rel_path,
                        "is_dir": is_dir,
                        "size": stat.st_size if stat and not is_dir else 0,
                        "size_fmt": format_size(stat.st_size) if stat and not is_dir else "-",
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M") if stat else "-",
                        "icon": "📁" if is_dir else get_file_icon(item.suffix),
                        "ext": item.suffix.lower() if not is_dir else ""
                    })
                except Exception as e:
                    continue
            
            items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
            
            parent = None
            if str(path_obj) != str(DRIVE_D):
                parent_rel = str(path_obj.parent).replace(str(DRIVE_D), "/D").replace("\\", "/")
                parent = parent_rel if parent_rel != "/D" else "/D"
            
            log(f"📂 Listando {path_obj}: {len(items)} items")
            
            return {
                "path": str(path_obj),
                "items": items,
                "parent": parent
            }
            
        except Exception as e:
            log(f"Error en list_directory: {e}", "ERROR")
            return {"error": str(e), "items": [], "path": str(path)}
    
    @staticmethod
    def create_folder(path, name):
        try:
            clean_path = FileManager.clean_path(path)
            path_obj = Path(clean_path).resolve()
            new_path = path_obj / name
            
            if not FileManager.is_safe_path(str(new_path)):
                return {"ok": False, "error": "Acceso denegado"}
            
            new_path.mkdir(parents=True, exist_ok=False)
            return {"ok": True, "path": str(new_path)}
        except FileExistsError:
            return {"ok": False, "error": "La carpeta ya existe"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    @staticmethod
    def delete(path):
        try:
            clean_path = FileManager.clean_path(path)
            path_obj = Path(clean_path).resolve()
            
            if not FileManager.is_safe_path(str(path_obj)):
                return {"ok": False, "error": "Acceso denegado"}
            
            if path_obj.is_dir():
                shutil.rmtree(path_obj)
            else:
                path_obj.unlink()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    @staticmethod
    def search(query, path=None):
        try:
            clean_path = FileManager.clean_path(path) if path else str(DRIVE_D)
            search_path = Path(clean_path).resolve()
            
            if not FileManager.is_safe_path(str(search_path)):
                return {"error": "Acceso denegado"}
            
            results = []
            query_lower = query.lower()
            
            for item in search_path.rglob("*"):
                try:
                    if query_lower in item.name.lower() and item.is_file():
                        stat = item.stat()
                        rel_path = str(item).replace(str(DRIVE_D), "/D").replace("\\", "/")
                        results.append({
                            "name": item.name,
                            "path": rel_path,
                            "size_fmt": format_size(stat.st_size),
                            "icon": get_file_icon(item.suffix)
                        })
                        if len(results) >= 100:
                            break
                except:
                    continue
            
            return {"results": results}
        except Exception as e:
            return {"error": str(e)}