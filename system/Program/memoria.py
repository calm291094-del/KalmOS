#!/usr/bin/env python3
"""Juego de Memoria en consola"""
import random
import os
import time

class MemoryGame:
    def __init__(self):
        self.tamano = 4  # 4x4
        self.cartas = []
        self.reveladas = []
        self.primera = None
        self.parejas = 0
        self.intentos = 0
        
    def crear_tablero(self):
        emojis = ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼']
        pares = emojis[:self.tamano * self.tamano // 2]
        self.cartas = pares * 2
        random.shuffle(self.cartas)
        self.reveladas = [False] * (self.tamano * self.tamano)
        self.primera = None
        self.parejas = 0
        self.intentos = 0
    
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🧠 JUEGO DE MEMORIA")
        print("=" * 40)
        print(f"Parejas encontradas: {self.parejas}")
        print(f"Intentos: {self.intentos}")
        print("=" * 40)
        
        print("   " + " ".join(f"{i:2}" for i in range(self.tamano)))
        print("   " + "─" * (self.tamano * 3))
        
        for i in range(self.tamano):
            print(f"{i:2}│", end="")
            for j in range(self.tamano):
                idx = i * self.tamano + j
                if self.reveladas[idx]:
                    print(f" {self.cartas[idx]} ", end="")
                else:
                    print(" ■ ", end="")
            print()
        
        print("=" * 40)
        print("Ingresa: fila,columna (ej: 1,2) o Q para salir")
    
    def jugar(self):
        while True:
            self.crear_tablero()
            
            while self.parejas < (self.tamano * self.tamano // 2):
                self.display()
                
                try:
                    entrada = input("\nSelecciona una carta (fila,columna): ").strip()
                    if entrada.lower() == 'q':
                        print("¡Hasta luego!")
                        return
                    
                    fila, col = map(int, entrada.split(','))
                    if fila < 0 or fila >= self.tamano or col < 0 or col >= self.tamano:
                        print("❌ Posición inválida")
                        continue
                    
                    idx = fila * self.tamano + col
                    if self.reveladas[idx]:
                        print("❌ Esta carta ya está revelada")
                        continue
                    
                    if self.primera is None:
                        self.primera = idx
                        self.reveladas[idx] = True
                    else:
                        self.reveladas[idx] = True
                        self.intentos += 1
                        self.display()
                        
                        if self.cartas[self.primera] == self.cartas[idx]:
                            print("🎉 ¡Pareja encontrada!")
                            self.parejas += 1
                            self.primera = None
                        else:
                            print("❌ No coinciden")
                            time.sleep(1)
                            self.reveladas[self.primera] = False
                            self.reveladas[idx] = False
                            self.primera = None
                        
                        input("\nPresiona Enter para continuar...")
                        
                except ValueError:
                    print("❌ Formato inválido. Usa fila,columna")
                    input("Presiona Enter...")
                except KeyboardInterrupt:
                    print("\n¡Juego terminado!")
                    return
            
            print("\n🎉 ¡FELICITACIONES! Completaste el juego")
            print(f"Intentos totales: {self.intentos}")
            
            if input("\n¿Jugar otra vez? (s/n): ").lower() != 's':
                break
        
        print("¡Gracias por jugar!")

if __name__ == "__main__":
    juego = MemoryGame()
    juego.jugar()