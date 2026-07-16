#!/usr/bin/env python3
"""Juego de Ajedrez en consola - Versión simplificada"""
import sys
import os

class Chess:
    def __init__(self):
        self.board = self._init_board()
        self.turn = 'white'
        self.selected = None
        self.move_history = []
        
    def _init_board(self):
        board = [[' ' for _ in range(8)] for _ in range(8)]
        pieces = {
            'back': ['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜'],
            'front': ['♟' for _ in range(8)]
        }
        # Negras
        for i, piece in enumerate(pieces['back']):
            board[0][i] = piece
        for i in range(8):
            board[1][i] = '♟'
        # Blancas
        for i, piece in enumerate(pieces['back']):
            board[7][i] = piece.lower()
        for i in range(8):
            board[6][i] = '♙'
        return board
    
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("    a  b  c  d  e  f  g  h")
        print("   ┌──┬──┬──┬──┬──┬──┬──┬──┐")
        for i, row in enumerate(self.board):
            print(f" {8-i} │", end="")
            for cell in row:
                print(f" {cell} │", end="")
            print(f" {8-i}")
            if i < 7:
                print("   ├──┼──┼──┼──┼──┼──┼──┼──┤")
        print("   └──┴──┴──┴──┴──┴──┴──┴──┘")
        print("    a  b  c  d  e  f  g  h")
        print(f"\nTurno: {self.turn}")
    
    def play(self):
        while True:
            self.display()
            try:
                move = input(f"\n{self.turn} - Movimiento (ej: e2e4): ").strip()
                if move.lower() == 'quit':
                    print("¡Gracias por jugar!")
                    break
                if len(move) != 4:
                    print("Formato inválido. Usa: columna1filacolumna2fila2")
                    continue
                
                col1 = ord(move[0]) - ord('a')
                row1 = 8 - int(move[1])
                col2 = ord(move[2]) - ord('a')
                row2 = 8 - int(move[3])
                
                if not (0 <= col1 < 8 and 0 <= row1 < 8 and 0 <= col2 < 8 and 0 <= row2 < 8):
                    print("Coordenadas fuera del tablero")
                    continue
                
                piece = self.board[row1][col1]
                if piece == ' ':
                    print("No hay pieza en esa posición")
                    continue
                
                if self.turn == 'white' and piece.islower():
                    print("No es tu pieza")
                    continue
                if self.turn == 'black' and piece.isupper():
                    print("No es tu pieza")
                    continue
                
                # Realizar movimiento
                self.board[row2][col2] = piece
                self.board[row1][col1] = ' '
                
                # Cambiar turno
                self.turn = 'black' if self.turn == 'white' else 'white'
                self.move_history.append(f"{move} ({piece})")
                
            except KeyboardInterrupt:
                print("\n¡Juego terminado!")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    game = Chess()
    game.play()