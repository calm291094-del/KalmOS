"""Task Manager, Monitor de Recursos y Monitor de Red"""
import shutil
import time
import threading
from system.config import HAS_PSUTIL, DRIVE_D, format_size

if HAS_PSUTIL:
    import psutil


class NetworkMonitor:
    """Monitor de velocidad de red en tiempo real"""
    
    def __init__(self):
        self.last_sent = 0
        self.last_recv = 0
        self.last_time = time.time()
        self.upload_speed = 0  # bytes/sec
        self.download_speed = 0  # bytes/sec
        self.total_sent = 0
        self.total_recv = 0
        self._running = False
        self._thread = None
    
    def start(self):
        """Inicia el monitor en background"""
        if self._running:
            return
        self._running = True
        # Inicializar valores
        try:
            counters = psutil.net_io_counters()
            self.last_sent = counters.bytes_sent
            self.last_recv = counters.bytes_recv
            self.last_time = time.time()
        except:
            pass
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        self._running = False
    
    def _monitor_loop(self):
        """Loop principal del monitor"""
        while self._running:
            try:
                time.sleep(1)  # Medir cada segundo
                if not HAS_PSUTIL:
                    continue
                
                counters = psutil.net_io_counters()
                current_time = time.time()
                delta_time = current_time - self.last_time
                
                if delta_time > 0:
                    # Calcular velocidad (bytes por segundo)
                    sent_delta = counters.bytes_sent - self.last_sent
                    recv_delta = counters.bytes_recv - self.last_recv
                    
                    self.upload_speed = sent_delta / delta_time
                    self.download_speed = recv_delta / delta_time
                    
                    self.total_sent = counters.bytes_sent
                    self.total_recv = counters.bytes_recv
                    
                    self.last_sent = counters.bytes_sent
                    self.last_recv = counters.bytes_recv
                    self.last_time = current_time
            except Exception as e:
                pass
    
    def get_stats(self):
        """Retorna estadísticas actuales de red"""
        return {
            "upload_speed": self.upload_speed,
            "download_speed": self.download_speed,
            "upload_speed_fmt": format_size(self.upload_speed) + "/s",
            "download_speed_fmt": format_size(self.download_speed) + "/s",
            "total_sent": self.total_sent,
            "total_recv": self.total_recv,
            "total_sent_fmt": format_size(self.total_sent),
            "total_recv_fmt": format_size(self.total_recv),
        }


# Instancia global del monitor de red
network_monitor = NetworkMonitor()


class TaskManager:
    @staticmethod
    def list_processes(limit=100):
        if not HAS_PSUTIL:
            return [{"pid": 0, "name": "psutil no disponible", "cpu": 0, "mem": 0, "status": "N/A"}]
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
            try:
                i = p.info
                procs.append({
                    "pid": i["pid"],
                    "name": i["name"] or "?",
                    "cpu": round(i["cpu_percent"] or 0, 1),
                    "mem": round(i["memory_percent"] or 0, 1),
                    "status": i["status"] or "?"
                })
            except:
                continue
        procs.sort(key=lambda x: x["mem"], reverse=True)
        return procs[:limit]
    
    @staticmethod
    def kill_process(pid):
        if not HAS_PSUTIL:
            return False
        try:
            # Matar árbol completo
            from system.script_runner import _kill_process_tree
            killed, errors = _kill_process_tree(pid)
            return killed > 0
        except:
            try:
                psutil.Process(pid).kill()
                return True
            except:
                return False
    
    @staticmethod
    def get_system_stats():
        """Retorna CPU, RAM, Disco, Red y procesos"""
        stats = {
            "cpu": 0, 
            "ram_used": "0 B", "ram_total": "0 B", "ram_percent": 0,
            "disk_used": "0 B", "disk_total": "0 B", "disk_percent": 0,
            "processes": 0,
            # ═══ NUEVO: RED ═══
            "net_upload": "0 B/s",
            "net_download": "0 B/s",
            "net_upload_raw": 0,
            "net_download_raw": 0,
            "net_total_sent": "0 B",
            "net_total_recv": "0 B",
        }
        if not HAS_PSUTIL:
            return stats
        try:
            stats["cpu"] = round(psutil.cpu_percent(interval=0.3), 1)
            vm = psutil.virtual_memory()
            stats["ram_used"] = format_size(vm.used)
            stats["ram_total"] = format_size(vm.total)
            stats["ram_percent"] = vm.percent
            du = shutil.disk_usage(str(DRIVE_D))
            stats["disk_used"] = format_size(du.used)
            stats["disk_total"] = format_size(du.total)
            stats["disk_percent"] = round((du.used / du.total) * 100, 1)
            stats["processes"] = len(psutil.pids())
            
            # ═══ RED ═══
            net = network_monitor.get_stats()
            stats["net_upload"] = net["upload_speed_fmt"]
            stats["net_download"] = net["download_speed_fmt"]
            stats["net_upload_raw"] = net["upload_speed"]
            stats["net_download_raw"] = net["download_speed"]
            stats["net_total_sent"] = net["total_sent_fmt"]
            stats["net_total_recv"] = net["total_recv_fmt"]
        except Exception as e:
            pass
        return stats