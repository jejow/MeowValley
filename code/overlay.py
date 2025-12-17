import pygame
from settings import *
import os

class Overlay:
    def __init__(self, player):
        self.display_surface = pygame.display.get_surface()
        self.player = player

        # ===== SETUP PATH GAMBAR =====
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir) # Mundur ke folder utama
        
        # Lokasi folder overlay
        overlay_path = os.path.join(root_dir, 'graphics', 'overlay')

        # ===== LOAD GAMBAR ALAT (TOOLS) =====
        self.tools_surf = {}
        # Daftar alat yang mungkin ada (sesuaikan dengan nama file kamu nanti)
        tool_names = ['hoe', 'axe', 'water', 'sword'] 
        
        for tool in tool_names:
            path = os.path.join(overlay_path, f'{tool}.png')
            try:
                surf = pygame.image.load(path).convert_alpha()
                self.tools_surf[tool] = pygame.transform.scale(surf, (64, 64)) # Perbesar dikit
            except:
                # Jika gambar tidak ada, biarkan kosong (nanti kita gambar kotak warna)
                self.tools_surf[tool] = None

        # ===== LOAD GAMBAR BENIH (SEEDS) =====
        self.seeds_surf = {}
        seed_names = ['corn', 'tomato']
        
        for seed in seed_names:
            path = os.path.join(overlay_path, f'{seed}.png')
            try:
                surf = pygame.image.load(path).convert_alpha()
                self.seeds_surf[seed] = pygame.transform.scale(surf, (64, 64))
            except:
                self.seeds_surf[seed] = None

    def display(self):
        # 1. TAMPILKAN ALAT (Kiri Bawah)
        tool_surf = self.tools_surf.get(self.player.selected_tool)
        tool_rect = pygame.Rect(20, SCREEN_HEIGHT - 100, 80, 80) # Kotak posisi
        
        # Gambar Kotak Latar (Background alat)
        pygame.draw.rect(self.display_surface, 'white', tool_rect, 0, 10) # Kotak putih
        pygame.draw.rect(self.display_surface, 'black', tool_rect, 4, 10) # Garis tepi hitam
        
        if tool_surf:
            # Gambar icon alat jika ada filenya
            surf_rect = tool_surf.get_rect(center = tool_rect.center)
            self.display_surface.blit(tool_surf, surf_rect)
        else:
            # Jika gambar tidak ada, tulis nama alatnya saja
            font = pygame.font.SysFont(None, 30)
            text = font.render(self.player.selected_tool, True, 'black')
            text_rect = text.get_rect(center = tool_rect.center)
            self.display_surface.blit(text, text_rect)

        # 2. TAMPILKAN BENIH (Kanan Bawah - Jika sedang pegang cangkul/air)
        seed_surf = self.seeds_surf.get(self.player.selected_seed)
        seed_rect = pygame.Rect(120, SCREEN_HEIGHT - 100, 80, 80) # Kotak posisi sebelah alat

        # Gambar Kotak Latar Benih
        pygame.draw.rect(self.display_surface, 'white', seed_rect, 0, 10)
        pygame.draw.rect(self.display_surface, 'black', seed_rect, 4, 10)

        if seed_surf:
            surf_rect = seed_surf.get_rect(center = seed_rect.center)
            self.display_surface.blit(seed_surf, surf_rect)
        else:
            font = pygame.font.SysFont(None, 30)
            text = font.render(self.player.selected_seed, True, 'black')
            text_rect = text.get_rect(center = seed_rect.center)
            self.display_surface.blit(text, text_rect)