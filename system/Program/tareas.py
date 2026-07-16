#!/usr/bin/env python3
"""Gestor de Tareas (To-Do List)"""
import os
import json
from datetime import datetime

class TaskManager:
    def __init__(self):
        self.tasks_file = "tareas.json"
        self.tasks = self._load_tasks()
    
    def _load_tasks(self):
        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_tasks(self):
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)
    
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("📋 GESTOR DE TAREAS")
        print("=" * 50)
        
        if not self.tasks:
            print("\n📝 No hay tareas")
        else:
            print(f"\n📊 Total: {len(self.tasks)} tareas")
            print(f"✅ Completadas: {sum(1 for t in self.tasks if t['completada'])}")
            print(f"⏳ Pendientes: {sum(1 for t in self.tasks if not t['completada'])}")
            print("=" * 50)
            
            for i, task in enumerate(self.tasks, 1):
                estado = "✅" if task['completada'] else "⬜"
                fecha = task.get('fecha', '')
                print(f"{i}. {estado} {task['titulo']} {fecha}")
        
        print("=" * 50)
        print("\nComandos:")
        print("  +  Agregar tarea")
        print("  #  Completar tarea (ej: 3)")
        print("  -  Eliminar tarea (ej: -3)")
        print("  L  Listar tareas")
        print("  Q  Salir")
    
    def add_task(self):
        titulo = input("📝 Descripción de la tarea: ").strip()
        if not titulo:
            return
        
        self.tasks.append({
            'titulo': titulo,
            'completada': False,
            'fecha': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'creada': datetime.now().isoformat()
        })
        self._save_tasks()
        print(f"✅ Tarea añadida: {titulo}")
    
    def complete_task(self, num):
        if 1 <= num <= len(self.tasks):
            self.tasks[num-1]['completada'] = True
            self._save_tasks()
            print(f"✅ Tarea completada: {self.tasks[num-1]['titulo']}")
        else:
            print("❌ Número de tarea inválido")
    
    def delete_task(self, num):
        if 1 <= num <= len(self.tasks):
            task = self.tasks.pop(num-1)
            self._save_tasks()
            print(f"🗑️ Tarea eliminada: {task['titulo']}")
        else:
            print("❌ Número de tarea inválido")
    
    def list_tasks(self):
        print("\n📋 LISTA DE TAREAS")
        print("-" * 40)
        
        if not self.tasks:
            print("No hay tareas")
        else:
            for i, task in enumerate(self.tasks, 1):
                estado = "✅" if task['completada'] else "⬜"
                fecha = task.get('fecha', '')
                print(f"{i}. {estado} {task['titulo']} [{fecha}]")
        
        input("\nPresiona Enter para continuar...")
    
    def run(self):
        while True:
            self.display()
            
            cmd = input("\nComando: ").strip()
            
            if cmd.lower() == 'q':
                print("¡Hasta luego!")
                break
            elif cmd == '+':
                self.add_task()
            elif cmd.startswith('#'):
                try:
                    num = int(cmd[1:].strip())
                    self.complete_task(num)
                except:
                    print("❌ Ingresa un número válido")
            elif cmd.startswith('-'):
                try:
                    num = int(cmd[1:].strip())
                    self.delete_task(num)
                except:
                    print("❌ Ingresa un número válido")
            elif cmd.lower() == 'l':
                self.list_tasks()
            else:
                print("❌ Comando no reconocido")
            
            input("Presiona Enter para continuar...")

if __name__ == "__main__":
    manager = TaskManager()
    manager.run()