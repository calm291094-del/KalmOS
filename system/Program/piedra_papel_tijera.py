#!/usr/bin/env python3
"""Piedra Papel Tijera Lagarto Spock"""
import random
import os

class RPSLS:
    def __init__(self):
        self.opciones = {
            'piedra': {'gana_a': ['tijera', 'lagarto'], 'emoji': '🪨'},
            'papel': {'gana_a': ['piedra', 'spock'], 'emoji': '📄'},
            'tijera': {'gana_a': ['papel', 'lagarto'], 'emoji': '✂️'},
            'lagarto': {'gana_a': ['papel', 'spock'], 'emoji': '🦎'},
            'spock': {'gana_a': ['piedra', 'tijera'], 'emoji': '🖖'}
        }
        self.historial = []
        self.puntaje = {'jugador': 0, 'computadora': 0}
        
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🪨📄✂️🦎🖖 PIEDRA PAPEL TIJERA LAGARTO SPOCK")
        print("=" * 50)
        print(f"Jugador: {self.puntaje['jugador']} | Computadora: {self.puntaje['computadora']}")
        print("=" * 50)
        print("\nOpciones:")
        for i, (nombre, info) in enumerate(self.opciones.items(), 1):
            print(f"  {i}. {info['emoji']} {nombre.capitalize()}")
        print("\n  0. Salir")
        
    def jugar(self):
        while True:
            self.display()
            
            try:
                opcion = input("\nElige una opción (1-5): ").strip()
                if opcion == '0':
                    print("\n¡Gracias por jugar!")
                    break
                
                opcion_num = int(opcion)
                if opcion_num < 1 or opcion_num > 5:
                    print("❌ Opción inválida")
                    input("Presiona Enter...")
                    continue
                
                nombres = list(self.opciones.keys())
                jugador = nombres[opcion_num - 1]
                computadora = random.choice(nombres)
                
                print(f"\nTú: {self.opciones[jugador]['emoji']} {jugador.capitalize()}")
                print(f"Computadora: {self.opciones[computadora]['emoji']} {computadora.capitalize()}")
                
                if jugador == computadora:
                    resultado = "Empate 🤝"
                elif computadora in self.opciones[jugador]['gana_a']:
                    resultado = "¡Ganaste! 🎉"
                    self.puntaje['jugador'] += 1
                else:
                    resultado = "Perdiste 😔"
                    self.puntaje['computadora'] += 1
                
                self.historial.append(f"{jugador} vs {computadora}: {resultado}")
                print(f"\n{resultado}")
                
                input("\nPresiona Enter para continuar...")
                
            except ValueError:
                print("❌ Ingresa un número válido")
                input("Presiona Enter...")
            except KeyboardInterrupt:
                print("\n¡Juego terminado!")
                break
        
        print(f"\n📊 Puntaje final: Jugador {self.puntaje['jugador']} - {self.puntaje['computadora']} Computadora")

if __name__ == "__main__":
    juego = RPSLS()
    juego.jugar()