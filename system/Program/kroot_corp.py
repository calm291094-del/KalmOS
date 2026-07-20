#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KROOT CORP - APLICACIÓN NATIVA PARA KALM OS
Versión que funciona sin navegador, usando solo consola/terminal
"""

import sys
import os
import json
import time
from datetime import datetime

# Intentar importar los módulos de Kroot
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'kroot_corp'))
    from app.crew import ejecutar_empresa
    from app.memory import guardar_aprendizaje, obtener_lessons_learned
except ImportError as e:
    print(f"❌ Error importando Kroot Corp: {e}")
    print("📦 Intentando instalar dependencias...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi uvicorn jinja2 python-multipart itsdangerous langchain langchain-core requests duckduckgo-search huggingface-hub"])
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'kroot_corp'))
    from app.crew import ejecutar_empresa
    from app.memory import guardar_aprendizaje, obtener_lessons_learned


def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "=" * 50)
    print("🏢 KROOT CORP IA - Menú Principal")
    print("=" * 50)
    print("1. 📝 Generar nuevo informe")
    print("2. 📋 Ver historial de informes")
    print("3. 🗑️ Limpiar historial")
    print("4. 💾 Guardar informe en archivo")
    print("5. ❓ Ayuda")
    print("0. 🚪 Salir")
    print("=" * 50)


def generar_informe():
    """Genera un nuevo informe"""
    tema = input("📝 Tema del informe: ").strip()
    if not tema:
        print("❌ Tema vacío")
        return None
    
    print(f"\n⏳ Generando informe sobre: {tema}")
    print("   (Esto puede tomar unos segundos...)\n")
    
    try:
        # Función para actualizar estado
        def update_status(phase):
            print(f"   📡 {phase}")
        
        # Ejecutar los agentes
        resultado = ejecutar_empresa(tema, update_status)
        
        print("\n" + "=" * 50)
        print("📊 INFORME GENERADO")
        print("=" * 50)
        print(resultado)
        print("=" * 50)
        
        return {
            "tema": tema,
            "resultado": resultado,
            "estado": "Éxito",
            "fecha": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error generando informe: {e}")
        return {
            "tema": tema,
            "resultado": f"Error: {e}",
            "estado": "Fallo",
            "fecha": datetime.now().isoformat()
        }


def guardar_informe(informe):
    """Guarda el informe en un archivo"""
    if not informe:
        print("❌ No hay informe para guardar")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"informe_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"INFORME: {informe['tema']}\n")
            f.write(f"FECHA: {informe['fecha']}\n")
            f.write(f"ESTADO: {informe['estado']}\n")
            f.write("=" * 50 + "\n\n")
            f.write(informe['resultado'])
        
        print(f"✅ Informe guardado en: {filename}")
    except Exception as e:
        print(f"❌ Error guardando informe: {e}")


def main():
    """Función principal"""
    print("🏢 KROOT CORP IA - Sistema de Agentes")
    print("   v1.0 - Modo Consola para Kalm OS")
    print("   Usa Pollinations AI (gratuito, sin API key)\n")
    
    historial = []
    
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ").strip()
        
        if opcion == "0":
            print("👋 Saliendo de Kroot Corp...")
            break
        
        elif opcion == "1":
            informe = generar_informe()
            if informe:
                historial.append(informe)
                guardar = input("💾 ¿Guardar informe en archivo? (s/n): ").strip().lower()
                if guardar == 's':
                    guardar_informe(informe)
        
        elif opcion == "2":
            if not historial:
                print("📋 No hay informes en el historial")
            else:
                print("\n" + "=" * 50)
                print("📋 HISTORIAL DE INFORMES")
                print("=" * 50)
                for i, info in enumerate(historial, 1):
                    estado = "✅" if info['estado'] == 'Éxito' else "❌"
                    print(f"{i}. {estado} {info['tema']} ({info['fecha'][:16]})")
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
                # Guardar el último informe
                guardar_informe(historial[-1])
        
        elif opcion == "5":
            print("\n" + "=" * 50)
            print("❓ AYUDA")
            print("=" * 50)
            print("Kroot Corp IA es un sistema de agentes que genera informes")
            print("sobre cualquier tema usando IA gratuita (Pollinations).")
            print("\n📝 Para generar un informe:")
            print("   1. Selecciona la opción 1")
            print("   2. Escribe el tema")
            print("   3. Espera a que los agentes trabajen")
            print("   4. El informe se mostrará en pantalla")
            print("\n💾 Los informes se guardan en archivos .txt")
            print("   en el directorio actual.")
            print("=" * 50)
        
        else:
            print("❌ Opción inválida")
        
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()
