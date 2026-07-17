#!/usr/bin/env python3
"""
Kroot Corp IA - Wrapper para Kalm OS
Este script ejecuta el lanzador de Kroot Corp
"""

import os
import sys
import subprocess
from pathlib import Path

# Obtener la ruta del directorio del proyecto
BASE_DIR = Path(__file__).parent / "kroot_corp"
RUN_SCRIPT = BASE_DIR / "run.py"

def main():
    if not RUN_SCRIPT.exists():
        print("❌ No se encuentra Kroot Corp. Verifica la instalación.")
        print(f"   Buscando en: {RUN_SCRIPT}")
        return
    
    print("🏢 Iniciando Kroot Corp IA...")
    
    # Cambiar al directorio del proyecto
    os.chdir(str(BASE_DIR))
    
    # Ejecutar el lanzador
    subprocess.run([sys.executable, str(RUN_SCRIPT)])

if __name__ == "__main__":
    main()