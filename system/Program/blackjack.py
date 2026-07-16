#!/usr/bin/env python3
"""Blackjack (21) en consola"""
import random
import os

class Blackjack:
    def __init__(self):
        self.baraja = []
        self.jugador = []
        self.crupier = []
        self.juego_terminado = False
        self.apuesta = 0
        self.fichas = 100
        
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
        while self.fichas > 0:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("🎰 BLACKJACK")
            print("=" * 40)
            print(f"Fichas: ${self.fichas}")
            print("=" * 40)
            
            try:
                self.apuesta = int(input("Apuesta: $"))
                if self.apuesta > self.fichas:
                    print("❌ No tienes suficientes fichas")
                    continue
            except:
                continue
            
            self.crear_baraja()
            self.jugador = [self.baraja.pop(), self.baraja.pop()]
            self.crupier = [self.baraja.pop(), self.baraja.pop()]
            self.juego_terminado = False
            
            while not self.juego_terminado:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("🎰 BLACKJACK")
                print("=" * 40)
                print(f"Fichas: ${self.fichas}")
                print(f"Apuesta: ${self.apuesta}")
                print("-" * 40)
                print(f"Crupier: {self.mostrar_mano(self.crupier, True)}")
                print(f"Tú: {self.mostrar_mano(self.jugador)} (Total: {self.valor_mano(self.jugador)})")
                print("-" * 40)
                
                if self.valor_mano(self.jugador) == 21:
                    print("\n🎉 ¡BLACKJACK! ¡Ganaste!")
                    self.fichas += int(self.apuesta * 1.5)
                    self.juego_terminado = True
                    break
                
                accion = input("\n[P]edir, [Q]uedarse, [R]endirse: ").lower()
                
                if accion == 'p':
                    carta = self.baraja.pop()
                    self.jugador.append(carta)
                    if self.valor_mano(self.jugador) > 21:
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print("🎰 BLACKJACK")
                        print("=" * 40)
                        print(f"Crupier: {self.mostrar_mano(self.crupier)} (Total: {self.valor_mano(self.crupier)})")
                        print(f"Tú: {self.mostrar_mano(self.jugador)} (Total: {self.valor_mano(self.jugador)})")
                        print("\n💀 ¡Te pasaste! Perdiste.")
                        self.fichas -= self.apuesta
                        self.juego_terminado = True
                        break
                
                elif accion == 'q':
                    while self.valor_mano(self.crupier) < 17:
                        self.crupier.append(self.baraja.pop())
                    
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("🎰 BLACKJACK")
                    print("=" * 40)
                    print(f"Crupier: {self.mostrar_mano(self.crupier)} (Total: {self.valor_mano(self.crupier)})")
                    print(f"Tú: {self.mostrar_mano(self.jugador)} (Total: {self.valor_mano(self.jugador)})")
                    
                    valor_jug = self.valor_mano(self.jugador)
                    valor_crup = self.valor_mano(self.crupier)
                    
                    if valor_crup > 21:
                        print("\n🎉 ¡El crupier se pasó! ¡Ganaste!")
                        self.fichas += self.apuesta
                    elif valor_jug > valor_crup:
                        print("\n🎉 ¡Ganaste!")
                        self.fichas += self.apuesta
                    elif valor_jug < valor_crup:
                        print("\n😔 Perdiste.")
                        self.fichas -= self.apuesta
                    else:
                        print("\n🤝 Empate.")
                    self.juego_terminado = True
                    break
                
                elif accion == 'r':
                    print("\n🤝 Te has rendido.")
                    self.fichas -= self.apuesta // 2
                    self.juego_terminado = True
                    break
            
            input("\nPresiona Enter para continuar...")
        
        print("\n💔 ¡Te quedaste sin fichas!")
        print("¡Gracias por jugar!")

if __name__ == "__main__":
    juego = Blackjack()
    juego.jugar()