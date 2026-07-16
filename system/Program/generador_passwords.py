#!/usr/bin/env python3
"""Generador de Contraseñas Seguras"""
import random
import string
import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def generar_password(longitud=12, mayusculas=True, minusculas=True, numeros=True, simbolos=True):
    caracteres = ""
    if mayusculas:
        caracteres += string.ascii_uppercase
    if minusculas:
        caracteres += string.ascii_lowercase
    if numeros:
        caracteres += string.digits
    if simbolos:
        caracteres += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    if not caracteres:
        return "❌ Debes seleccionar al menos un tipo de carácter"
    
    # Asegurar al menos uno de cada tipo seleccionado
    password = []
    if mayusculas:
        password.append(random.choice(string.ascii_uppercase))
    if minusculas:
        password.append(random.choice(string.ascii_lowercase))
    if numeros:
        password.append(random.choice(string.digits))
    if simbolos:
        password.append(random.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))
    
    # Completar el resto
    for _ in range(longitud - len(password)):
        password.append(random.choice(caracteres))
    
    random.shuffle(password)
    return ''.join(password)

def main():
    while True:
        clear()
        print("🔐 GENERADOR DE CONTRASEÑAS")
        print("=" * 40)
        
        try:
            longitud = int(input("Longitud (8-32): ") or "12")
            longitud = max(8, min(32, longitud))
        except:
            longitud = 12
        
        print("\nTipos de caracteres:")
        mayus = input("¿Mayúsculas? (s/n): ").lower() != 'n'
        minus = input("¿Minúsculas? (s/n): ").lower() != 'n'
        nums = input("¿Números? (s/n): ").lower() != 'n'
        simb = input("¿Símbolos? (s/n): ").lower() != 'n'
        
        if not (mayus or minus or nums or simb):
            print("❌ Debes seleccionar al menos un tipo")
            input("Presiona Enter...")
            continue
        
        password = generar_password(longitud, mayus, minus, nums, simb)
        
        print("\n" + "=" * 40)
        print(f"🔑 Contraseña generada:")
        print(f"\n  {password}\n")
        print(f"📊 Longitud: {len(password)} caracteres")
        print(f"📊 Fuerza: {'Alta' if longitud >= 16 else 'Media' if longitud >= 10 else 'Baja'}")
        print("=" * 40)
        
        if input("\n¿Generar otra? (s/n): ").lower() != 's':
            break
    
    print("\n¡Hasta luego!")

if __name__ == "__main__":
    main()