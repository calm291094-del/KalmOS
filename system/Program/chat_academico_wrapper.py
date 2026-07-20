#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chat Académico - Wrapper para Kalm OS
Ejecuta la versión nativa de consola
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Obtener la ruta de la aplicación
    app_path = Path(__file__).parent / "chat_app.py"
    
    if not app_path.exists():
        print(f"❌ No se encuentra chat_app.py en: {app_path}")
        return
    
    # Ejecutar la aplicación
    subprocess.run([sys.executable, str(app_path)] + sys.argv[1:])

if __name__ == "__main__":
    main()