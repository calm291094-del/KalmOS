#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CHAT ACADÉMICO - VERSIÓN AUTÓNOMA PARA KALM OS
Sin dependencias externas, usa solo requests y Pollinations AI
"""

import sys
import os
import time
import subprocess
from datetime import datetime

# ============================================================
# 1. INSTALAR DEPENDENCIAS
# ============================================================
def instalar_dependencias():
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
# 3. CLIENTE POLLINATIONS AI
# ============================================================
class PollinationsClient:
    BASE_URL = "https://text.pollinations.ai/openai"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def chat_completion(self, model, messages):
        payload = {"model": model, "messages": messages, "stream": False}
        try:
            response = self.session.post(self.BASE_URL, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"Error en Pollinations: {str(e)}")

# ============================================================
# 4. FUNCIONES
# ============================================================
def generar_trabajo(tema, client, modelo="openai"):
    prompt = f"""
    Escribe un trabajo académico completo sobre: {tema}
    
    Estructura EXACTA:
    ## INTRODUCCIÓN (en español)
    ## INTRODUCTION (in English)  
    ## DESARROLLO
    ## CONCLUSIONES
    ## BIBLIOGRAFÍA
    """
    try:
        return client.chat_completion(modelo, [{"role": "user", "content": prompt}])
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ============================================================
# 5. FUNCIÓN PRINCIPAL
# ============================================================
def main():
    print("\n" + "=" * 50)
    print("🤖 CHAT ACADÉMICO - Sistema de IA")
    print("   v2.0 - Modo Consola para Kalm OS")
    print("   Usa Pollinations AI (gratuito, sin API key)\n")
    
    client = PollinationsClient()
    modelo_actual = "openai"
    ultimo_trabajo = None
    
    while True:
        print("\n" + "=" * 50)
        print("🤖 CHAT ACADÉMICO - Menú Principal")
        print("=" * 50)
        print("1. 📝 Generar trabajo académico")
        print("2. 💬 Chat libre con IA")
        print("3. 💾 Guardar último trabajo")
        print("4. 🔍 Probar modelo")
        print("0. 🚪 Salir")
        print("=" * 50)
        
        opcion = input("Selecciona una opción: ").strip()
        
        if opcion == "0":
            print("👋 Saliendo de Chat Académico...")
            break
        
        elif opcion == "1":
            tema = input("📝 Tema del trabajo: ").strip()
            if not tema:
                print("❌ Tema vacío")
                continue
            
            print(f"\n⏳ Generando trabajo sobre: {tema}")
            print("   (Esto puede tomar 30-60 segundos...)\n")
            
            resultado = generar_trabajo(tema, client, modelo_actual)
            
            print("\n" + "=" * 50)
            print("📊 TRABAJO GENERADO")
            print("=" * 50)
            print(resultado)
            print("=" * 50)
            
            ultimo_trabajo = {
                "tema": tema,
                "resultado": resultado,
                "fecha": datetime.now().isoformat()
            }
            
            guardar = input("\n💾 ¿Guardar en archivo? (s/n): ").strip().lower()
            if guardar == 's':
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"trabajo_{timestamp}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(resultado)
                print(f"✅ Guardado en: {filename}")
        
        elif opcion == "2":
            print("\n💬 Chat libre (escribe 'salir' para terminar)")
            print("-" * 40)
            historial_chat = []
            
            while True:
                mensaje = input("🧑 Tú: ").strip()
                if mensaje.lower() in ['salir', 'exit', 'quit']:
                    break
                if not mensaje:
                    continue
                
                print("🤖 IA: ", end="", flush=True)
                try:
                    messages = historial_chat + [{"role": "user", "content": mensaje}]
                    respuesta = client.chat_completion(modelo_actual, messages)
                    print(respuesta + "\n")
                    historial_chat.append({"role": "user", "content": mensaje})
                    historial_chat.append({"role": "assistant", "content": respuesta})
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        elif opcion == "3":
            if not ultimo_trabajo:
                print("📋 No hay trabajo para guardar")
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"trabajo_{timestamp}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(ultimo_trabajo['resultado'])
                print(f"✅ Guardado en: {filename}")
        
        elif opcion == "4":
            print("\n🔍 Probando modelo...")
            try:
                resp = client.chat_completion("openai", [{"role": "user", "content": "Responde OK"}])
                print(f"✅ Modelo responde: {resp}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Saliendo...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)