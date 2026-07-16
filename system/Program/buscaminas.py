#!/usr/bin/env python3
"""Buscaminas en consola"""
import random
import os

class Minesweeper:
    def __init__(self, filas=9, columnas=9, minas=10):
        self.filas = filas
        self.columnas = columnas
        self.minas = minas
        self.tablero = [[' ' for _ in range(columnas)] for _ in range(filas)]
        self.revelado = [[False for _ in range(columnas)] for _ in range(filas)]
        self.minas_pos = set()
        self.game_over = False
        self.banderas = 0
        self._colocar_minas()
        self._calcular_numeros()
    
    def _colocar_minas(self):
        while len(self.minas_pos) < self.minas:
            f = random.randint(0, self.filas-1)
            c = random.randint(0, self.columnas-1)
            self.minas_pos.add((f, c))
            self.tablero[f][c] = '*'
    
    def _calcular_numeros(self):
        for f, c in self.minas_pos:
            for df in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nf, nc = f + df, c + dc
                    if 0 <= nf < self.filas and 0 <= nc < self.columnas:
                        if self.tablero[nf][nc] != '*':
                            if self.tablero[nf][nc] == ' ':
                                self.tablero[nf][nc] = 1
                            else:
                                self.tablero[nf][nc] += 1
    
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("💣 BUSCAMINAS")
        print("=" * 40)
        print(f"Minas: {self.minas} | Banderas: {self.banderas}")
        print("=" * 40)
        
        print("   " + " ".join(f"{i:2}" for i in range(self.columnas)))
        print("  " + "─" * (self.columnas * 3))
        
        for f in range(self.filas):
            print(f"{f:2}│", end="")
            for c in range(self.columnas):
                if self.revelado[f][c]:
                    if (f, c) in self.minas_pos:
                        print(" 💣", end="")
                    else:
                        print(f" {self.tablero[f][c]}", end="")
                else:
                    print(" ■", end="")
            print()
        
        print("=" * 40)
        print("Comandos: [f]ila [c]olumna [a]cción (r=revelar, b=bandera)")
        print("Ejemplo: 3 4 r (revela la casilla 3,4)")
    
    def revelar(self, f, c):
        if self.revelado[f][c]:
            return
        
        self.revelado[f][c] = True
        
        if (f, c) in self.minas_pos:
            self.game_over = True
            return
        
        if self.tablero[f][c] == ' ' or self.tablero[f][c] == 0:
            for df in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nf, nc = f + df, c + dc
                    if 0 <= nf < self.filas and 0 <= nc < self.columnas:
                        if not self.revelado[nf][nc]:
                            self.revelar(nf, nc)
    
    def jugar(self):
        while not self.game_over:
            self.display()
            
            try:
                entrada = input("\nComando: ").strip().split()
                if len(entrada) != 3:
                    print("❌ Formato: fila columna acción")
                    continue
                
                f, c, accion = int(entrada[0]), int(entrada[1]), entrada[2]
                
                if f < 0 or f >= self.filas or c < 0 or c >= self.columnas:
                    print("❌ Posición inválida")
                    continue
                
                if accion == 'r':
                    self.revelar(f, c)
                elif accion == 'b':
                    self.revelado[f][c] = True
                    self.banderas += 1
                else:
                    print("❌ Acción inválida (r=revelar, b=bandera)")
                
                # Verificar victoria
                reveladas = sum(1 for f in range(self.filas) for c in range(self.columnas) if self.revelado[f][c])
                if reveladas == (self.filas * self.columnas - self.minas):
                    print("\n🎉 ¡FELICITACIONES! Has ganado")
                    break
                
            except KeyboardInterrupt:
                print("\n¡Juego terminado!")
                break
            except:
                print("❌ Entrada inválida")
        
        if self.game_over:
            self.display()
            print("\n💥 ¡BOOM! Has perdido")
            input("Presiona Enter para salir...")

if __name__ == "__main__":
    juego = Minesweeper()
    juego.jugar()