#!/usr/bin/env python3
"""
🎰 BLACKJACK CASINO v2.0
Juego de Blackjack con apuestas, estadísticas y estrategias
"""
import random
import os
import json
from pathlib import Path
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

class Blackjack:
    def __init__(self):
        self.baraja = []
        self.jugador = []
        self.crupier = []
        self.juego_terminado = False
        self.apuesta = 0
        self.fichas = 1000
        self.historial = []
        self.estadisticas = self._cargar_estadisticas()
        self.partidas_jugadas = 0
        self.ganadas = 0
        self.perdidas = 0
        
    def _cargar_estadisticas(self):
        try:
            stats_file = Path(__file__).parent / "blackjack_stats.json"
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {'partidas': 0, 'ganadas': 0, 'perdidas': 0, 'max_fichas': 1000}
    
    def _guardar_estadisticas(self):
        try:
            stats_file = Path(__file__).parent / "blackjack_stats.json"
            with open(stats_file, 'w') as f:
                json.dump(self.estadisticas, f, indent=2)
        except:
            pass
    
    def crear_baraja(self):
        palos = ['♠', '♥', '♦', '♣']
        valores = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        self.baraja = []
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
        return f"[{', '.join(mano)}] ({self.valor_mano(mano)})"
    
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}🎰 BLACKJACK CASINO{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"💰 Fichas: {Colors.YELLOW}${self.fichas}{Colors.END}")
        print(f"📊 Partidas: {self.estadisticas['partidas']}  |  Ganadas: {self.estadisticas['ganadas']}  |  Perdidas: {self.estadisticas['perdidas']}")
        if self.apuesta > 0:
            print(f"🎲 Apuesta: ${self.apuesta}")
        print(f"{Colors.CYAN}{'-'*60}{Colors.END}")
    
    def jugar(self):
        while self.fichas > 0:
            self.display()
            
            # Mostrar historial de apuestas anteriores
            if self.historial:
                print(f"\n{Colors.BLUE}📋 Últimas jugadas:{Colors.END}")
                for h in self.historial[-3:]:
                    print(f"  {h}")
            
            try:
                apuesta_str = input(f"\n💰 Apuesta (mín 10, máx {self.fichas}): $")
                self.apuesta = int(apuesta_str)
                if self.apuesta < 10:
                    print("❌ Apuesta mínima: $10")
                    continue
                if self.apuesta > self.fichas:
                    print(f"❌ No tienes suficientes fichas. Máximo: ${self.fichas}")
                    continue
            except:
                print("❌ Ingresa un número válido")
                continue
            
            self.crear_baraja()
            self.jugador = [self.baraja.pop(), self.baraja.pop()]
            self.crupier = [self.baraja.pop(), self.baraja.pop()]
            self.juego_terminado = False
            self.partidas_jugadas += 1
            
            # Blackjack inicial
            if self.valor_mano(self.jugador) == 21:
                self.display()
                print(f"\n{Colors.GREEN}🎉 ¡BLACKJACK! ¡Ganaste!{Colors.END}")
                self.fichas += int(self.apuesta * 1.5)
                self.ganadas += 1
                self.historial.append(f"🎉 Blackjack! +${int(self.apuesta * 1.5)}")
                input("Presiona Enter...")
                continue
            
            while not self.juego_terminado:
                self.display()
                print(f"\nCrupier: {self.mostrar_mano(self.crupier, True)}")
                print(f"Tú: {self.mostrar_mano(self.jugador)}")
                print(f"\n{Colors.YELLOW}[P]edir  [Q]uedarse  [D]oblar  [R]endirse{Colors.END}")
                
                accion = input("👉 ").lower()
                
                if accion == 'p':
                    carta = self.baraja.pop()
                    self.jugador.append(carta)
                    if self.valor_mano(self.jugador) > 21:
                        self.display()
                        print(f"\n{Colors.RED}💀 ¡Te pasaste! Perdiste.{Colors.END}")
                        self.fichas -= self.apuesta
                        self.perdidas += 1
                        self.historial.append(f"💀 Perdiste -${self.apuesta}")
                        self.juego_terminado = True
                        break
                
                elif accion == 'q':
                    while self.valor_mano(self.crupier) < 17:
                        self.crupier.append(self.baraja.pop())
                    
                    self.display()
                    print(f"\nCrupier: {self.mostrar_mano(self.crupier)}")
                    print(f"Tú: {self.mostrar_mano(self.jugador)}")
                    
                    valor_jug = self.valor_mano(self.jugador)
                    valor_crup = self.valor_mano(self.crupier)
                    
                    if valor_crup > 21:
                        print(f"\n{Colors.GREEN}🎉 ¡El crupier se pasó! ¡Ganaste!{Colors.END}")
                        self.fichas += self.apuesta
                        self.ganadas += 1
                        self.historial.append(f"🎉 Ganaste +${self.apuesta}")
                    elif valor_jug > valor_crup:
                        print(f"\n{Colors.GREEN}🎉 ¡Ganaste!{Colors.END}")
                        self.fichas += self.apuesta
                        self.ganadas += 1
                        self.historial.append(f"🎉 Ganaste +${self.apuesta}")
                    elif valor_jug < valor_crup:
                        print(f"\n{Colors.RED}😔 Perdiste.{Colors.END}")
                        self.fichas -= self.apuesta
                        self.perdidas += 1
                        self.historial.append(f"💀 Perdiste -${self.apuesta}")
                    else:
                        print(f"\n{Colors.YELLOW}🤝 Empate. Recuperas tu apuesta.{Colors.END}")
                    self.juego_terminado = True
                    break
                
                elif accion == 'd':
                    if len(self.jugador) == 2 and self.fichas >= self.apuesta * 2:
                        self.fichas -= self.apuesta
                        self.apuesta *= 2
                        self.jugador.append(self.baraja.pop())
                        if self.valor_mano(self.jugador) > 21:
                            self.display()
                            print(f"\n{Colors.RED}💀 ¡Te pasaste! Perdiste.{Colors.END}")
                            self.perdidas += 1
                            self.historial.append(f"💀 Perdiste -${self.apuesta}")
                        else:
                            # Forzar quedarse
                            while self.valor_mano(self.crupier) < 17:
                                self.crupier.append(self.baraja.pop())
                            self.display()
                            valor_jug = self.valor_mano(self.jugador)
                            valor_crup = self.valor_mano(self.crupier)
                            if valor_crup > 21 or valor_jug > valor_crup:
                                print(f"\n{Colors.GREEN}🎉 ¡Ganaste!{Colors.END}")
                                self.fichas += self.apuesta * 2
                                self.ganadas += 1
                                self.historial.append(f"🎉 Ganaste +${self.apuesta*2}")
                            elif valor_jug < valor_crup:
                                print(f"\n{Colors.RED}😔 Perdiste.{Colors.END}")
                                self.perdidas += 1
                                self.historial.append(f"💀 Perdiste -${self.apuesta}")
                            else:
                                print(f"\n{Colors.YELLOW}🤝 Empate.{Colors.END}")
                        self.juego_terminado = True
                    else:
                        print("❌ No puedes doblar en esta situación")
                
                elif accion == 'r':
                    print(f"\n{Colors.YELLOW}🤝 Te has rendido. Pierdes la mitad de la apuesta.{Colors.END}")
                    self.fichas -= self.apuesta // 2
                    self.perdidas += 1
                    self.historial.append(f"🏳️ Rendido -${self.apuesta//2}")
                    self.juego_terminado = True
            
            # Actualizar estadísticas
            self.estadisticas['partidas'] += 1
            self.estadisticas['ganadas'] += 1 if self.ganadas > 0 else 0
            self.estadisticas['perdidas'] += 1 if self.perdidas > 0 else 0
            if self.fichas > self.estadisticas.get('max_fichas', 0):
                self.estadisticas['max_fichas'] = self.fichas
            self._guardar_estadisticas()
            
            input("\nPresiona Enter para continuar...")
        
        print(f"\n{Colors.RED}💔 ¡Te quedaste sin fichas!{Colors.END}")
        print(f"📊 Partidas jugadas: {self.estadisticas['partidas']}")
        print(f"🎯 Máximo de fichas alcanzado: ${self.estadisticas.get('max_fichas', 0)}")
        print("¡Gracias por jugar!")

if __name__ == "__main__":
    juego = Blackjack()
    juego.jugar()