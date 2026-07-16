#!/usr/bin/env python3
"""Calculadora en consola"""
import os
import math

def mostrar_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("🧮 CALCULADORA")
    print("=" * 30)
    print("1. Suma")
    print("2. Resta")
    print("3. Multiplicación")
    print("4. División")
    print("5. Potencia")
    print("6. Raíz cuadrada")
    print("7. Seno")
    print("8. Coseno")
    print("9. Tangente")
    print("10. Salir")
    print("=" * 30)

def obtener_numero(mensaje):
    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("❌ Ingresa un número válido")

def main():
    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción (1-10): ").strip()
        
        if opcion == "10":
            print("¡Hasta luego!")
            break
        
        if opcion == "1":
            a = obtener_numero("Primer número: ")
            b = obtener_numero("Segundo número: ")
            print(f"\n✅ {a} + {b} = {a + b}")
        
        elif opcion == "2":
            a = obtener_numero("Primer número: ")
            b = obtener_numero("Segundo número: ")
            print(f"\n✅ {a} - {b} = {a - b}")
        
        elif opcion == "3":
            a = obtener_numero("Primer número: ")
            b = obtener_numero("Segundo número: ")
            print(f"\n✅ {a} × {b} = {a * b}")
        
        elif opcion == "4":
            a = obtener_numero("Dividendo: ")
            b = obtener_numero("Divisor: ")
            if b == 0:
                print("\n❌ No se puede dividir entre cero")
            else:
                print(f"\n✅ {a} ÷ {b} = {a / b}")
        
        elif opcion == "5":
            a = obtener_numero("Base: ")
            b = obtener_numero("Exponente: ")
            print(f"\n✅ {a} ^ {b} = {a ** b}")
        
        elif opcion == "6":
            a = obtener_numero("Número: ")
            if a < 0:
                print("\n❌ No se puede calcular raíz de número negativo")
            else:
                print(f"\n✅ √{a} = {math.sqrt(a)}")
        
        elif opcion == "7":
            a = obtener_numero("Ángulo (grados): ")
            print(f"\n✅ sen({a}°) = {math.sin(math.radians(a))}")
        
        elif opcion == "8":
            a = obtener_numero("Ángulo (grados): ")
            print(f"\n✅ cos({a}°) = {math.cos(math.radians(a))}")
        
        elif opcion == "9":
            a = obtener_numero("Ángulo (grados): ")
            if a % 180 == 90:
                print("\n❌ Tangente no definida para este ángulo")
            else:
                print(f"\n✅ tan({a}°) = {math.tan(math.radians(a))}")
        
        else:
            print("\n❌ Opción inválida")
        
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()