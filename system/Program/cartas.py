#!/usr/bin/env python3
"""Juego de Blackjack en consola"""
import random
import os

class Blackjack:
    def __init__(self):
        self.baraja = []
        self.jugador = []
        self.crupier = []
        self.juego_terminado = False
        
    def crear_baraja(self):
        palos = ['♠', '♥', '♦', '♣']
        valores = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        for palo in palos:
            for valor in valores:
                self.baraja.append(f"{valor}{palo}")
        random.shuffle(self.baraja)
    
    def valor_carta(self, carta):
        valor = carta[:-1]
        if valor in ['J', 'Q', 'K']:
            return 10
        elif valor == 'A':
            return 11
        else:
            return int(valor)
    
    def valor_mano(self, mano):
        valor = sum(self.valor_carta(c) for c in mano)
        # Ajustar Ases
        ases = sum(1 for c in mano if c.startswith('A'))
        while valor > 21 and ases > 0:
            valor -= 10
            ases -= 1
        return valor
    
    def mostrar_mano(self, mano, ocultar=False):
        if ocultar:
            return f"[{mano[0]}, ?]"
        return f"[{', '.join(mano)}]"
    
    def jugar(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🎰 BLACKJACK")
        print("=" * 30)
        
        self.crear_baraja()
        
        # Repartir
        self.jugador = [self.baraja.pop(), self.baraja.pop()]
        self.crupier = [self.baraja.pop(), self.baraja.pop()]
        
        while not self.juego_terminado:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("🎰 BLACKJACK")
            print("=" * 30)
            print(f"\nCrupier: {self.mostrar_mano(self.crupier, True)}")
            print(f"Tú: {self.mostrar_mano(self.jugador)} (Total: {self.valor_mano(self.jugador)})")
            
            if self.valor_mano(self.jugador) == 21:
                print("\n🎉 ¡BLACKJACK! ¡Ganaste!")
                self.juego_terminado = True
                break
            
            accion = input("\n¿Qué quieres hacer? [P]edir carta, [Q]uedarte, [R]endirse: ").lower()
            
            if accion == 'p':
                carta = self.baraja.pop()
                self.jugador.append(carta)
                if self.valor_mano(self.jugador) > 21:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("🎰 BLACKJACK")
                    print("=" * 30)
                    print(f"\nCrupier: {self.mostrar_mano(self.crupier)} (Total: {self.valor_mano(self.crupier)})")
                    print(f"Tú: {self.mostrar_mano(self.jugador)} (Total: {self.valor_mano(self.jugador)})")
                    print("\n💀 ¡Te pasaste de 21! Perdiste.")
                    self.juego_terminado = True
                    break
            
            elif accion == 'q':
                # Turno del crupier
                while self.valor_mano(self.crupier) < 17:
                    self.crupier.append(self.baraja.pop())
                
                os.system('cls' if os.name == 'nt' else 'clear')
                print("🎰 BLACKJACK")
                print("=" * 30)
                print(f"\nCrupier: {self.mostrar_mano(self.crupier)} (Total: {self.valor_mano(self.crupier)})")
                print(f"Tú: {self.mostrar_mano(self.jugador)} (Total: {self.valor_mano(self.jugador)})")
                
                valor_jug = self.valor_mano(self.jugador)
                valor_crup = self.valor_mano(self.crupier)
                
                if valor_crup > 21:
                    print("\n🎉 ¡El crupier se pasó! ¡Ganaste!")
                elif valor_jug > valor_crup:
                    print("\n🎉 ¡Ganaste!")
                elif valor_jug < valor_crup:
                    print("\n😔 Perdiste.")
                else:
                    print("\n🤝 Empate.")
                self.juego_terminado = True
                break
            
            elif accion == 'r':
                print("\n🤝 Te has rendido.")
                self.juego_terminado = True
                break
            
            else:
                print("Opción inválida")
        
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    while True:
        game = Blackjack()
        game.jugar()
        if input("¿Jugar otra partida? (s/n): ").lower() != 's':
            break
    print("¡Gracias por jugar!")