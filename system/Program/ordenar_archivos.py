#!/usr/bin/env python3
"""Organizador de Archivos por extensión"""
import os
import shutil
from pathlib import Path

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    try:
        clear()
        print("📂 ORGANIZADOR DE ARCHIVOS")
        print("=" * 40)
        
        ruta = input("Ruta a organizar: ").strip()
        if not ruta:
            ruta = "."
        
        path = Path(ruta).resolve()
        if not path.exists():
            print("❌ Ruta no existe")
            return
        
        print(f"\n📁 Organizando: {path}")
        
        # Extensiones y carpetas destino
        categorias = {
            'Imágenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp'],
            'Documentos': ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf', '.odt'],
            'Hojas de cálculo': ['.xls', '.xlsx', '.csv', '.ods'],
            'Presentaciones': ['.ppt', '.pptx', '.odp'],
            'Archivos comprimidos': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'Ejecutables': ['.exe', '.msi', '.bat', '.cmd', '.sh'],
            'Código': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go'],
            'Vídeos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
            'Otros': []
        }
        
        # Crear carpetas
        for categoria in categorias:
            (path / categoria).mkdir(exist_ok=True)
        
        # Mover archivos
        movidos = 0
        for item in path.iterdir():
            if item.is_file():
                ext = item.suffix.lower()
                movido = False
                for categoria, extensiones in categorias.items():
                    if ext in extensiones:
                        destino = path / categoria / item.name
                        # Si ya existe, renombrar
                        if destino.exists():
                            base = item.stem
                            counter = 1
                            while destino.exists():
                                destino = path / categoria / f"{base}_{counter}{ext}"
                                counter += 1
                        shutil.move(str(item), str(destino))
                        movidos += 1
                        movido = True
                        break
                
                if not movido:
                    # Otros
                    destino = path / 'Otros' / item.name
                    if destino.exists():
                        base = item.stem
                        counter = 1
                        while destino.exists():
                            destino = path / 'Otros' / f"{base}_{counter}{ext}"
                            counter += 1
                    shutil.move(str(item), str(destino))
                    movidos += 1
        
        print(f"\n✅ {movidos} archivos organizados")
        
    except KeyboardInterrupt:
        print("\n¡Cancelado!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()