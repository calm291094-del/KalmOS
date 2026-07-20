#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KROOT CORP - VERSIÓN GUI (Tkinter)
Interfaz gráfica nativa para Kalm OS
"""

import sys
import os
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from datetime import datetime

# ============================================================
# 1. INSTALAR DEPENDENCIAS
# ============================================================
def instalar_dependencias():
    try:
        import requests
    except ImportError:
        print("📦 Instalando requests...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])

instalar_dependencias()

# ============================================================
# 2. IMPORTAR MÓDULOS
# ============================================================
try:
    import requests
except ImportError:
    print("❌ Error: requests no instalado")
    sys.exit(1)

# ============================================================
# 3. CLIENTE POLLINATIONS AI
# ============================================================
class PollinationsClient:
    BASE_URL = "https://text.pollinations.ai/openai"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def chat_completion(self, model, messages):
        payload = {"model": model, "messages": messages, "stream": False}
        response = self.session.post(self.BASE_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

# ============================================================
# 4. APLICACIÓN GUI
# ============================================================
class KrootCorpApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏢 Kroot Corp IA - Kalm OS")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a2e')
        
        self.client = PollinationsClient()
        self.modelo_actual = tk.StringVar(value="openai")
        self.historial = []
        self.ultimo_informe = None
        
        self.crear_widgets()
        self.mostrar_bienvenida()
    
    def crear_widgets(self):
        # Frame superior
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        titulo = tk.Label(top_frame, text="🏢 Kroot Corp IA", 
                         font=("Segoe UI", 20, "bold"), 
                         bg='#1a1a2e', fg='#da70d6')
        titulo.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(top_frame, text="🟢 Listo", 
                                     font=("Segoe UI", 10), 
                                     bg='#1a1a2e', fg='#00cc66')
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # Frame de controles
        controls = ttk.Frame(self.root, padding="10")
        controls.pack(fill=tk.X)
        
        ttk.Label(controls, text="Modelo:").pack(side=tk.LEFT, padx=(0,5))
        modelos = ["openai", "claude", "gemini", "deepseek", "llama", "mistral"]
        modelo_combo = ttk.Combobox(controls, textvariable=self.modelo_actual, 
                                    values=modelos, state="readonly", width=12)
        modelo_combo.pack(side=tk.LEFT, padx=(0,10))
        
        ttk.Label(controls, text="Tema:").pack(side=tk.LEFT, padx=(0,5))
        self.tema_entry = ttk.Entry(controls, width=50)
        self.tema_entry.pack(side=tk.LEFT, padx=(0,10))
        self.tema_entry.bind("<Return>", lambda e: self.generar_informe())
        
        ttk.Button(controls, text="📝 Generar", command=self.generar_informe).pack(side=tk.LEFT)
        
        # Área de texto
        text_frame = ttk.Frame(self.root, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_area = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD, 
            font=("Segoe UI", 11),
            bg='#0a0a1a',
            fg='#e0e0e0',
            insertbackground='#da70d6',
            relief=tk.FLAT,
            borderwidth=0
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Tags
        self.text_area.tag_configure("titulo", foreground="#da70d6", font=("Segoe UI", 14, "bold"))
        self.text_area.tag_configure("subtitulo", foreground="#9370db", font=("Segoe UI", 12, "bold"))
        self.text_area.tag_configure("normal", foreground="#e0e0e0", font=("Segoe UI", 11))
        self.text_area.tag_configure("error", foreground="#ff4444", font=("Segoe UI", 11, "bold"))
        self.text_area.tag_configure("exito", foreground="#00cc66", font=("Segoe UI", 11, "bold"))
        
        # Frame inferior
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X)
        
        ttk.Button(bottom_frame, text="💾 Guardar TXT", command=self.guardar_txt).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="📋 Copiar", command=self.copiar_texto).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="📋 Historial", command=self.mostrar_historial).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="🗑️ Limpiar", command=self.limpiar).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="❓ Ayuda", command=self.mostrar_ayuda).pack(side=tk.RIGHT, padx=5)
    
    def mostrar_bienvenida(self):
        self.text_area.insert(tk.END, "🏢 KROOT CORP IA\n", "titulo")
        self.text_area.insert(tk.END, "=" * 40 + "\n\n", "normal")
        self.text_area.insert(tk.END, "✅ Sin API Key (Pollinations AI)\n", "exito")
        self.text_area.insert(tk.END, "✅ Elige modelo y tema\n", "exito")
        self.text_area.insert(tk.END, "✅ Genera informes ejecutivos\n\n", "exito")
        self.text_area.insert(tk.END, "📝 Escribe un tema y pulsa 'Generar'\n", "normal")
    
    def set_status(self, texto, color="#00cc66"):
        self.status_label.config(text=texto, fg=color)
        self.root.update()
    
    def generar_informe(self):
        tema = self.tema_entry.get().strip()
        if not tema:
            messagebox.showwarning("Tema vacío", "Por favor, escribe un tema.")
            return
        
        modelo = self.modelo_actual.get()
        self.set_status("⏳ Generando...", "#ffaa00")
        self.text_area.insert(tk.END, f"\n📝 Generando informe: {tema}\n", "subtitulo")
        self.text_area.see(tk.END)
        
        def tarea():
            try:
                # Investigación
                prompt_inv = f"Investiga a fondo sobre '{tema}'. Da 5 puntos clave y datos relevantes."
                inv = self.client.chat_completion(modelo, [{"role": "user", "content": prompt_inv}])
                
                # Informe
                prompt_inf = f"Basado en: {inv}\n\nRedacta un informe ejecutivo profesional con: Introducción, Puntos Clave, Conclusiones y Recomendaciones."
                informe = self.client.chat_completion(modelo, [{"role": "user", "content": prompt_inf}])
                
                # QA
                prompt_qa = f"Revisa este informe y da feedback: {informe}"
                qa = self.client.chat_completion(modelo, [{"role": "user", "content": prompt_qa}])
                
                resultado = f"""📊 INFORME EJECUTIVO: {tema.upper()}
{'=' * 50}

