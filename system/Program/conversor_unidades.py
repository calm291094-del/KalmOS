#!/usr/bin/env python3
"""Conversor de Unidades"""
import os
import math

class UnitConverter:
    def __init__(self):
        self.conversiones = {
            'longitud': {
                'metros': 1,
                'kilometros': 0.001,
                'centimetros': 100,
                'milimetros': 1000,
                'pulgadas': 39.3701,
                'pies': 3.28084,
                'yardas': 1.09361,
                'millas': 0.000621371
            },
            'masa': {
                'gramos': 1,
                'kilogramos': 0.001,
                'libras': 0.00220462,
                'onzas': 0.035274
            },
            'volumen': {
                'litros': 1,
                'mililitros': 1000,
                'galones': 0.264172,
                'tazas': 4.22675
            },
            'temperatura': {
                'celsius': 'c',
                'fahrenheit': 'f',
                'kelvin': 'k'
            }
        }
    
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🔄 CONVERSOR DE UNIDADES")
        print("=" * 40)
        print("1. Longitud")
        print("2. Masa")
        print("3. Volumen")
        print("4. Temperatura")
        print("0. Salir")
        print("=" * 40)
    
    def convertir_longitud(self):
        print("\n📏 CONVERSOR DE LONGITUD")
        print("-" * 30)
        valor = float(input("Valor: "))
        desde = input("Desde (metros, km, cm, mm, pulgadas, pies, yardas, millas): ").lower()
        hasta = input("Hasta (metros, km, cm, mm, pulgadas, pies, yardas, millas): ").lower()
        
        if desde not in self.conversiones['longitud'] or hasta not in self.conversiones['longitud']:
            print("❌ Unidad no válida")
            return
        
        # Convertir a metros
        valor_metros = valor / self.conversiones['longitud'][desde]
        # Convertir de metros a destino
        resultado = valor_metros * self.conversiones['longitud'][hasta]
        
        print(f"\n✅ {valor} {desde} = {resultado:.6f} {hasta}")
    
    def convertir_masa(self):
        print("\n⚖️ CONVERSOR DE MASA")
        print("-" * 30)
        valor = float(input("Valor: "))
        desde = input("Desde (gramos, kg, libras, onzas): ").lower()
        hasta = input("Hasta (gramos, kg, libras, onzas): ").lower()
        
        if desde not in self.conversiones['masa'] or hasta not in self.conversiones['masa']:
            print("❌ Unidad no válida")
            return
        
        valor_gramos = valor / self.conversiones['masa'][desde]
        resultado = valor_gramos * self.conversiones['masa'][hasta]
        
        print(f"\n✅ {valor} {desde} = {resultado:.6f} {hasta}")
    
    def convertir_volumen(self):
        print("\n🧪 CONVERSOR DE VOLUMEN")
        print("-" * 30)
        valor = float(input("Valor: "))
        desde = input("Desde (litros, ml, galones, tazas): ").lower()
        hasta = input("Hasta (litros, ml, galones, tazas): ").lower()
        
        if desde not in self.conversiones['volumen'] or hasta not in self.conversiones['volumen']:
            print("❌ Unidad no válida")
            return
        
        valor_litros = valor / self.conversiones['volumen'][desde]
        resultado = valor_litros * self.conversiones['volumen'][hasta]
        
        print(f"\n✅ {valor} {desde} = {resultado:.6f} {hasta}")
    
    def convertir_temperatura(self):
        print("\n🌡️ CONVERSOR DE TEMPERATURA")
        print("-" * 30)
        valor = float(input("Valor: "))
        desde = input("Desde (C, F, K): ").upper()
        hasta = input("Hasta (C, F, K): ").upper()
        
        # Convertir a Celsius primero
        if desde == 'C':
            celsius = valor
        elif desde == 'F':
            celsius = (valor - 32) * 5/9
        elif desde == 'K':
            celsius = valor - 273.15
        else:
            print("❌ Unidad no válida")
            return
        
        # Convertir de Celsius a destino
        if hasta == 'C':
            resultado = celsius
        elif hasta == 'F':
            resultado = celsius * 9/5 + 32
        elif hasta == 'K':
            resultado = celsius + 273.15
        else:
            print("❌ Unidad no válida")
            return
        
        print(f"\n✅ {valor} {desde} = {resultado:.2f} {hasta}")
    
    def run(self):
        while True:
            self.display()
            
            opcion = input("\nSelecciona una opción (0-4): ").strip()
            
            if opcion == '0':
                print("¡Hasta luego!")
                break
            elif opcion == '1':
                self.convertir_longitud()
            elif opcion == '2':
                self.convertir_masa()
            elif opcion == '3':
                self.convertir_volumen()
            elif opcion == '4':
                self.convertir_temperatura()
            else:
                print("❌ Opción inválida")
            
            input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    converter = UnitConverter()
    converter.run()