import pygame
import sys
import math
import os  
from settings import *
from level import Level
from menu import Menu

class Game:
    def __init__(self):
        pygame.init()

        # ===== WINDOW =====
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Meow Valley')
        self.clock = pygame.time.Clock()

        # ===== STATE =====
        self.game_active = False
        self.level = Level()

        # ===== SETUP PATH PINTAR =====
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        def get_file_path(filename, subfolders):
            # Cek 1: Di folder yang sama dengan main.py
            path1 = os.path.join(current_dir, subfolders, filename)
            if os.path.exists(path1): return path1
            
            # Cek 2: Mundur satu folder, lalu masuk ke folder aset
            root_dir = os.path.dirname(current_dir)
            path2 = os.path.join(root_dir, subfolders, filename)
            if os.path.exists(path2): return path2

            # Cek 3: Struktur folder data/graphics
            path3 = os.path.join(root_dir, 'data', subfolders, filename)
            if os.path.exists(path3): return path3
            
            return None

        # Cari lokasi Font & Gambar
        font_path = get_file_path('LycheeSoda.ttf', 'font')
        bg_path = get_file_path('menu_bg.png', 'graphics')
        cloud_path = get_file_path('cloud_small.png', 'graphics')

        # ===== LOAD FONT =====
        if font_path:
            self.title_font = pygame.font.Font(font_path, 120)
            self.menu_font = pygame.font.Font(font_path, 40)
        else:
            print("PERINGATAN: Font tidak ditemukan. Menggunakan font default.")
            self.title_font = pygame.font.SysFont(None, 100)
            self.menu_font = pygame.font.SysFont(None, 40)

        # ===== LOAD MENU =====
        self.menu = Menu(self.menu_font)

        # ===== LOAD BACKGROUND =====
        self.menu_bg = None
        if bg_path:
            try:
                print(f"Background ditemukan di: {bg_path}")
                img = pygame.image.load(bg_path).convert()
                self.menu_bg = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except Exception as e:
                print(f"Gagal memuat gambar background: {e}")

        # ===== LOAD CLOUD =====
        self.cloud_surf = None
        if cloud_path:
            try:
                img = pygame.image.load(cloud_path).convert_alpha()
                self.cloud_surf = pygame.transform.scale(img, (200, 100))
            except:
                pass

        self.clouds = [
            {'x': SCREEN_WIDTH * 0.5, 'y': 60, 'speed': 30},
            {'x': -220, 'y': 140, 'speed': 20},
        ]

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if not self.game_active:
                    # Input Menu
                    action = self.menu.input(event)
                    
                    if action in ['Start', 'Mulai Game', 'Main']: 
                        self.game_active = True
                    elif action in ['Exit', 'Keluar']:
                        pygame.quit()
                        sys.exit()

            if self.game_active:
                # --- GAMEPLAY ---
                self.screen.fill('black')
                self.level.run(dt)
            else:
                # --- TAMPILAN MENU ---
                
                # 1. Background
                if self.menu_bg:
                    self.screen.blit(self.menu_bg, (0, 0))
                else:
                    self.screen.fill('#87CEEB')

                # 2. Awan Bergerak
                if self.cloud_surf:
                    for cloud in self.clouds:
                        cloud['x'] += cloud['speed'] * dt
                        if cloud['x'] > SCREEN_WIDTH + 200:
                            cloud['x'] = -300
                        self.screen.blit(self.cloud_surf, (cloud['x'], cloud['y']))

                # 3. Judul dengan Efek Melayang
                # Kita pakai waktu saat ini untuk membuat gerakan gelombang
                current_time = pygame.time.get_ticks()
                title_offset = math.sin(current_time * 0.002) * 6
                
                # Bayangan Judul
                title_shadow = self.title_font.render('MEOW VALLEY', True, 'Black')
                rect_shadow = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 4, 200 + title_offset + 4))
                self.screen.blit(title_shadow, rect_shadow)

                # Judul Utama
                title = self.title_font.render('MEOW VALLEY', True, '#FFEB3B')
                rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200 + title_offset))
                self.screen.blit(title, rect)

                # =========================================
                # 4. TOMBOL MENU BERANIMASI (Fitur Baru!)
                # =========================================
                
                # A. Buat permukaan sementara (kaca transparan)
                menu_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                menu_surf.fill((0,0,0,0)) # Pastikan transparan total

                # B. Gambar tombol menu di atas kaca transparan itu
                try:
                    self.menu.draw(menu_surf, dt)
                except TypeError:
                    self.menu.draw(menu_surf)

                # C. Hitung gerakan melayang untuk menu
                # Kita pakai rumus yang sama dengan judul, tapi mungkin sedikit lebih pelan/kecil gerakannya (* 4)
                menu_offset = math.sin(current_time * 0.002) * 4 

                # D. Tempelkan kaca transparan berisi tombol ke layar utama, dengan offset naik-turun
                self.screen.blit(menu_surf, (0, menu_offset))
                # =========================================

            pygame.display.update()

if __name__ == '__main__':
    Game().run()