#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KROOT CORP - VERSIÓN AUTÓNOMA PARA KALM OS
Sin dependencias externas, usa solo requests y Pollinations AI
"""

import sys
import os
import json
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
# 4. FUNCIONES DE KROOT CORP
# ============================================================
def generar_informe(tema, client, modelo="openai"):
    """Genera un informe completo usando Pollinations AI"""
    
    # Prompt para el investigador
    prompt_investigador = f"""
    INVESTIGA a fondo sobre: '{tema}'
    
    Responde SOLO con hechos y datos clave:
    - 5 puntos clave
    - Datos relevantes
    - Tendencias actuales
    """
    
    # Prompt para el redactor
    prompt_redactor = f"""
    Basado en esta investigación, redacta un informe ejecutivo profesional:
    
    INVESTIGACIÓN:
    {{investigacion}}
    
    Estructura:
    ## INTRODUCCIÓN
    ## PUNTOS CLAVE
    ## CONCLUSIONES
    ## RECOMENDACIONES
    """
    
    try:
        # Fase 1: Investigación
        print("   🔍 Fase 1: Investigando...")
        investigacion = client.chat_completion(modelo, [{"role": "user", "content": prompt_investigador}])
        
        # Fase 2: Redacción
        print("   ✍️ Fase 2: Redactando informe...")
        prompt_completo = prompt_redactor.replace("{investigacion}", investigacion)
        informe = client.chat_completion(modelo, [{"role": "user", "content": prompt_completo}])
        
        # Fase 3: QA
        print("   🔎 Fase 3: Revisión de calidad...")
        prompt_critica = f"""
        Revisa este informe y da feedback:
        
        INFORME:
        {informe}
        
        Si es bueno, APRUÉBALO.
        Si es malo, explica por qué y cómo mejorarlo.
        """
        critica = client.chat_completion(modelo, [{"role": "user", "content": prompt_critica}])
        
        resultado = f"""
📊 INFORME EJECUTIVO: {tema.upper()}
{'=' * 50}

{informe}

{'=' * 50}
📝 VEREDICTO DE CALIDAD:
{critica}
{'=' * 50}
"""
        return resultado
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ============================================================
# 5. FUNCIÓN PRINCIPAL
# ============================================================
def main():
    print("\n" + "=" * 50)
    print("🏢 KROOT CORP IA - Sistema de Agentes")
    print("   v2.0 - Modo Consola para Kalm OS")
    print("   Usa Pollinations AI (gratuito, sin API key)\n")
    
    client = PollinationsClient()
    historial = []
    
    while True:
        print("\n" + "=" * 50)
        print("🏢 KROOT CORP IA - Menú Principal")
        print("=" * 50)
        print("1. 📝 Generar nuevo informe")
        print("2. 📋 Ver historial")
        print("3. 🗑️ Limpiar historial")
        print("4. 💾 Guardar informe en archivo")
        print("5. 🔍 Probar modelo")
        print("0. 🚪 Salir")
        print("=" * 50)
        
        opcion = input("Selecciona una opción: ").strip()
        
        if opcion == "0":
            print("👋 Saliendo de Kroot Corp...")
            break
        
        elif opcion == "1":
            tema = input("📝 Tema del informe: ").strip()
            if not tema:
                print("❌ Tema vacío")
                continue
            
            print(f"\n⏳ Generando informe sobre: {tema}")
            print("   (Esto puede tomar 30-60 segundos...)\n")
            
            resultado = generar_informe(tema, client)
            
            print("\n" + "=" * 50)
            print("📊 INFORME GENERADO")
            print("=" * 50)
            print(resultado)
            print("=" * 50)
            
            historial.append({
                "tema": tema,
                "resultado": resultado,
                "fecha": datetime.now().isoformat()
            })
            
            guardar = input("\n💾 ¿Guardar informe en archivo? (s/n): ").strip().lower()
            if guardar == 's':
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"informe_{timestamp}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(resultado)
                print(f"✅ Informe guardado en: {filename}")
        
        elif opcion == "2":
            if not historial:
                print("📋 No hay informes en el historial")
            else:
                print("\n" + "=" * 50)
                print("📋 HISTORIAL")
                print("=" * 50)
                for i, info in enumerate(historial, 1):
                    print(f"{i}. 📝 {info['tema']} ({info['fecha'][:16]})")
                print("=" * 50)
        
        elif opcion == "3":
            if not historial:
                print("📋 No hay informes para limpiar")
            else:
                confirmar = input(f"⚠️ ¿Limpiar {len(historial)} informes? (s/n): ").strip().lower()
                if confirmar == 's':
                    historial = []
                    print("✅ Historial limpiado")
        
        elif opcion == "4":
            if not historial:
                print("📋 No hay informes para guardar")
            else:
                ultimo = historial[-1]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"informe_{timestamp}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(ultimo['resultado'])
                print(f"✅ Informe guardado en: {filename}")
        
        elif opcion == "5":
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
