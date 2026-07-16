#!/usr/bin/env python3
"""Editor de Texto Simple en consola"""
import os
import sys
import time

class TextEditor:
    def __init__(self):
        self.filename = ""
        self.content = []
        self.cursor = 0
    
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"📝 EDITOR DE TEXTO - {self.filename or 'Nuevo archivo'}")
        print("=" * 50)
        print("Comandos: [N]uevo [C]argar [G]uardar [Q]uit")
        print("=" * 50)
        
        # Mostrar contenido
        for i, line in enumerate(self.content):
            print(f"{i+1:3}│ {line}")
        
        if not self.content:
            print("    │ (archivo vacío)")
        
        print("=" * 50)
    
    def new_file(self):
        self.filename = ""
        self.content = []
        self.cursor = 0
        print("✅ Nuevo archivo creado")
        time.sleep(0.5)
    
    def load_file(self):
        filename = input("📂 Nombre del archivo a cargar: ").strip()
        if not filename:
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.content = f.read().splitlines()
            self.filename = filename
            print(f"✅ Archivo '{filename}' cargado ({len(self.content)} líneas)")
        except FileNotFoundError:
            print(f"❌ Archivo '{filename}' no encontrado")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(0.5)
    
    def save_file(self):
        if not self.filename:
            self.filename = input("📝 Nombre del archivo: ").strip()
            if not self.filename:
                return
        
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.content))
            print(f"✅ Archivo guardado: {self.filename}")
        except Exception as e:
            print(f"❌ Error guardando: {e}")
        
        time.sleep(0.5)
    
    def edit_content(self):
        print("\n📝 Editando contenido (escribe '///' para terminar):")
        print("-" * 40)
        
        if self.content:
            print("Líneas actuales:")
            for i, line in enumerate(self.content):
                print(f"  {i+1}: {line}")
            print("-" * 40)
        
        new_lines = []
        while True:
            line = input()
            if line.strip() == '///':
                break
            new_lines.append(line)
        
        if new_lines:
            self.content.extend(new_lines)
            print(f"✅ {len(new_lines)} líneas añadidas")
        else:
            print("ℹ️ No se añadieron líneas")
        
        time.sleep(0.5)
    
    def run(self):
        while True:
            self.display()
            
            if self.content:
                print(f"📊 {len(self.content)} líneas | Cursor: {self.cursor+1}")
            
            cmd = input("\nComando: ").strip().lower()
            
            if cmd == 'n':
                self.new_file()
            elif cmd == 'c':
                self.load_file()
            elif cmd == 'g':
                self.save_file()
            elif cmd == 'e':
                self.edit_content()
            elif cmd == 'q':
                if self.content and input("¿Guardar cambios? (s/n): ").lower() == 's':
                    self.save_file()
                print("¡Hasta luego!")
                break
            elif cmd == '?':
                print("\nComandos:")
                print("  N - Nuevo archivo")
                print("  C - Cargar archivo")
                print("  G - Guardar archivo")
                print("  E - Editar contenido")
                print("  Q - Salir")
                input("Presiona Enter...")
            else:
                print("❌ Comando no reconocido. Usa N, C, G, E o Q")
                time.sleep(0.5)

if __name__ == "__main__":
    editor = TextEditor()
    editor.run()