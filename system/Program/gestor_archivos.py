#!/usr/bin/env python3
"""Gestor de Archivos CLI"""
import os
import shutil
from pathlib import Path

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def listar_directorio(path="."):
    try:
        items = sorted(Path(path).iterdir(), key=lambda x: (not x.is_dir(), x.name))
        print("📂 CONTENIDO:")
        print("-" * 40)
        for item in items:
            if item.is_dir():
                print(f"📁 {item.name}/")
            else:
                size = item.stat().st_size
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024*1024:
                    size_str = f"{size/1024:.1f} KB"
                else:
                    size_str = f"{size/(1024*1024):.1f} MB"
                print(f"📄 {item.name} ({size_str})")
        print("-" * 40)
        print(f"Total: {len(items)} elementos")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    current = "."
    
    while True:
        clear()
        print(f"📂 GESTOR DE ARCHIVOS - {os.getcwd()}")
        print("=" * 50)
        listar_directorio(current)
        print("\nComandos:")
        print("  cd <dir>  - Cambiar directorio")
        print("  mkdir <nombre> - Crear carpeta")
        print("  rm <nombre> - Eliminar archivo/carpeta")
        print("  mv <origen> <destino> - Mover/renombrar")
        print("  cp <origen> <destino> - Copiar")
        print("  pwd - Mostrar ruta actual")
        print("  q - Salir")
        
        cmd = input("\n> ").strip().split()
        if not cmd:
            continue
        
        if cmd[0] == 'q':
            break
        elif cmd[0] == 'pwd':
            print(os.getcwd())
            input("Presiona Enter...")
        elif cmd[0] == 'cd' and len(cmd) > 1:
            try:
                os.chdir(cmd[1])
                current = "."
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Presiona Enter...")
        elif cmd[0] == 'mkdir' and len(cmd) > 1:
            try:
                Path(cmd[1]).mkdir(exist_ok=False)
                print(f"✅ Carpeta creada: {cmd[1]}")
            except FileExistsError:
                print(f"❌ La carpeta ya existe")
            except Exception as e:
                print(f"❌ Error: {e}")
            input("Presiona Enter...")
        elif cmd[0] == 'rm' and len(cmd) > 1:
            try:
                p = Path(cmd[1])
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
                print(f"✅ Eliminado: {cmd[1]}")
            except Exception as e:
                print(f"❌ Error: {e}")
            input("Presiona Enter...")
        elif cmd[0] == 'mv' and len(cmd) > 2:
            try:
                shutil.move(cmd[1], cmd[2])
                print(f"✅ Movido: {cmd[1]} -> {cmd[2]}")
            except Exception as e:
                print(f"❌ Error: {e}")
            input("Presiona Enter...")
        elif cmd[0] == 'cp' and len(cmd) > 2:
            try:
                if Path(cmd[1]).is_dir():
                    shutil.copytree(cmd[1], cmd[2], dirs_exist_ok=True)
                else:
                    shutil.copy2(cmd[1], cmd[2])
                print(f"✅ Copiado: {cmd[1]} -> {cmd[2]}")
            except Exception as e:
                print(f"❌ Error: {e}")
            input("Presiona Enter...")
        else:
            print("❌ Comando no reconocido")
            input("Presiona Enter...")
    
    print("¡Hasta luego!")

if __name__ == "__main__":
    main()