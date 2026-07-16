#!/usr/bin/env python3
"""Reproductor de Música en consola"""
import os
import time
import threading
import glob
from pathlib import Path

class MusicPlayer:
    def __init__(self):
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.volume = 50
        self.audio_files = []
        
    def scan_music(self, path=None):
        """Escanea archivos de audio en el directorio"""
        if not path:
            path = str(Path.home() / "Music")
        
        extensions = ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac']
        self.audio_files = []
        
        for ext in extensions:
            self.audio_files.extend(glob.glob(f"{path}/**/*{ext}", recursive=True))
        
        return len(self.audio_files)
    
    def play(self, file_path=None):
        """Reproduce un archivo de audio"""
        if file_path:
            self.playlist = [file_path]
            self.current_index = 0
        elif not self.playlist:
            if self.audio_files:
                self.playlist = self.audio_files
                self.current_index = 0
            else:
                print("❌ No hay archivos de audio")
                return
        
        self.is_playing = True
        print(f"▶️ Reproduciendo: {os.path.basename(self.playlist[self.current_index])}")
        print(f"📁 {self.playlist[self.current_index]}")
        
        try:
            # Intentar usar pygame para reproducción
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(self.playlist[self.current_index])
                pygame.mixer.music.set_volume(self.volume / 100)
                pygame.mixer.music.play()
                
                # Mostrar controles
                self._show_controls()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.5)
                
                # Siguiente canción automáticamente
                if self.is_playing:
                    self.next()
                    
            except ImportError:
                # Fallback: usar sistema operativo
                import platform
                if platform.system() == "Windows":
                    os.system(f'start "" "{self.playlist[self.current_index]}"')
                else:
                    os.system(f'xdg-open "{self.playlist[self.current_index]}"')
                
        except Exception as e:
            print(f"❌ Error reproduciendo: {e}")
    
    def _show_controls(self):
        """Muestra controles del reproductor"""
        print("\n" + "=" * 40)
        print("🎵 CONTROLES:")
        print("  [Espacio] Pausa/Reanudar")
        print("  [N] Siguiente")
        print("  [P] Anterior")
        print("  [+/-] Volumen")
        print("  [Q] Salir")
        print("=" * 40)
    
    def pause(self):
        """Pausa/Reanuda la reproducción"""
        try:
            import pygame
            if pygame.mixer.music.get_busy():
                if pygame.mixer.music.get_endevent():
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.pause()
        except:
            pass
    
    def next(self):
        """Siguiente canción"""
        if self.playlist and self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self.play(self.playlist[self.current_index])
        else:
            self.is_playing = False
            print("⏹️ Fin de la lista de reproducción")
    
    def previous(self):
        """Canción anterior"""
        if self.playlist and self.current_index > 0:
            self.current_index -= 1
            self.play(self.playlist[self.current_index])
    
    def volume_up(self):
        """Sube el volumen"""
        self.volume = min(100, self.volume + 10)
        try:
            import pygame
            pygame.mixer.music.set_volume(self.volume / 100)
        except:
            pass
        print(f"🔊 Volumen: {self.volume}%")
    
    def volume_down(self):
        """Baja el volumen"""
        self.volume = max(0, self.volume - 10)
        try:
            import pygame
            pygame.mixer.music.set_volume(self.volume / 100)
        except:
            pass
        print(f"🔊 Volumen: {self.volume}%")
    
    def menu(self):
        """Menú principal del reproductor"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("🎵 REPRODUCTOR DE MÚSICA")
            print("=" * 40)
            print(f"📂 Archivos encontrados: {len(self.audio_files)}")
            print(f"🎵 Reproduciendo: {os.path.basename(self.playlist[self.current_index]) if self.playlist else 'Ninguno'}")
            print(f"🔊 Volumen: {self.volume}%")
            print("\n1. Escanear música")
            print("2. Reproducir archivo")
            print("3. Reproducir lista completa")
            print("4. Siguiente")
            print("5. Anterior")
            print("6. Pausa/Reanudar")
            print("7. Subir volumen")
            print("8. Bajar volumen")
            print("0. Salir")
            print("=" * 40)
            
            opcion = input("Opción: ").strip()
            
            if opcion == '0':
                break
            elif opcion == '1':
                path = input("Ruta de música (Enter para ~/Music): ").strip()
                if not path:
                    path = str(Path.home() / "Music")
                count = self.scan_music(path)
                print(f"✅ {count} archivos encontrados")
                input("Presiona Enter...")
            elif opcion == '2':
                path = input("Ruta del archivo: ").strip()
                if path and os.path.exists(path):
                    self.play(path)
                else:
                    print("❌ Archivo no encontrado")
                    input("Presiona Enter...")
            elif opcion == '3':
                if self.audio_files:
                    self.playlist = self.audio_files
                    self.current_index = 0
                    self.play()
                else:
                    print("❌ No hay archivos de música")
                    input("Presiona Enter...")
            elif opcion == '4':
                self.next()
            elif opcion == '5':
                self.previous()
            elif opcion == '6':
                self.pause()
            elif opcion == '7':
                self.volume_up()
            elif opcion == '8':
                self.volume_down()
            else:
                print("❌ Opción inválida")
                input("Presiona Enter...")

if __name__ == "__main__":
    player = MusicPlayer()
    # Escanear automáticamente
    player.scan_music()
    player.menu()