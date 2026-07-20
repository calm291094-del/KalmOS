#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CHAT ACADÉMICO - APLICACIÓN NATIVA PARA KALM OS
Versión que funciona sin navegador, usando solo consola/terminal
"""

import sys
import os
import json
import time
import subprocess
from datetime import datetime

# ============================================================
# 1. INSTALAR DEPENDENCIAS AUTOMÁTICAMENTE
# ============================================================
def instalar_dependencias():
    """Instala las dependencias necesarias automáticamente"""
    dependencias = ["requests"]
    for pkg in dependencias:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"📦 Instalando {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

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
# 3. CLIENTE POLLINATIONS AI (sin API key)
# ============================================================
class PollinationsClient:
    """Cliente para Pollinations AI - gratuito, sin API key."""
    
    BASE_URL = "https://text.pollinations.ai/openai"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def chat_completion(self, model, messages):
        """Envía una consulta a Pollinations AI"""
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        try:
            response = self.session.post(self.BASE_URL, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception("Respuesta inesperada de Pollinations")
        except Exception as e:
            raise Exception(f"Error en Pollinations: {str(e)}")

# ============================================================
# 4. FUNCIONES DE LA APLICACIÓN
# ============================================================
def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "=" * 50)
    print("🤖 CHAT ACADÉMICO - Menú Principal")
    print("=" * 50)
    print("1. 📝 Generar trabajo académico")
    print("2. 💬 Chat libre con IA")
    print("3. 📋 Ver historial")
    print("4. 🗑️ Limpiar historial")
    print("5. 💾 Guardar último trabajo en archivo")
    print("6. 🔍 Probar modelo")
    print("7. 📚 Ayuda")
    print("0. 🚪 Salir")
    print("=" * 50)

def generar_trabajo(client, modelo="openai"):
    """Genera un trabajo académico completo"""
    tema = input("📝 Tema del trabajo: ").strip()
    if not tema:
        print("❌ Tema vacío")
        return None
    
    print(f"\n⏳ Generando trabajo sobre: {tema}")
    print("   (Esto puede tomar 30-60 segundos...)\n")
    
    prompt = f"""
    Escribe un trabajo académico completo sobre el siguiente tema:

    TEMA: {tema}

    La estructura debe ser EXACTAMENTE esta:

    ## INTRODUCCIÓN (en español)
    [Texto de la introducción en español]

    ## INTRODUCTION (in English)
    [Texto de la introducción en inglés]

    ## DESARROLLO
    [Texto del desarrollo, con subtemas y explicaciones]

    ## CONCLUSIONES
    [Texto de las conclusiones]

    ## BIBLIOGRAFÍA
    [Lista de referencias bibliográficas en formato APA]

    Requisitos:
    - El trabajo debe ser completo, bien estructurado y coherente.
    - Cada sección debe estar claramente marcada con los títulos indicados.
    - La introducción en español e inglés deben tener contenido similar pero no idéntico.
    - El desarrollo debe tener al menos 3 subtemas.
    - Las conclusiones deben ser reflexivas y basadas en el desarrollo.
    - La bibliografía debe incluir al menos 5 fuentes relevantes.
    """
    
    try:
        respuesta = client.chat_completion(modelo, [{"role": "user", "content": prompt}])
        
        print("\n" + "=" * 50)
        print("📊 TRABAJO ACADÉMICO GENERADO")
        print("=" * 50)
        print(respuesta)
        print("=" * 50)
        
        return {
            "tema": tema,
            "resultado": respuesta,
            "modelo": modelo,
            "fecha": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error generando trabajo: {e}")
        return None

def chat_libre(client, modelo="openai"):
    """Chat libre con la IA"""
    print("\n💬 Chat libre con IA (escribe 'salir' para terminar)")
    print("   Modelo: " + modelo)
    print("-" * 40)
    
    historial_chat = []
    
    while True:
        mensaje = input("🧑 Tú: ").strip()
        if mensaje.lower() in ['salir', 'exit', 'quit']:
            break
        if not mensaje:
            continue
        
        # Mostrar indicador de proceso
        print("🤖 IA: ", end="", flush=True)
        
        try:
            # Preparar historial para la IA
            messages = historial_chat + [{"role": "user", "content": mensaje}]
            respuesta = client.chat_completion(modelo, messages)
            
            print(respuesta)
            print()
            
            # Guardar en historial
            historial_chat.append({"role": "user", "content": mensaje})
            historial_chat.append({"role": "assistant", "content": respuesta})
            
        except Exception as e:
            print(f"\n❌ Error: {e}")

def guardar_trabajo(trabajo):
    """Guarda un trabajo en un archivo"""
    if not trabajo:
        print("❌ No hay trabajo para guardar")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"trabajo_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"TRABAJO ACADÉMICO\n")
            f.write(f"TEMA: {trabajo['tema']}\n")
            f.write(f"FECHA: {trabajo['fecha']}\n")
            f.write(f"MODELO: {trabajo['modelo']}\n")
            f.write("=" * 50 + "\n\n")
            f.write(trabajo['resultado'])
        
        print(f"✅ Trabajo guardado en: {filename}")
    except Exception as e:
        print(f"❌ Error guardando: {e}")

def probar_modelo(client):
    """Prueba el modelo de IA"""
    print("\n🔍 Probando modelo...")
    
    modelos = ["openai", "claude", "gemini", "deepseek", "llama", "mistral", "phi", "qwen"]
    print("Modelos disponibles:")
    for i, m in enumerate(modelos, 1):
        print(f"  {i}. {m}")
    
    try:
        opcion = input("Selecciona modelo (1-8, Enter para openai): ").strip()
        if opcion:
            idx = int(opcion) - 1
            modelo = modelos[idx] if 0 <= idx < len(modelos) else "openai"
        else:
            modelo = "openai"
    except:
        modelo = "openai"
    
    print(f"\n⏳ Probando {modelo}...")
    try:
        respuesta = client.chat_completion(modelo, [{"role": "user", "content": "Responde con un saludo corto"}])
        print(f"✅ Modelo responde: {respuesta}")
    except Exception as e:
        print(f"❌ Error: {e}")

def mostrar_ayuda():
    """Muestra la ayuda"""
    print("\n" + "=" * 50)
    print("❓ AYUDA - Chat Académico")
    print("=" * 50)
    print("Chat Académico usa Pollinations AI (gratuito, sin API key)")
    print("\n📝 Opciones:")
    print("   1. Generar trabajo académico con estructura completa")
    print("   2. Chat libre con la IA (conversación)") 
    print("   3. Ver historial de trabajos generados")
    print("   4. Limpiar historial")
    print("   5. Guardar el último trabajo en archivo .txt")
    print("   6. Probar diferentes modelos de IA")
    print("   7. Ver esta ayuda")
    print("   0. Salir")
    print("\n💡 Los trabajos se guardan automáticamente en archivos .txt")
    print("   en el directorio actual.")
    print("=" * 50)

# ============================================================
# 5. FUNCIÓN PRINCIPAL
# ============================================================
def main():
    """Función principal de la aplicación"""
    print("\n" + "=" * 50)
    print("🤖 CHAT ACADÉMICO - Sistema de IA para trabajos")
    print("   v2.0 - Modo Consola para Kalm OS")
    print("   Usa Pollinations AI (gratuito, sin API key)\n")
    
    # Inicializar cliente
    client = PollinationsClient()
    modelo_actual = "openai"
    historial = []
    ultimo_trabajo = None
    
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ").strip()
        
        if opcion == "0":
            print("👋 Saliendo de Chat Académico...")
            break
        
        elif opcion == "1":
            trabajo = generar_trabajo(client, modelo_actual)
            if trabajo:
                historial.append(trabajo)
                ultimo_trabajo = trabajo
                guardar = input("\n💾 ¿Guardar este trabajo en archivo? (s/n): ").strip().lower()
                if guardar == 's':
                    guardar_trabajo(trabajo)
        
        elif opcion == "2":
            chat_libre(client, modelo_actual)
        
        elif opcion == "3":
            if not historial:
                print("📋 No hay trabajos en el historial")
            else:
                print("\n" + "=" * 50)
                print("📋 HISTORIAL DE TRABAJOS")
                print("=" * 50)
                for i, trabajo in enumerate(historial, 1):
                    print(f"{i}. 📝 {trabajo['tema']} ({trabajo['fecha'][:16]})")
                print("=" * 50)
        
        elif opcion == "4":
            if not historial:
                print("📋 No hay trabajos para limpiar")
            else:
                confirmar = input(f"⚠️ ¿Limpiar {len(historial)} trabajos? (s/n): ").strip().lower()
                if confirmar == 's':
                    historial = []
                    ultimo_trabajo = None
                    print("✅ Historial limpiado")
        
        elif opcion == "5":
            if not ultimo_trabajo:
                print("📋 No hay trabajos para guardar")
            else:
                guardar_trabajo(ultimo_trabajo)
        
        elif opcion == "6":
            probar_modelo(client)
            # Actualizar modelo actual si el usuario quiere
            cambiar = input("\n¿Cambiar modelo por defecto? (s/n): ").strip().lower()
            if cambiar == 's':
                modelos = ["openai", "claude", "gemini", "deepseek", "llama", "mistral", "phi", "qwen"]
                print("Modelos disponibles:")
                for i, m in enumerate(modelos, 1):
                    print(f"  {i}. {m}")
                try:
                    opc = input("Selecciona modelo (1-8): ").strip()
                    if opc:
                        idx = int(opc) - 1
                        modelo_actual = modelos[idx] if 0 <= idx < len(modelos) else "openai"
                        print(f"✅ Modelo actual: {modelo_actual}")
                except:
                    pass
        
        elif opcion == "7":
            mostrar_ayuda()
        
        else:
            print("❌ Opción inválida")
        
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Saliendo de Chat Académico...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)