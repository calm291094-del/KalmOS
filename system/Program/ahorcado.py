#!/usr/bin/env python3
"""Juego del Ahorcado en consola"""
import random
import os

class Hangman:
    def __init__(self):
        self.palabras = [
            'python', 'programacion', 'computadora', 'internet', 'algoritmo',
            'desarrollador', 'sistema', 'codigo', 'terminal', 'archivo',
            'red', 'servidor', 'cliente', 'base', 'datos', 'nube',
            'seguridad', 'encriptacion', 'inteligencia', 'artificial'
        ]
        self.palabra = random.choice(self.palabras)
        self.letras_adivinadas = []
        self.letras_falladas = []
        self.intentos_maximos = 6
        
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🎯 AHORCADO")
        print("=" * 30)
        
        # Estado del ahorcado
        estados = [
            """
              ------
              |    |
              |
              |
              |
              |
            =========
            """,
            """
              ------
              |    |
              |    O
              |
              |
              |
            =========
            """,
            """
              ------
              |    |
              |    O
              |    |
              |
              |
            =========
            """,
            """
              ------
              |    |
              |    O
              |   /|
              |
              |
            =========
            """,
            """
              ------
              |    |
              |    O
              |   /|\\
              |
              |
            =========
            """,
            """
              ------
              |    |
              |    O
              |   /|\\
              |   /
              |
            =========
            """,
            """
              ------
              |    |
              |    O
              |   /|\\
              |   / \\
              |
            =========
            """
        ]
        print(estados[len(self.letras_falladas)])
        
        # Palabra
        palabra_mostrar = ""
        for letra in self.palabra:
            if letra in self.letras_adivinadas:
                palabra_mostrar += letra + " "
            else:
                palabra_mostrar += "_ "
        print(f"\nPalabra: {palabra_mostrar}")
        
        # Letras falladas
        if self.letras_falladas:
            print(f"\nLetras falladas: {', '.join(self.letras_falladas)}")
        
        print(f"\nIntentos restantes: {self.intentos_maximos - len(self.letras_falladas)}")
    
    def jugar(self):
        while True:
            self.display()
            
            if len(self.letras_falladas) >= self.intentos_maximos:
                print(f"\n💀 ¡Perdiste! La palabra era: {self.palabra}")
                break
            
            # Verificar si ganó
            ganaste = True
            for letra in self.palabra:
                if letra not in self.letras_adivinadas:
                    ganaste = False
                    break
            if ganaste:
                print("\n🎉 ¡Ganaste! Adivinaste la palabra")
                break
            
            letra = input("\nIngresa una letra: ").lower()
            
            if len(letra) != 1 or not letra.isalpha():
                print("Ingresa una sola letra")
                continue
            
            if letra in self.letras_adivinadas or letra in self.letras_falladas:
                print("Ya usaste esa letra")
                continue
            
            if letra in self.palabra:
                self.letras_adivinadas.append(letra)
                print("✅ ¡Correcto!")
            else:
                self.letras_falladas.append(letra)
                print("❌ Incorrecto")
            
            input("Presiona Enter para continuar...")
        
        print("\n¡Gracias por jugar!")

if __name__ == "__main__":
    juego = Hangman()
    juego.jugar()