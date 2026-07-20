#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KROOT CORP - VERSIÓN CONSOLA (para entornos headless como Render)
"""

import sys
import os
import subprocess

def main():
    print("\n" + "=" * 50)
    print("🏢 KROOT CORP IA - Modo Consola")
    print("=" * 50)
    print("   Este es el modo para entornos sin interfaz gráfica.")
    print("   Para la versión GUI, ejecuta en Windows o con display.\n")
    
    try:
        # Ejecutar la versión autónoma
        from kroot_app import main as kroot_main
        kroot_main()
    except ImportError:
        print("📦 Cargando versión autónoma...")
        exec(open(os.path.join(os.path.dirname(__file__), 'kroot_app.py')).read())

if __name__ == "__main__":
    main()