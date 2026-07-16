#!/usr/bin/env python3
"""Tres en Raya en consola"""
import os

class TicTacToe:
    def __init__(self):
        self.tablero = [[' ' for _ in range(3)] for _ in range(3)]
        self.turno = 'X'
        
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🎮 TRES EN RAYA")
        print("=" * 20)
        print("\n   1   2   3")
        print("  ┌───┬───┬───┐")
        for i in range(3):
            print(f"{i+1} │ {self.tablero[i][0]} │ {self.tablero[i][1]} │ {self.tablero[i][2]} │")
            if i < 2:
                print("  ├───┼───┼───┤")
        print("  └───┴───┴───┘")
        print(f"\nTurno: {self.turno}")
    
    def verificar_ganador(self):
        # Filas
        for fila in self.tablero:
            if fila[0] == fila[1] == fila[2] != ' ':
                return fila[0]
        # Columnas
        for col in range(3):
            if self.tablero[0][col] == self.tablero[1][col] == self.tablero[2][col] != ' ':
                return self.tablero[0][col]
        # Diagonales
        if self.tablero[0][0] == self.tablero[1][1] == self.tablero[2][2] != ' ':
            return self.tablero[0][0]
        if self.tablero[0][2] == self.tablero[1][1] == self.tablero[2][0] != ' ':
            return self.tablero[0][2]
        return None
    
    def tablero_lleno(self):
        for fila in self.tablero:
            for celda in fila:
                if celda == ' ':
                    return False
        return True
    
    def jugar(self):
        while True:
            self.display()
            
            if self.verificar_ganador():
                ganador = self.verificar_ganador()
                print(f"\n🎉 ¡{ganador} ha ganado!")
                break
            
            if self.tablero_lleno():
                print("\n🤝 ¡Empate!")
                break
            
            try:
                movimiento = input(f"\n{self.turno}, ingresa fila,columna (ej: 1,2): ")
                if movimiento.lower() == 'quit':
                    print("¡Hasta luego!")
                    break
                
                fila, col = map(int, movimiento.split(','))
                fila -= 1
                col -= 1
                
                if not (0 <= fila < 3 and 0 <= col < 3):
                    print("Posición inválida")
                    continue
                
                if self.tablero[fila][col] != ' ':
                    print("Casilla ocupada")
                    continue
                
                self.tablero[fila][col] = self.turno
                self.turno = 'O' if self.turno == 'X' else 'X'
                
            except KeyboardInterrupt:
                print("\n¡Juego terminado!")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n¡Gracias por jugar!")

if __name__ == "__main__":
    juego = TicTacToe()
    juego.jugar()