#!/usr/bin/env python3
"""Analizador de Texto"""
import os
import string

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    try:
        clear()
        print("📊 ANALIZADOR DE TEXTO")
        print("=" * 40)
        print("Ingresa el texto (escribe '///' para terminar):")
        print("-" * 40)
        
        lines = []
        while True:
            line = input()
            if line.strip() == '///':
                break
            lines.append(line)
        
        texto = '\n'.join(lines)
        
        if not texto.strip():
            print("❌ No ingresaste texto")
            return
        
        # Análisis
        palabras = texto.split()
        caracteres = len(texto)
        letras = sum(1 for c in texto if c.isalpha())
        digitos = sum(1 for c in texto if c.isdigit())
        espacios = sum(1 for c in texto if c.isspace())
        puntuacion = sum(1 for c in texto if c in string.punctuation)
        
        # Palabras más comunes
        from collections import Counter
        palabras_clean = [p.lower().strip(string.punctuation) for p in palabras if p.strip()]
        contador = Counter(palabras_clean)
        top_palabras = contador.most_common(5)
        
        clear()
        print("📊 ANALIZADOR DE TEXTO")
        print("=" * 50)
        print(f"\n📄 Texto analizado:")
        print(f"   Líneas: {len(lines)}")
        print(f"   Palabras: {len(palabras)}")
        print(f"   Caracteres totales: {caracteres}")
        print(f"   Letras: {letras}")
        print(f"   Dígitos: {digitos}")
        print(f"   Espacios: {espacios}")
        print(f"   Signos de puntuación: {puntuacion}")
        
        if top_palabras:
            print(f"\n📊 Palabras más frecuentes:")
            for palabra, count in top_palabras:
                print(f"   {palabra}: {count} veces")
        
        print("\n" + "=" * 50)
        
    except KeyboardInterrupt:
        print("\n¡Cancelado!")
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()