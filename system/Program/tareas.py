#!/usr/bin/env python3
"""
📋 TASK MANAGER PRO v2.0
Gestor de tareas con categorías, prioridades y fechas
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

class TaskManager:
    def __init__(self):
        self.tasks_file = Path(__file__).parent / "tareas.json"
        self.tasks = self._load_tasks()
        self.categorias = ['Trabajo', 'Personal', 'Estudio', 'Hogar', 'Otro']
        self.prioridades = ['Alta', 'Media', 'Baja']
    
    def _load_tasks(self):
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def _save_tasks(self):
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)
    
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}📋 TASK MANAGER PRO v2.0{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")
        
        total = len(self.tasks)
        completadas = sum(1 for t in self.tasks if t.get('completada', False))
        pendientes = total - completadas
        
        # Barra de progreso
        if total > 0:
            pct = int((completadas / total) * 50)
            barra = f"{Colors.GREEN}{'█'*pct}{Colors.RED}{'█'*(50-pct)}{Colors.END}"
            print(f"📊 Progreso: {barra} {int((completadas/total)*100)}%")
        
        print(f"\n📊 Total: {total}  |  {Colors.GREEN}✅ Completadas: {completadas}{Colors.END}  |  {Colors.YELLOW}⏳ Pendientes: {pendientes}{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")
        
        # Mostrar tareas por prioridad
        if self.tasks:
            print(f"\n{Colors.BOLD}📋 TAREAS:{Colors.END}")
            for i, task in enumerate(self.tasks, 1):
                estado = f"{Colors.GREEN}✅{Colors.END}" if task.get('completada') else f"{Colors.YELLOW}⬜{Colors.END}"
                fecha = task.get('fecha', '')
                categoria = task.get('categoria', 'General')
                prioridad = task.get('prioridad', 'Media')
                
                prioridad_colors = {
                    'Alta': Colors.RED,
                    'Media': Colors.YELLOW,
                    'Baja': Colors.GREEN
                }
                prioridad_color = prioridad_colors.get(prioridad, Colors.END)
                
                # Resaltar tareas vencidas
                vencida = False
                if task.get('fecha_vencimiento') and not task.get('completada'):
                    try:
                        fecha_venc = datetime.strptime(task['fecha_vencimiento'], '%Y-%m-%d')
                        if fecha_venc < datetime.now():
                            vencida = True
                    except:
                        pass
                
                nombre = f"{Colors.RED}🔴 {task['titulo']}{Colors.END}" if vencida else task['titulo']
                print(f"{i:2}. {estado} {nombre}")
                print(f"     📁 {categoria}  |  {prioridad_color}● {prioridad}{Colors.END}  |  📅 {fecha}")
                if task.get('descripcion'):
                    print(f"     📝 {task['descripcion'][:50]}")
                if vencida:
                    print(f"     {Colors.RED}⚠️ VENCIDA{Colors.END}")
                print()
        
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")
        print("Comandos: [+] Agregar  [#N] Completar  [-N] Eliminar  [E] Editar  [F] Filtrar  [Q] Salir")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    
    def add_task(self):
        print(f"\n{Colors.BOLD}📝 NUEVA TAREA{Colors.END}")
        titulo = input("📌 Título: ").strip()
        if not titulo:
            return
        
        descripcion = input("📝 Descripción (opcional): ").strip()
        
        # Categoría
        print(f"\n📁 Categorías disponibles:")
        for i, cat in enumerate(self.categorias, 1):
            print(f"  {i}. {cat}")
        cat_sel = input("Selecciona categoría (1-5, Enter para 'Otro'): ").strip()
        try:
            categoria = self.categorias[int(cat_sel)-1] if cat_sel else 'Otro'
        except:
            categoria = 'Otro'
        
        # Prioridad
        print(f"\n🎯 Prioridades:")
        for i, pri in enumerate(self.prioridades, 1):
            print(f"  {i}. {pri}")
        pri_sel = input("Selecciona prioridad (1-3, Enter para 'Media'): ").strip()
        try:
            prioridad = self.prioridades[int(pri_sel)-1] if pri_sel else 'Media'
        except:
            prioridad = 'Media'
        
        # Fecha de vencimiento
        fecha_venc = input("📅 Fecha de vencimiento (YYYY-MM-DD, opcional): ").strip()
        
        task = {
            'titulo': titulo,
            'descripcion': descripcion,
            'categoria': categoria,
            'prioridad': prioridad,
            'completada': False,
            'fecha': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'creada': datetime.now().isoformat()
        }
        if fecha_venc:
            try:
                datetime.strptime(fecha_venc, '%Y-%m-%d')
                task['fecha_vencimiento'] = fecha_venc
            except:
                print("❌ Formato de fecha inválido")
        
        self.tasks.append(task)
        self._save_tasks()
        print(f"\n{Colors.GREEN}✅ Tarea añadida: {titulo}{Colors.END}")
        input("Presiona Enter...")
    
    def complete_task(self, num):
        if 1 <= num <= len(self.tasks):
            if not self.tasks[num-1].get('completada'):
                self.tasks[num-1]['completada'] = True
                self.tasks[num-1]['fecha_completada'] = datetime.now().isoformat()
                self._save_tasks()
                print(f"{Colors.GREEN}✅ Tarea completada: {self.tasks[num-1]['titulo']}{Colors.END}")
            else:
                # Opción de desmarcar
                if input("¿Desmarcar como completada? (s/n): ").lower() == 's':
                    self.tasks[num-1]['completada'] = False
                    self.tasks[num-1].pop('fecha_completada', None)
                    self._save_tasks()
                    print(f"{Colors.YELLOW}↩️ Tarea reactivada: {self.tasks[num-1]['titulo']}{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Número de tarea inválido{Colors.END}")
        input("Presiona Enter...")
    
    def delete_task(self, num):
        if 1 <= num <= len(self.tasks):
            task = self.tasks.pop(num-1)
            self._save_tasks()
            print(f"{Colors.RED}🗑️ Tarea eliminada: {task['titulo']}{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Número de tarea inválido{Colors.END}")
        input("Presiona Enter...")
    
    def edit_task(self, num):
        if 1 <= num <= len(self.tasks):
            task = self.tasks[num-1]
            print(f"\n{Colors.BOLD}✏️ EDITANDO TAREA:{Colors.END}")
            print(f"  Título actual: {task['titulo']}")
            print(f"  Descripción: {task.get('descripcion', '')}")
            print(f"  Categoría: {task.get('categoria', 'General')}")
            print(f"  Prioridad: {task.get('prioridad', 'Media')}")
            print()
            
            nuevo_titulo = input("Nuevo título (Enter para mantener): ").strip()
            if nuevo_titulo:
                task['titulo'] = nuevo_titulo
            
            nueva_desc = input("Nueva descripción (Enter para mantener): ").strip()
            if nueva_desc:
                task['descripcion'] = nueva_desc
            
            self._save_tasks()
            print(f"{Colors.GREEN}✅ Tarea actualizada{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Número de tarea inválido{Colors.END}")
        input("Presiona Enter...")
    
    def filter_tasks(self):
        print(f"\n{Colors.BOLD}🔍 FILTRAR TAREAS{Colors.END}")
        print("1. Ver todas")
        print("2. Solo pendientes")
        print("3. Solo completadas")
        print("4. Por categoría")
        print("5. Por prioridad")
        print("6. Vencidas")
        
        opcion = input("Selecciona filtro: ").strip()
        
        filtradas = self.tasks.copy()
        
        if opcion == '2':
            filtradas = [t for t in self.tasks if not t.get('completada')]
        elif opcion == '3':
            filtradas = [t for t in self.tasks if t.get('completada')]
        elif opcion == '4':
            print(f"\n📁 Categorías:")
            for i, cat in enumerate(self.categorias, 1):
                print(f"  {i}. {cat}")
            cat_sel = input("Selecciona categoría: ").strip()
            try:
                categoria = self.categorias[int(cat_sel)-1]
                filtradas = [t for t in self.tasks if t.get('categoria') == categoria]
            except:
                print("❌ Categoría inválida")
                return
        elif opcion == '5':
            print(f"\n🎯 Prioridades:")
            for i, pri in enumerate(self.prioridades, 1):
                print(f"  {i}. {pri}")
            pri_sel = input("Selecciona prioridad: ").strip()
            try:
                prioridad = self.prioridades[int(pri_sel)-1]
                filtradas = [t for t in self.tasks if t.get('prioridad') == prioridad]
            except:
                print("❌ Prioridad inválida")
                return
        elif opcion == '6':
            hoy = datetime.now()
            filtradas = []
            for t in self.tasks:
                if not t.get('completada') and t.get('fecha_vencimiento'):
                    try:
                        fecha_venc = datetime.strptime(t['fecha_vencimiento'], '%Y-%m-%d')
                        if fecha_venc < hoy:
                            filtradas.append(t)
                    except:
                        pass
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}🔍 FILTRO APLICADO - {len(filtradas)} tareas{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")
        
        for i, task in enumerate(filtradas, 1):
            estado = f"{Colors.GREEN}✅{Colors.END}" if task.get('completada') else f"{Colors.YELLOW}⬜{Colors.END}"
            print(f"{i}. {estado} {task['titulo']} [{task.get('categoria', 'General')}]")
        
        input("\nPresiona Enter para continuar...")
    
    def run(self):
        while True:
            self.display()
            cmd = input("\n👉 Comando: ").strip()
            
            if cmd.lower() == 'q':
                print(f"{Colors.GREEN}¡Hasta luego!{Colors.END}")
                break
            elif cmd == '+':
                self.add_task()
            elif cmd.startswith('#'):
                try:
                    num = int(cmd[1:].strip())
                    self.complete_task(num)
                except:
                    print(f"{Colors.RED}❌ Número inválido{Colors.END}")
            elif cmd.startswith('-'):
                try:
                    num = int(cmd[1:].strip())
                    self.delete_task(num)
                except:
                    print(f"{Colors.RED}❌ Número inválido{Colors.END}")
            elif cmd.lower().startswith('e'):
                try:
                    num = int(cmd[1:].strip()) if len(cmd) > 1 else int(input("Número de tarea: "))
                    self.edit_task(num)
                except:
                    print(f"{Colors.RED}❌ Número inválido{Colors.END}")
            elif cmd.lower() == 'f':
                self.filter_tasks()
            else:
                print(f"{Colors.RED}❌ Comando no reconocido{Colors.END}")
                input("Presiona Enter...")

if __name__ == "__main__":
    manager = TaskManager()
    manager.run()