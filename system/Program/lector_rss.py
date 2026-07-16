#!/usr/bin/env python3
"""Lector RSS simple"""
import os
import urllib.request
import xml.etree.ElementTree as ET

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    try:
        print("📡 LECTOR RSS")
        print("=" * 30)
        url = input("URL del feed RSS: ").strip()
        
        if not url:
            print("❌ URL vacía")
            return
        
        print("\n⏳ Cargando...")
        
        try:
            response = urllib.request.urlopen(url, timeout=10)
            data = response.read().decode('utf-8', errors='ignore')
            root = ET.fromstring(data)
            
            # Buscar items
            items = root.findall('.//item') or root.findall('.//entry')
            
            if not items:
                print("❌ No se encontraron items en el feed")
                return
            
            clear()
            print("📡 LECTOR RSS")
            print("=" * 50)
            
            for i, item in enumerate(items[:10], 1):
                title = item.find('title')
                title_text = title.text if title is not None else "Sin título"
                
                link = item.find('link')
                link_text = link.text if link is not None else ""
                
                print(f"{i}. {title_text[:60]}")
                if link_text:
                    print(f"   🔗 {link_text[:60]}")
                print()
            
            print("=" * 50)
            print(f"Mostrados {min(10, len(items))} de {len(items)} items")
            
        except Exception as e:
            print(f"❌ Error cargando feed: {e}")
        
        input("\nPresiona Enter para salir...")
        
    except KeyboardInterrupt:
        print("\n¡Cancelado!")

if __name__ == "__main__":
    main()