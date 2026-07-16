#!/usr/bin/env python3
"""Sokoban - Puzzle de almacenes"""
import os

class Sokoban:
    def __init__(self):
        # Nivel simple
        self.mapa = [
            "##########",
            "#        #",
            "#   $    #",
            "#   .    #",
            "#   @    #",
            "#        #",
            "#        #",
            "##########"
        ]
        self.jugador = (4, 4)
        self.cajas = [(2, 4)]
        self.objetivos = [(3, 4)]
        self.pasos = 0
    
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("📦 SOKOBAN")
        print("=" * 40)
        print(f"Pasos: {self.pasos} | Cajas: {len(self.cajas)} | Objetivos: {len(self.objetivos)}")
        print("=" * 40)
        print("Controles: WASD | Q=Salir")
        print("-" * 40)
        
        for y, fila in enumerate(self.mapa):
            for x, char in enumerate(fila):
                if (y, x) == self.jugador:
                    print("@", end="")
                elif (y, x) in self.cajas:
                    print("$", end="")
                elif (y, x) in self.objetivos:
                    print(".", end="")
                else:
                    print(char, end="")
            print()
    
    def mover(self, dx, dy):
        ny, nx = self.jugador[0] + dy, self.jugador[1] + dx
        
        # Verificar si hay caja
        if (ny, nx) in self.cajas:
            ny2, nx2 = ny + dy, nx + dx
            # Verificar que la nueva posición sea válida
            if self.mapa[ny2][nx2] != '#':
                # Mover caja
                self.cajas.remove((ny, nx))
                self.cajas.append((ny2, nx2))
                # Mover jugador
                self.jugador = (ny, nx)
                self.pasos += 1
                return
        
        # Movimiento normal
        if self.mapa[ny][nx] != '#':
            self.jugador = (ny, nx)
            self.pasos += 1
    
    def verificar_victoria(self):
        for objetivo in self.objetivos:
            if objetivo not in self.cajas:
                return False
        return True
    
    def jugar(self):
        while True:
            self.display()
            
            if self.verificar_victoria():
                print("\n🎉 ¡FELICITACIONES! Has completado el nivel")
                print(f"Pasos: {self.pasos}")
                input("Presiona Enter para salir...")
                break
            
            tecla = input("\nMovimiento: ").lower()
            
            if tecla == 'q':
                break
            elif tecla == 'w':
                self.mover(0, -1)
            elif tecla == 's':
                self.mover(0, 1)
            elif tecla == 'a':
                self.mover(-1, 0)
            elif tecla == 'd':
                self.mover(1, 0)

if __name__ == "__main__":
    juego = Sokoban()
    juego.jugar()