#!/usr/bin/env python3
"""Calculadora Científica"""
import os
import math

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    while True:
        clear()
        print("🧮 CALCULADORA CIENTÍFICA")
        print("=" * 40)
        print("1. Seno")
        print("2. Coseno")
        print("3. Tangente")
        print("4. Logaritmo natural")
        print("5. Logaritmo base 10")
        print("6. Potencia")
        print("7. Raíz cuadrada")
        print("8. Factorial")
        print("9. Pi")
        print("10. Número e")
        print("0. Salir")
        print("=" * 40)
        
        opcion = input("Opción: ").strip()
        
        if opcion == '0':
            print("¡Hasta luego!")
            break
        
        try:
            if opcion in ['1', '2', '3']:
                angulo = float(input("Ángulo (grados): "))
                rad = math.radians(angulo)
                if opcion == '1':
                    print(f"\n✅ sen({angulo}°) = {math.sin(rad):.6f}")
                elif opcion == '2':
                    print(f"\n✅ cos({angulo}°) = {math.cos(rad):.6f}")
                else:
                    if rad % math.pi == math.pi/2:
                        print("\n❌ Tangente no definida para este ángulo")
                    else:
                        print(f"\n✅ tan({angulo}°) = {math.tan(rad):.6f}")
            
            elif opcion == '4':
                n = float(input("Número: "))
                if n <= 0:
                    print("❌ Número debe ser positivo")
                else:
                    print(f"\n✅ ln({n}) = {math.log(n):.6f}")
            
            elif opcion == '5':
                n = float(input("Número: "))
                if n <= 0:
                    print("❌ Número debe ser positivo")
                else:
                    print(f"\n✅ log10({n}) = {math.log10(n):.6f}")
            
            elif opcion == '6':
                base = float(input("Base: "))
                exp = float(input("Exponente: "))
                print(f"\n✅ {base}^{exp} = {base**exp:.6f}")
            
            elif opcion == '7':
                n = float(input("Número: "))
                if n < 0:
                    print("❌ Número debe ser positivo")
                else:
                    print(f"\n✅ √{n} = {math.sqrt(n):.6f}")
            
            elif opcion == '8':
                n = int(input("Número entero: "))
                if n < 0:
                    print("❌ Número debe ser positivo")
                else:
                    print(f"\n✅ {n}! = {math.factorial(n)}")
            
            elif opcion == '9':
                print(f"\n✅ π = {math.pi:.15f}")
            
            elif opcion == '10':
                print(f"\n✅ e = {math.e:.15f}")
            
            else:
                print("❌ Opción inválida")
        
        except ValueError:
            print("❌ Ingresa un número válido")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()