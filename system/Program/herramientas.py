#!/usr/bin/env python3
"""Herramientas profesionales estilo Hiren's Boot"""
import os
import sys
import platform
import subprocess
import hashlib
import shutil
import socket
import psutil

class SystemTools:
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def info_sistema():
        """Muestra información del sistema"""
        SystemTools.clear()
        print("🖥️ INFORMACIÓN DEL SISTEMA")
        print("=" * 50)
        print(f"SO: {platform.system()} {platform.release()}")
        print(f"Arquitectura: {platform.machine()}")
        print(f"Procesador: {platform.processor()}")
        print(f"Hostname: {socket.gethostname()}")
        
        if psutil:
            print("\n📊 RECURSOS")
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            print(f"CPU: {cpu}%")
            print(f"RAM: {ram.used / (1024**3):.1f} GB / {ram.total / (1024**3):.1f} GB")
            print(f"Disco: {disk.used / (1024**3):.1f} GB / {disk.total / (1024**3):.1f} GB")
        
        print("=" * 50)
        input("Presiona Enter...")
    
    @staticmethod
    def analisis_disco():
        """Analiza el uso de disco"""
        SystemTools.clear()
        print("💿 ANÁLISIS DE DISCO")
        print("=" * 50)
        
        if psutil:
            disk = psutil.disk_usage('/')
            print(f"Total: {disk.total / (1024**3):.1f} GB")
            print(f"Usado: {disk.used / (1024**3):.1f} GB")
            print(f"Libre: {disk.free / (1024**3):.1f} GB")
            print(f"Uso: {disk.percent}%")
            
            # Archivos grandes
            print("\n📂 Archivos grandes (>100MB):")
            grandes = 0
            for root, dirs, files in os.walk('/'):
                try:
                    for file in files:
                        path = os.path.join(root, file)
                        if os.path.exists(path):
                            size = os.path.getsize(path)
                            if size > 100 * 1024 * 1024:
                                print(f"  {size / (1024**2):.1f} MB: {path}")
                                grandes += 1
                                if grandes >= 10:
                                    break
                except:
                    pass
                if grandes >= 10:
                    break
        
        print("=" * 50)
        input("Presiona Enter...")
    
    @staticmethod
    def generar_hash():
        """Genera hash de un archivo"""
        SystemTools.clear()
        print("🔐 GENERADOR DE HASH")
        print("=" * 50)
        
        archivo = input("Ruta del archivo: ").strip()
        if not os.path.exists(archivo):
            print("❌ Archivo no encontrado")
            input("Presiona Enter...")
            return
        
        print("\nCalculando hashes...")
        
        with open(archivo, 'rb') as f:
            data = f.read()
        
        print(f"MD5:    {hashlib.md5(data).hexdigest()}")
        print(f"SHA1:   {hashlib.sha1(data).hexdigest()}")
        print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
        print(f"SHA512: {hashlib.sha512(data).hexdigest()}")
        
        input("\nPresiona Enter...")
    
    @staticmethod
    def escanear_puertos():
        """Escanea puertos abiertos"""
        SystemTools.clear()
        print("🌐 ESCÁNER DE PUERTOS")
        print("=" * 50)
        
        host = input("IP o dominio: ").strip()
        if not host:
            print("❌ Host no especificado")
            input("Presiona Enter...")
            return
        
        print(f"\nEscaneando {host}...")
        
        puertos_comunes = [20, 21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389, 5432, 8080, 8443]
        abiertos = []
        
        for puerto in puertos_comunes:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((host, puerto))
                sock.close()
                if result == 0:
                    abiertos.append(puerto)
            except:
                pass
        
        if abiertos:
            print(f"\n✅ Puertos abiertos: {', '.join(map(str, abiertos))}")
        else:
            print("\nℹ️ No se encontraron puertos abiertos comunes")
        
        input("\nPresiona Enter...")
    
    @staticmethod
    def menu():
        """Menú principal de herramientas"""
        while True:
            SystemTools.clear()
            print("🛠️ HERRAMIENTAS PROFESIONALES")
            print("=" * 50)
            print("1. Información del Sistema")
            print("2. Análisis de Disco")
            print("3. Generador de Hash")
            print("4. Escáner de Puertos")
            print("5. Limpieza de Archivos Temporales")
            print("6. Monitor de Procesos")
            print("0. Salir")
            print("=" * 50)
            
            opcion = input("Opción: ").strip()
            
            if opcion == '0':
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
                SystemTools.limpiar_temporales()
            elif opcion == '6':
                SystemTools.monitor_procesos()
            else:
                print("❌ Opción inválida")
                input("Presiona Enter...")
    
    @staticmethod
    def limpiar_temporales():
        """Limpia archivos temporales"""
        SystemTools.clear()
        print("🧹 LIMPIEZA DE ARCHIVOS TEMPORALES")
        print("=" * 50)
        
        if platform.system() == "Windows":
            temp_dirs = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp')
            ]
        else:
            temp_dirs = ['/tmp', '/var/tmp']
        
        total = 0
        for temp_dir in temp_dirs:
            if temp_dir and os.path.exists(temp_dir):
                print(f"\n📁 {temp_dir}")
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        try:
                            path = os.path.join(root, file)
                            size = os.path.getsize(path)
                            if size > 0:
                                total += size
                        except:
                            pass
        
        print(f"\nTotal archivos temporales: {total / (1024**2):.1f} MB")
        
        if input("\n¿Eliminar? (s/n): ").lower() == 's':
            for temp_dir in temp_dirs:
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    os.makedirs(temp_dir, exist_ok=True)
            print("✅ Limpieza completada")
        
        input("Presiona Enter...")
    
    @staticmethod
    def monitor_procesos():
        """Monitor de procesos"""
        SystemTools.clear()
        print("📊 MONITOR DE PROCESOS")
        print("=" * 50)
        
        if psutil:
            procesos = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']), 
                            key=lambda x: x.info['cpu_percent'] or 0, reverse=True)[:20]
            
            print("PID     CPU%    MEM%    Nombre")
            print("-" * 50)
            for p in procesos:
                try:
                    print(f"{p.info['pid']:6}  {p.info['cpu_percent'] or 0:5.1f}   {p.info['memory_percent'] or 0:5.1f}   {p.info['name']}")
                except:
                    pass
        
        input("\nPresiona Enter...")

if __name__ == "__main__":
    try:
        import psutil
    except ImportError:
        print("⚠️ psutil no instalado. Instalar con: pip install psutil")
    
    SystemTools.menu()