{informe}

{'=' * 50}
📝 VEREDICTO DE CALIDAD:
{qa}
{'=' * 50}"""
                
                self.root.after(0, lambda: self.mostrar_resultado(resultado, tema))
                
            except Exception as e:
                self.root.after(0, lambda: self.mostrar_error(str(e)))
        
        threading.Thread(target=tarea, daemon=True).start()
    
    def mostrar_resultado(self, resultado, tema):
        self.text_area.insert(tk.END, "\n" + "=" * 50 + "\n", "normal")
        self.text_area.insert(tk.END, f"📊 INFORME: {tema}\n", "titulo")
        self.text_area.insert(tk.END, "=" * 50 + "\n\n", "normal")
        self.text_area.insert(tk.END, resultado, "normal")
        self.text_area.insert(tk.END, "\n\n" + "=" * 50 + "\n", "normal")
        self.text_area.see(tk.END)
        
        self.ultimo_informe = resultado
        self.historial.append({"tema": tema, "resultado": resultado, "fecha": datetime.now()})
        self.set_status("✅ Listo", "#00cc66")
        self.tema_entry.delete(0, tk.END)
    
    def mostrar_error(self, error):
        self.text_area.insert(tk.END, f"\n❌ Error: {error}\n", "error")
        self.text_area.see(tk.END)
        self.set_status("❌ Error", "#ff4444")
    
    def guardar_txt(self):
        contenido = self.text_area.get(1.0, tk.END).strip()
        if not contenido or "Bienvenido" in contenido:
            messagebox.showinfo("Sin contenido", "No hay nada para guardar.")
            return
        
        archivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Guardar informe"
        )
        if archivo:
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)
            messagebox.showinfo("Éxito", f"✅ Guardado en: {archivo}")
    
    def copiar_texto(self):
        contenido = self.text_area.get(1.0, tk.END).strip()
        if contenido:
            self.root.clipboard_clear()
            self.root.clipboard_append(contenido)
            self.set_status("📋 Copiado al portapapeles", "#9370db")
    
    def mostrar_historial(self):
        if not self.historial:
            messagebox.showinfo("Historial", "No hay informes en el historial.")
            return
        
        historial_texto = "📋 HISTORIAL DE INFORMES\n"
        historial_texto += "=" * 40 + "\n\n"
        for i, item in enumerate(self.historial, 1):
            fecha = item["fecha"].strftime("%d/%m/%Y %H:%M")
            historial_texto += f"{i}. {item['tema']} ({fecha})\n"
        
        messagebox.showinfo("Historial", historial_texto)
    
    def limpiar(self):
        self.text_area.delete(1.0, tk.END)
        self.mostrar_bienvenida()
        self.ultimo_informe = None
        self.set_status("🗑️ Limpiado", "#9370db")
    
    def mostrar_ayuda(self):
        messagebox.showinfo(
            "Ayuda",
            "🏢 KROOT CORP IA\n\n"
            "📝 Generar informe:\n"
            "  - Escribe un tema y pulsa 'Generar'\n"
            "  - Espera 30-60 segundos\n"
            "  - El informe aparecerá en el área de texto\n\n"
            "💾 Guardar:\n"
            "  - Haz clic en 'Guardar TXT'\n"
            "  - Elige la ubicación y el nombre\n\n"
            "📋 Copiar:\n"
            "  - Copia todo el contenido al portapapeles\n\n"
            "📋 Historial:\n"
            "  - Muestra todos los informes generados\n\n"
            "🔄 Modelos:\n"
            "  - openai, claude, gemini, deepseek, llama, mistral\n"
            "  - Todos son gratuitos (Pollinations AI)"
        )

# ============================================================
# 5. PUNTO DE ENTRADA
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = KrootCorpApp(root)
    root.mainloop()