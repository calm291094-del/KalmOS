#!/usr/bin/env python3
"""
🛠️ HERRAMIENTAS PROFESIONALES v2.0
Sistema de herramientas estilo Hiren's Boot con interfaz mejorada
"""
import os
import sys
import platform
import subprocess
import hashlib
import shutil
import socket
import time
import json
from datetime import datetime
from pathlib import Path

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("⚠️ psutil no instalado. Instalar: pip install psutil")

class Colors:
    """Colores para terminal"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class SystemTools:
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_header(title):
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}{title:^60}{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    @staticmethod
    def print_success(msg):
        print(f"{Colors.GREEN}✅ {msg}{Colors.END}")
    
    @staticmethod
    def print_error(msg):
        print(f"{Colors.RED}❌ {msg}{Colors.END}")
    
    @staticmethod
    def print_info(msg):
        print(f"{Colors.BLUE}ℹ️ {msg}{Colors.END}")
    
    @staticmethod
    def print_warning(msg):
        print(f"{Colors.YELLOW}⚠️ {msg}{Colors.END}")
    
    @staticmethod
    def info_sistema():
        """Muestra información completa del sistema"""
        SystemTools.clear()
        SystemTools.print_header("🖥️ INFORMACIÓN DEL SISTEMA")
        
        print(f"{Colors.BOLD}Sistema Operativo:{Colors.END} {platform.system()} {platform.release()}")
        print(f"{Colors.BOLD}Arquitectura:{Colors.END} {platform.machine()}")
        print(f"{Colors.BOLD}Procesador:{Colors.END} {platform.processor()}")
        print(f"{Colors.BOLD}Hostname:{Colors.END} {socket.gethostname()}")
        print(f"{Colors.BOLD}Python:{Colors.END} {platform.python_version()}")
        
        if HAS_PSUTIL:
            print(f"\n{Colors.BOLD}{Colors.CYAN}📊 RECURSOS DEL SISTEMA{Colors.END}")
            print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
            
            cpu = psutil.cpu_percent(interval=0.5)
            cpu_freq = psutil.cpu_freq()
            print(f"CPU: {Colors.GREEN if cpu < 70 else Colors.YELLOW if cpu < 90 else Colors.RED}{cpu}%{Colors.END}")
            if cpu_freq:
                print(f"  Frecuencia: {cpu_freq.current:.0f} MHz")
            
            ram = psutil.virtual_memory()
            ram_used_gb = ram.used / (1024**3)
            ram_total_gb = ram.total / (1024**3)
            ram_percent = ram.percent
            print(f"RAM: {Colors.GREEN if ram_percent < 70 else Colors.YELLOW if ram_percent < 90 else Colors.RED}{ram_used_gb:.1f} GB / {ram_total_gb:.1f} GB ({ram_percent}%){Colors.END}")
            
            disk = psutil.disk_usage('/')
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)
            disk_percent = disk.percent
            print(f"Disco: {Colors.GREEN if disk_percent < 70 else Colors.YELLOW if disk_percent < 90 else Colors.RED}{disk_used_gb:.1f} GB / {disk_total_gb:.1f} GB ({disk_percent}%){Colors.END}")
            
            # Procesos
            procs = len(psutil.pids())
            print(f"Procesos: {procs}")
            
            # Tiempo de actividad
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            print(f"Tiempo activo: {days}d {hours}h {minutes}m")
        
        SystemTools.print_info("Presiona Enter para continuar...")
        input()
    
    @staticmethod
    def analisis_disco():
        """Analiza el uso de disco con detalles"""
        SystemTools.clear()
        SystemTools.print_header("💿 ANÁLISIS DE DISCO")
        
        if not HAS_PSUTIL:
            SystemTools.print_error("psutil no instalado")
            input()
            return
        
        # Discos disponibles
        print(f"{Colors.BOLD}📁 DISCOS DISPONIBLES:{Colors.END}")
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                used_gb = usage.used / (1024**3)
                total_gb = usage.total / (1024**3)
                percent = usage.percent
                color = Colors.GREEN if percent < 70 else Colors.YELLOW if percent < 90 else Colors.RED
                print(f"  {partition.device} {partition.mountpoint}: {color}{used_gb:.1f}/{total_gb:.1f} GB ({percent}%){Colors.END}")
            except:
                pass
        
        # Archivos grandes (solo en directorio actual)
        print(f"\n{Colors.BOLD}📂 ARCHIVOS GRANDES (>100MB):{Colors.END}")
        grandes = []
        for root, dirs, files in os.walk('.'):
            try:
                for file in files:
                    path = os.path.join(root, file)
                    if os.path.exists(path):
                        size = os.path.getsize(path)
                        if size > 100 * 1024 * 1024:
                            grandes.append((size, path))
                            if len(grandes) >= 15:
                                break
                if len(grandes) >= 15:
                    break
            except:
                pass
        
        if grandes:
            grandes.sort(reverse=True)
            for size, path in grandes[:10]:
                print(f"  {size/(1024**2):.1f} MB: {path}")
        else:
            SystemTools.print_info("No se encontraron archivos grandes")
        
        SystemTools.print_info("Presiona Enter para continuar...")
        input()
    
    @staticmethod
    def generar_hash():
        """Generador de hashes con múltiples algoritmos"""
        SystemTools.clear()
        SystemTools.print_header("🔐 GENERADOR DE HASH")
        
        archivo = input("📂 Ruta del archivo: ").strip()
        if not archivo or not os.path.exists(archivo):
            SystemTools.print_error("Archivo no encontrado")
            input()
            return
        
        print(f"\n{Colors.YELLOW}⏳ Calculando hashes...{Colors.END}")
        
        try:
            with open(archivo, 'rb') as f:
                data = f.read()
            
            algos = [
                ('MD5', hashlib.md5),
                ('SHA1', hashlib.sha1),
                ('SHA256', hashlib.sha256),
                ('SHA384', hashlib.sha384),
                ('SHA512', hashlib.sha512),
                ('BLAKE2b', hashlib.blake2b),
                ('BLAKE2s', hashlib.blake2s),
            ]
            
            print(f"\n{Colors.BOLD}📊 HASHES PARA: {os.path.basename(archivo)}{Colors.END}")
            print(f"{Colors.CYAN}{'-'*50}{Colors.END}")
            
            for name, algo in algos:
                hash_value = algo(data).hexdigest()
                print(f"{Colors.BOLD}{name}:{Colors.END} {hash_value}")
                print()
            
            # Guardar en archivo
            if input("\n💾 ¿Guardar hashes en archivo? (s/n): ").lower() == 's':
                output_file = f"hashes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(output_file, 'w') as f:
                    f.write(f"Archivo: {archivo}\n")
                    f.write(f"Fecha: {datetime.now()}\n")
                    f.write("="*50 + "\n")
                    for name, algo in algos:
                        f.write(f"{name}: {algo(data).hexdigest()}\n")
                SystemTools.print_success(f"Guardado en: {output_file}")
        
        except Exception as e:
            SystemTools.print_error(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    @staticmethod
    def escanear_puertos():
        """Escáner de puertos mejorado"""
        SystemTools.clear()
        SystemTools.print_header("🌐 ESCÁNER DE PUERTOS")
        
        host = input("🌐 IP o dominio: ").strip()
        if not host:
            SystemTools.print_error("Host no especificado")
            input()
            return
        
        print(f"\n{Colors.YELLOW}⏳ Escaneando {host}...{Colors.END}")
        
        puertos = {
            20: 'FTP-Datos', 21: 'FTP', 22: 'SSH', 23: 'Telnet',
            25: 'SMTP', 53: 'DNS', 80: 'HTTP', 110: 'POP3',
            143: 'IMAP', 443: 'HTTPS', 465: 'SMTPS', 587: 'SMTP',
            993: 'IMAPS', 995: 'POP3S', 3306: 'MySQL', 3389: 'RDP',
            5432: 'PostgreSQL', 8080: 'HTTP-Alt', 8443: 'HTTPS-Alt'
        }
        
        abiertos = []
        for puerto, nombre in puertos.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((host, puerto))
                sock.close()
                if result == 0:
                    abiertos.append((puerto, nombre))
                    SystemTools.print_success(f"Puerto {puerto} ({nombre}) - ABIERTO")
            except:
                pass
        
        if not abiertos:
            SystemTools.print_warning("No se encontraron puertos abiertos")
        
        SystemTools.print_info("Presiona Enter para continuar...")
        input()
    
    @staticmethod
    def monitor_procesos():
        """Monitor de procesos en tiempo real"""
        SystemTools.clear()
        SystemTools.print_header("📊 MONITOR DE PROCESOS")
        
        if not HAS_PSUTIL:
            SystemTools.print_error("psutil no instalado")
            input()
            return
        
        print(f"{Colors.BOLD}{'PID':>6} {'CPU%':>6} {'MEM%':>6} {'NOMBRE':<30}{Colors.END}")
        print(f"{Colors.CYAN}{'-'*50}{Colors.END}")
        
        procesos = sorted(
            psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
            key=lambda x: x.info['cpu_percent'] or 0,
            reverse=True
        )[:25]
        
        for p in procesos:
            try:
                pid = p.info['pid']
                cpu = p.info['cpu_percent'] or 0
                mem = p.info['memory_percent'] or 0
                name = p.info['name'] or '?'
                cpu_color = Colors.GREEN if cpu < 10 else Colors.YELLOW if cpu < 50 else Colors.RED
                print(f"{pid:>6} {cpu_color}{cpu:5.1f}%{Colors.END} {mem:5.1f}% {name:<30}")
            except:
                pass
        
        print(f"\n{Colors.CYAN}{'-'*50}{Colors.END}")
        print(f"Total procesos: {len(psutil.pids())}")
        
        SystemTools.print_info("Presiona Enter para continuar...")
        input()
    
    @staticmethod
    def limpiar_temporales():
        """Limpieza avanzada de archivos temporales"""
        SystemTools.clear()
        SystemTools.print_header("🧹 LIMPIEZA DE ARCHIVOS TEMPORALES")
        
        if platform.system() == "Windows":
            temp_dirs = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp'),
                os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Temp')
            ]
        else:
            temp_dirs = ['/tmp', '/var/tmp', '/var/cache']
        
        total_size = 0
        file_count = 0
        
        for temp_dir in temp_dirs:
            if temp_dir and os.path.exists(temp_dir):
                print(f"\n📁 {temp_dir}")
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        try:
                            path = os.path.join(root, file)
                            size = os.path.getsize(path)
                            if size > 0:
                                total_size += size
                                file_count += 1
                        except:
                            pass
        
        print(f"\n📊 Archivos temporales encontrados: {file_count}")
        print(f"📊 Tamaño total: {total_size / (1024**2):.1f} MB")
        
        if file_count > 0 and input("\n⚠️ ¿Eliminar archivos temporales? (s/n): ").lower() == 's':
            deleted = 0
            for temp_dir in temp_dirs:
                if temp_dir and os.path.exists(temp_dir):
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            try:
                                os.remove(os.path.join(root, file))
                                deleted += 1
                            except:
                                pass
            SystemTools.print_success(f"Eliminados {deleted} archivos temporales")
        
        input("\nPresiona Enter para continuar...")
    
    @staticmethod
    def menu():
        """Menú principal mejorado"""
        while True:
            SystemTools.clear()
            print(f"{Colors.HEADER}{'='*60}{Colors.END}")
            print(f"{Colors.BOLD}{Colors.HEADER}🛠️  HERRAMIENTAS PROFESIONALES v2.0{Colors.END}")
            print(f"{Colors.HEADER}{'='*60}{Colors.END}")
            print(f"{Colors.CYAN}   🔧 Sistema de herramientas estilo Hiren's Boot{Colors.END}")
            print(f"{Colors.HEADER}{'='*60}{Colors.END}")
            print(f"""
{Colors.GREEN}1.{Colors.END} 🖥️  Información del Sistema
{Colors.GREEN}2.{Colors.END} 💿 Análisis de Disco
{Colors.GREEN}3.{Colors.END} 🔐 Generador de Hash
{Colors.GREEN}4.{Colors.END} 🌐 Escáner de Puertos
{Colors.GREEN}5.{Colors.END} 📊 Monitor de Procesos
{Colors.GREEN}6.{Colors.END} 🧹 Limpieza de Temporales
{Colors.GREEN}7.{Colors.END} 🔄 Diagnóstico de Red
{Colors.GREEN}0.{Colors.END} 🚪 Salir
""")
            print(f"{Colors.HEADER}{'='*60}{Colors.END}")
            
            opcion = input("👉 Selecciona una opción: ").strip()
            
            if opcion == '0':
                SystemTools.print_success("¡Hasta luego!")
                break
            elif opcion == '1':
                SystemTools.info_sistema()
            elif opcion == '2':
                SystemTools.analisis_disco()
            elif opcion == '3':
                SystemTools.generar_hash()
            elif opcion == '4':
                SystemTools.escanear_puertos()
            elif opcion == '5':
                SystemTools.monitor_procesos()
            elif opcion == '6':
                SystemTools.limpiar_temporales()
            elif opcion == '7':
                SystemTools.diagnostico_red()
            else:
                SystemTools.print_error("Opción inválida")
                input("Presiona Enter...")
    
    @staticmethod
    def diagnostico_red():
        """Diagnóstico de red completo"""
        SystemTools.clear()
        SystemTools.print_header("🔄 DIAGNÓSTICO DE RED")
        
        # IP local
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"{Colors.BOLD}Hostname:{Colors.END} {hostname}")
            print(f"{Colors.BOLD}IP Local:{Colors.END} {local_ip}")
        except:
            SystemTools.print_error("Error obteniendo información de red")
        
        # DNS
        try:
            print(f"\n{Colors.BOLD}🌐 DNS:{Colors.END}")
            for domain in ['google.com', 'github.com', 'kalmos.onrender.com']:
                try:
                    ip = socket.gethostbyname(domain)
                    print(f"  {domain}: {Colors.GREEN}{ip}{Colors.END}")
                except:
                    print(f"  {domain}: {Colors.RED}FALLÓ{Colors.END}")
        except:
            pass
        
        # Puertos locales
        print(f"\n{Colors.BOLD}🔌 Puertos locales:{Colors.END}")
        for port in [80, 443, 8080, 3306, 5432, 27017]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.3)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                if result == 0:
                    print(f"  Puerto {port}: {Colors.GREEN}OCUPADO{Colors.END}")
                else:
                    print(f"  Puerto {port}: {Colors.YELLOW}LIBRE{Colors.END}")
            except:
                pass
        
        SystemTools.print_info("Presiona Enter para continuar...")
        input()

if __name__ == "__main__":
    SystemTools.menu()