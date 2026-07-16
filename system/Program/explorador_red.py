#!/usr/bin/env python3
"""Explorador de Red - Ping y escaneo de puertos"""
import os
import subprocess
import socket
import threading
import time

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def ping(host):
    try:
        param = '-n' if os.name == 'nt' else '-c'
        result = subprocess.run(['ping', param, '1', host], capture_output=True, text=True, timeout=3)
        return result.returncode == 0
    except:
        return False

def scan_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def main():
    try:
        clear()
        print("🌐 EXPLORADOR DE RED")
        print("=" * 40)
        
        host = input("Dirección IP o dominio: ").strip()
        if not host:
            print("❌ Host no especificado")
            return
        
        print(f"\n⏳ Analizando {host}...")
        
        # Ping
        alive = ping(host)
        print(f"\n📡 Ping: {'✅ Activo' if alive else '❌ Inactivo'}")
        
        if alive:
            # Puertos comunes
            puertos = [20, 21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389, 5432, 8080, 8443]
            print(f"\n🔍 Escaneando puertos comunes...")
            
            abiertos = []
            for port in puertos:
                if scan_port(host, port):
                    servicios = {
                        20: 'FTP-Datos', 21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
                        53: 'DNS', 80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS',
                        465: 'SMTPS', 587: 'SMTP', 993: 'IMAPS', 995: 'POP3S',
                        3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL', 8080: 'HTTP-Alt', 8443: 'HTTPS-Alt'
                    }
                    abiertos.append(f"{port} ({servicios.get(port, 'Desconocido')})")
            
            if abiertos:
                print(f"\n✅ Puertos abiertos:")
                for p in abiertos:
                    print(f"   🔓 {p}")
            else:
                print("\nℹ️ No se encontraron puertos abiertos comunes")
        
        print("\n" + "=" * 40)
        
    except KeyboardInterrupt:
        print("\n¡Cancelado!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()