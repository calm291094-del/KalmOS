"""Gestor de red y archivo hosts"""
import os
import platform
import subprocess
import socket
from pathlib import Path
from system.config import log, BASE_DIR

class NetworkManager:
    MARKER_START = "# >>> KALM OS - Managed Domains >>>"
    MARKER_END = "# <<< Kalm OS - Managed Domains <<<"
    
    @staticmethod
    def get_hosts_path():
        """Obtiene la ruta del archivo hosts según el SO"""
        if platform.system() == "Windows":
            return Path(r"C:\Windows\System32\drivers\etc\hosts")
        else:
            return Path("/etc/hosts")
    
    @staticmethod
    def is_admin():
        """Verifica si se ejecuta con privilegios de administrador"""
        if platform.system() == "Windows":
            try:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                return False
        else:
            return os.geteuid() == 0
    
    @staticmethod
    def read_hosts():
        """Lee el contenido actual del archivo hosts"""
        hosts_path = NetworkManager.get_hosts_path()
        if not hosts_path.exists():
            return ""
        with open(hosts_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    
    @staticmethod
    def write_hosts(content):
        """Escribe en el archivo hosts (requiere admin)"""
        hosts_path = NetworkManager.get_hosts_path()
        try:
            # Backup primero
            backup = hosts_path.with_suffix(".bak")
            if hosts_path.exists():
                with open(hosts_path, "r", encoding="utf-8", errors="ignore") as f:
                    backup.write_text(f.read(), encoding="utf-8")
            
            with open(hosts_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, "Archivo hosts actualizado"
        except PermissionError:
            return False, "Se requieren privilegios de administrador"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_kalm_domains():
        """Obtiene los dominios gestionados por Kalm"""
        content = NetworkManager.read_hosts()
        domains = []
        in_kalm_section = False
        for line in content.split("\n"):
            line = line.strip()
            if NetworkManager.MARKER_START in line:
                in_kalm_section = True
                continue
            if NetworkManager.MARKER_END in line:
                in_kalm_section = False
                continue
            if in_kalm_section and line and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 2:
                    domains.append({"ip": parts[0], "domain": parts[1]})
        return domains
    
    @staticmethod
    def add_domain(domain, ip="127.0.0.1"):
        """Agrega un dominio al archivo hosts"""
        content = NetworkManager.read_hosts()
        
        # Remover sección Kalm existente
        new_content = NetworkManager._remove_kalm_section(content)
        
        # Obtener dominios actuales + el nuevo
        domains = NetworkManager._parse_existing_domains(new_content)
        
        # Agregar/actualizar el nuevo
        existing = {d["domain"]: d for d in domains}
        existing[domain] = {"ip": ip, "domain": domain}
        
        # Reconstruir archivo
        final_content = new_content.rstrip() + "\n\n"
        final_content += NetworkManager.MARKER_START + "\n"
        for d in existing.values():
            final_content += f"{d['ip']}    {d['domain']}\n"
        final_content += NetworkManager.MARKER_END + "\n"
        
        return NetworkManager.write_hosts(final_content)
    
    @staticmethod
    def remove_domain(domain):
        """Elimina un dominio del archivo hosts"""
        content = NetworkManager.read_hosts()
        domains = NetworkManager._parse_existing_domains(content)
        domains = [d for d in domains if d["domain"] != domain]
        
        new_content = NetworkManager._remove_kalm_section(content)
        if domains:
            new_content = new_content.rstrip() + "\n\n"
            new_content += NetworkManager.MARKER_START + "\n"
            for d in domains:
                new_content += f"{d['ip']}    {d['domain']}\n"
            new_content += NetworkManager.MARKER_END + "\n"
        
        return NetworkManager.write_hosts(new_content)
    
    @staticmethod
    def _remove_kalm_section(content):
        """Remueve la sección gestionada por Kalm"""
        lines = content.split("\n")
        new_lines = []
        in_kalm = False
        for line in lines:
            if NetworkManager.MARKER_START in line:
                in_kalm = True
                continue
            if NetworkManager.MARKER_END in line:
                in_kalm = False
                continue
            if not in_kalm:
                new_lines.append(line)
        return "\n".join(new_lines)
    
    @staticmethod
    def _parse_existing_domains(content):
        """Parsea dominios existentes en la sección Kalm"""
        domains = []
        in_kalm = False
        for line in content.split("\n"):
            line = line.strip()
            if NetworkManager.MARKER_START in line:
                in_kalm = True
                continue
            if NetworkManager.MARKER_END in line:
                in_kalm = False
                continue
            if in_kalm and line and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 2:
                    domains.append({"ip": parts[0], "domain": parts[1]})
        return domains
    
    @staticmethod
    def flush_dns():
        """Limpia la caché DNS del sistema"""
        try:
            if platform.system() == "Windows":
                subprocess.run(["ipconfig", "/flushdns"], 
                             capture_output=True, timeout=10)
            else:
                subprocess.run(["sudo", "systemd-resolve", "--flush-caches"],
                             capture_output=True, timeout=10)
            return True, "Caché DNS limpiada"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def check_port_available(port):
        """Verifica si un puerto está disponible"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return True
            except:
                return False
    
    @staticmethod
    def get_network_info():
        """Obtiene información de red del sistema"""
        info = {
            "hostname": socket.gethostname(),
            "is_admin": NetworkManager.is_admin(),
            "hosts_path": str(NetworkManager.get_hosts_path()),
            "kalm_domains": NetworkManager.get_kalm_domains(),
            "port_80_available": NetworkManager.check_port_available(80),
            "port_443_available": NetworkManager.check_port_available(443),
        }
        return info