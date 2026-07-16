#!/usr/bin/env python3
"""Juego Snake en consola"""
import random
import os
import time
import threading
import sys
import termios
import tty
import select

class SnakeGame:
    def __init__(self):
        self.width = 20
        self.height = 15
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.direction = (1, 0)
        self.food = self._generate_food()
        self.score = 0
        self.game_over = False
        self.speed = 0.15
        self.paused = False
        
    def _generate_food(self):
        while True:
            food = (random.randint(0, self.width-1), random.randint(0, self.height-1))
            if food not in self.snake:
                return food
    
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🐍 SNAKE GAME")
        print("=" * 50)
        print(f"Puntuación: {self.score}")
        if self.paused:
            print("⏸️ PAUSADO")
        print("=" * 50)
        
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) == self.food:
                    print("🍎", end="")
                elif (x, y) in self.snake:
                    if (x, y) == self.snake[0]:
                        print("🐍", end="")
                    else:
                        print("⬛", end="")
                else:
                    print("⬜", end="")
            print()
        
        print("=" * 50)
        print("Controles: WASD o Flechas | [Q] Salir | [P] Pausa")
    
    def update(self):
        if self.paused or self.game_over:
            return
            
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        if new_head[0] < 0 or new_head[0] >= self.width or new_head[1] < 0 or new_head[1] >= self.height:
            self.game_over = True
            return
        
        if new_head in self.snake[:-1]:
            self.game_over = True
            return
        
        self.snake.insert(0, new_head)
        
        if new_head == self.food:
            self.score += 10
            self.food = self._generate_food()
            self.speed = max(0.05, self.speed - 0.005)
        else:
            self.snake.pop()
    
    def getch(self):
        """Obtiene una tecla sin esperar Enter"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
    def play(self):
        print("Presiona cualquier tecla para empezar...")
        self.getch()
        
        while not self.game_over:
            self.display()
            
            # Verificar entrada sin bloquear
            if select.select([sys.stdin], [], [], 0)[0]:
                key = self.getch()
                
                if key == 'q':
                    self.game_over = True
                    break
                elif key == 'p':
                    self.paused = not self.paused
                    continue
                
                # WASD
                if key == 'w' and self.direction != (0, 1):
                    self.direction = (0, -1)
                elif key == 's' and self.direction != (0, -1):
                    self.direction = (0, 1)
                elif key == 'a' and self.direction != (1, 0):
                    self.direction = (-1, 0)
                elif key == 'd' and self.direction != (-1, 0):
                    self.direction = (1, 0)
                
                # Flechas
                elif key == 'A':  # Flecha arriba
                    self.direction = (0, -1)
                elif key == 'B':  # Flecha abajo
                    self.direction = (0, 1)
                elif key == 'C':  # Flecha derecha
                    self.direction = (1, 0)
                elif key == 'D':  # Flecha izquierda
                    self.direction = (-1, 0)
            
            self.update()
            time.sleep(self.speed)
        
        print("\n" + "=" * 50)
        print(f"🎮 ¡GAME OVER! Puntuación: {self.score}")
        print("=" * 50)
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    game = SnakeGame()
    game.play()