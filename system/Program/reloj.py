#!/usr/bin/env python3
"""Reloj Digital en consola"""
import os
import time
import sys
from datetime import datetime

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    try:
        while True:
            clear()
            now = datetime.now()
            print("🕐 RELOJ DIGITAL")
            print("=" * 30)
            print(f"\n  {now.strftime('%H:%M:%S')}")
            print(f"\n  {now.strftime('%A, %d de %B de %Y')}")
            print("\n" + "=" * 30)
            print("Presiona Ctrl+C para salir")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n¡Hasta luego!")

if __name__ == "__main__":
    main()