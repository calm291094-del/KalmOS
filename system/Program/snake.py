#!/usr/bin/env python3
"""
🐍 SNAKE GAME v2.0
Juego de serpiente con niveles, puntuación y efectos visuales
"""
import random
import os
import time
import sys
import threading
import json
from pathlib import Path

try:
    import termios
    import tty
    import select
    HAS_TTY = True
except ImportError:
    HAS_TTY = False

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

class SnakeGame:
    def __init__(self):
        self.width = 30
        self.height = 18
        self.snake = [(8, 8), (7, 8), (6, 8)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self._generate_food()
        self.special_food = None
        self.score = 0
        self.high_score = self._load_high_score()
        self.game_over = False
        self.speed = 0.12
        self.level = 1
        self.paused = False
        self.particles = []
        self.combo = 0
        
    def _generate_food(self):
        while True:
            food = (random.randint(1, self.width-2), random.randint(1, self.height-2))
            if food not in self.snake:
                return food
    
    def _load_high_score(self):
        try:
            score_file = Path(__file__).parent / "snake_score.json"
            if score_file.exists():
                with open(score_file, 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
    
    def _save_high_score(self):
        try:
            score_file = Path(__file__).parent / "snake_score.json"
            with open(score_file, 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
    
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Colors.CYAN}{'='*65}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}🐍 SNAKE GAME v2.0{Colors.END}")
        print(f"{Colors.CYAN}{'='*65}{Colors.END}")
        print(f"🎯 Puntuación: {Colors.YELLOW}{self.score}{Colors.END}  |  🏆 Récord: {Colors.BLUE}{self.high_score}{Colors.END}  |  📊 Nivel: {self.level}")
        if self.paused:
            print(f"{Colors.RED}⏸️  PAUSADO{Colors.END}")
        print(f"{Colors.CYAN}{'-'*65}{Colors.END}")
        
        # Dibujar tablero
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width-1 or y == 0 or y == self.height-1:
                    print(f"{Colors.BLUE}█{Colors.END}", end="")
                elif (x, y) == self.food:
                    print(f"{Colors.RED}●{Colors.END}", end="")
                elif self.special_food and (x, y) == self.special_food[0]:
                    print(f"{Colors.YELLOW}★{Colors.END}", end="")
                elif (x, y) in self.snake:
                    if (x, y) == self.snake[0]:
                        print(f"{Colors.GREEN}◄{Colors.END}", end="")
                    else:
                        print(f"{Colors.GREEN}■{Colors.END}", end="")
                else:
                    print(" ", end="")
            print()
        
        print(f"{Colors.CYAN}{'-'*65}{Colors.END}")
        print("Controles: WASD o Flechas | [P] Pausa | [R] Reiniciar | [Q] Salir")
        print(f"{Colors.CYAN}{'='*65}{Colors.END}")
    
    def update(self):
        if self.paused or self.game_over:
            return
        
        self.direction = self.next_direction
        
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Colisión con bordes
        if new_head[0] <= 0 or new_head[0] >= self.width-1 or new_head[1] <= 0 or new_head[1] >= self.height-1:
            self.game_over = True
            return
        
        # Colisión con cuerpo
        if new_head in self.snake[:-1]:
            self.game_over = True
            return
        
        self.snake.insert(0, new_head)
        
        # Comer comida normal
        if new_head == self.food:
            self.score += 10
            self.combo += 1
            self.food = self._generate_food()
            
            # Subir de nivel
            if self.score % 100 == 0:
                self.level += 1
                self.speed = max(0.05, self.speed - 0.01)
                self._spawn_special_food()
                
            # Actualizar récord
            if self.score > self.high_score:
                self.high_score = self.score
                self._save_high_score()
        else:
            self.snake.pop()
            self.combo = max(0, self.combo - 1)
        
        # Comer comida especial
        if self.special_food and new_head == self.special_food[0]:
            self.score += self.special_food[1]
            self.special_food = None
            self._spawn_particles(new_head)
    
    def _spawn_special_food(self):
        """Genera comida especial que da más puntos"""
        self.special_food = (self._generate_food(), 50)
    
    def _spawn_particles(self, pos):
        """Genera partículas para efecto visual"""
        self.particles = []
        for _ in range(10):
            self.particles.append({
                'x': pos[0] + random.randint(-1, 1),
                'y': pos[1] + random.randint(-1, 1),
                'char': random.choice(['✦', '✧', '•', '◦']),
                'life': 10
            })
    
    def _get_key(self):
        if not HAS_TTY:
            try:
                import msvcrt
                if msvcrt.kbhit():
                    return msvcrt.getch().decode('utf-8', errors='ignore')
                return ''
            except:
                return ''
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            if select.select([sys.stdin], [], [], 0)[0]:
                ch = sys.stdin.read(1)
                return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ''
    
    def play(self):
        print(f"{Colors.YELLOW}Presiona cualquier tecla para empezar...{Colors.END}")
        self._get_key()
        
        while not self.game_over:
            self.display()
            
            key = self._get_key()
            if key:
                if key == 'q':
                    self.game_over = True
                    break
                elif key == 'p':
                    self.paused = not self.paused
                    continue
                elif key == 'r':
                    self.__init__()
                    continue
                
                # WASD
                if key == 'w' and self.direction != (0, 1):
                    self.next_direction = (0, -1)
                elif key == 's' and self.direction != (0, -1):
                    self.next_direction = (0, 1)
                elif key == 'a' and self.direction != (1, 0):
                    self.next_direction = (-1, 0)
                elif key == 'd' and self.direction != (-1, 0):
                    self.next_direction = (1, 0)
                
                # Flechas (ANSI)
                elif key == 'A':
                    self.next_direction = (0, -1)
                elif key == 'B':
                    self.next_direction = (0, 1)
                elif key == 'C':
                    self.next_direction = (1, 0)
                elif key == 'D':
                    self.next_direction = (-1, 0)
            
            self.update()
            
            # Efectos de partículas
            if self.particles:
                for p in self.particles[:]:
                    p['life'] -= 1
                    if p['life'] <= 0:
                        self.particles.remove(p)
            
            time.sleep(self.speed)
        
        self.display()
        print(f"\n{Colors.RED}{'='*65}{Colors.END}")
        print(f"{Colors.RED}💀 ¡GAME OVER!{Colors.END}")
        print(f"🎯 Puntuación final: {Colors.YELLOW}{self.score}{Colors.END}")
        if self.score >= self.high_score:
            print(f"{Colors.GREEN}🏆 ¡NUEVO RÉCORD!{Colors.END}")
        print(f"{Colors.RED}{'='*65}{Colors.END}")
        
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()
        
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    game = SnakeGame()
    game.play()