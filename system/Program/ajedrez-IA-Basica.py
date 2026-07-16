#!/usr/bin/env python3
"""Ajedrez en consola con IA básica"""
import os
import random

class Chess:
    def __init__(self):
        self.tablero = self._inicializar()
        self.turno = 'blancas'
        self.movimientos = []
        
    def _inicializar(self):
        tablero = [[' ' for _ in range(8)] for _ in range(8)]
        
        # Piezas negras
        piezas_back = ['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜']
        for i, pieza in enumerate(piezas_back):
            tablero[0][i] = pieza
        for i in range(8):
            tablero[1][i] = '♟'
        
        # Piezas blancas (usamos letras para distinguir)
        piezas_white = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        for i, pieza in enumerate(piezas_white):
            tablero[7][i] = pieza
        for i in range(8):
            tablero[6][i] = 'P'
        
        return tablero
    
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("♛ AJEDREZ")
        print("=" * 40)
        print(f"Turno: {self.turno}")
        print("=" * 40)
        print("    a  b  c  d  e  f  g  h")
        print("   ┌──┬──┬──┬──┬──┬──┬──┬──┐")
        for i in range(8):
            print(f" {8-i} │", end="")
            for j in range(8):
                print(f" {self.tablero[i][j]} │", end="")
            print(f" {8-i}")
            if i < 7:
                print("   ├──┼──┼──┼──┼──┼──┼──┼──┤")
        print("   └──┴──┴──┴──┴──┴──┴──┴──┘")
        print("    a  b  c  d  e  f  g  h")
    
    def es_movimiento_valido(self, origen, destino):
        # Verificar que origen tenga una pieza del turno actual
        pieza = self.tablero[origen[0]][origen[1]]
        if self.turno == 'blancas' and pieza not in ['P', 'R', 'N', 'B', 'Q', 'K']:
            return False
        if self.turno == 'negras' and pieza not in ['♟', '♜', '♞', '♝', '♛', '♚']:
            return False
        return True
    
    def mover(self, origen, destino):
        if not self.es_movimiento_valido(origen, destino):
            return False
        
        # Realizar movimiento
        self.tablero[destino[0]][destino[1]] = self.tablero[origen[0]][origen[1]]
        self.tablero[origen[0]][origen[1]] = ' '
        self.turno = 'negras' if self.turno == 'blancas' else 'blancas'
        return True
    
    def ia_mover(self):
        """IA muy simple: mueve una pieza al azar"""
        piezas = []
        for i in range(8):
            for j in range(8):
                if self.tablero[i][j] in ['♟', '♜', '♞', '♝', '♛', '♚']:
                    piezas.append((i, j))
        
        random.shuffle(piezas)
        
        for origen in piezas:
            # Intentar mover en alguna dirección
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    destino = (origen[0] + di, origen[1] + dj)
                    if 0 <= destino[0] < 8 and 0 <= destino[1] < 8:
                        if self.mover(origen, destino):
                            return True
        return False
    
    def jugar(self):
        while True:
            self.display()
            
            if self.turno == 'negras':
                print("\n🤖 IA pensando...")
                if not self.ia_mover():
                    print("💀 No hay movimientos disponibles")
                    break
                continue
            
            try:
                entrada = input("\nMovimiento (ej: e2 e4): ").strip()
                if entrada.lower() == 'quit':
                    break
                
                origen_str, destino_str = entrada.split()
                
                # Convertir coordenadas
                origen = (8 - int(origen_str[1]), ord(origen_str[0]) - ord('a'))
                destino = (8 - int(destino_str[1]), ord(destino_str[0]) - ord('a'))
                
                if not self.mover(origen, destino):
                    print("❌ Movimiento inválido")
                
            except KeyboardInterrupt:
                print("\n¡Juego terminado!")
                break
            except:
                print("❌ Formato inválido. Usa: e2 e4")
        
        print("\n¡Gracias por jugar!")

if __name__ == "__main__":
    juego = Chess()
    juego.jugar()