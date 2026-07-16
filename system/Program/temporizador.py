#!/usr/bin/env python3
"""Temporizador con cuenta regresiva"""
import os
import time
import sys

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    try:
        print("⏱️ TEMPORIZADOR")
        print("=" * 30)
        
        try:
            segundos = int(input("Segundos: "))
            if segundos <= 0:
                print("❌ Debe ser un número positivo")
                return
        except ValueError:
            print("❌ Ingresa un número válido")
            return
        
        clear()
        print("⏱️ CUENTA REGRESIVA")
        print("=" * 30)
        
        for i in range(segundos, 0, -1):
            print(f"\n  {i} segundos restantes")
            print("  " + "█" * (i * 10 // segundos) + "░" * (10 - (i * 10 // segundos)))
            time.sleep(1)
            clear()
            print("⏱️ CUENTA REGRESIVA")
            print("=" * 30)
        
        print("\n  ⏰ ¡TIEMPO CUMPLIDO!")
        print("  🔔" * 5)
        
        # Sonido (si está disponible)
        try:
            import winsound
            winsound.Beep(1000, 500)
            winsound.Beep(1200, 500)
        except:
            print("\a")
        
        input("\nPresiona Enter para salir...")
        
    except KeyboardInterrupt:
        print("\n¡Temporizador cancelado!")

if __name__ == "__main__":
    main()