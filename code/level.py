import pygame
from pytmx.util_pygame import load_pygame
from settings import *
from player import Player
from overlay import Overlay
from soil import SoilLayer # Pastikan soil.py sudah dibuat
import os

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        # ===== GROUPS =====
        self.all_sprites = pygame.sprite.Group()

        # ===== LOAD MAP =====
        base_path = os.path.dirname(os.path.abspath(__file__))
        root_path = os.path.dirname(base_path)
        tmx_path = os.path.join(root_path, 'data', 'map.tmx')
        
        try:
            self.tmx_data = load_pygame(tmx_path)
            self.tile_width = self.tmx_data.tilewidth
            self.tile_height = self.tmx_data.tileheight
            self.map_width = self.tmx_data.width * self.tile_width
            self.map_height = self.tmx_data.height * self.tile_height
        except:
            print("Warning: Map tidak ditemukan, menggunakan ukuran default.")
            self.tmx_data = None
            self.map_width, self.map_height = 2000, 2000
            self.tile_width, self.tile_height = 64, 64

        # ===== SETUP PLAYER =====
        # [UPDATE PENTING] Kita kirim 'self.all_sprites' ke Player
        # Supaya Player otomatis masuk ke grup gambar dan update
        self.player = Player((640, 360), self.all_sprites) 

        # ===== SETUP SOIL (TANAH PERTANIAN) =====
        # [BARU] Layer tanah dibuat di sini
        self.soil_layer = SoilLayer(self.all_sprites)

        # ===== SETUP OVERLAY (UI) =====
        self.overlay = Overlay(self.player)

        # ===== CAMERA =====
        self.offset = pygame.math.Vector2()
        
        # ===== LOGIKA PANEN (Bawaan lama untuk tes H/J) =====
        self.panen_sesi_ini = {'Jagung': 0, 'Tomat': 0, 'Wortel': 0}
        self.import_timer = 0

    def camera_follow(self):
        self.offset.x = self.player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = self.player.rect.centery - SCREEN_HEIGHT / 2
        self.offset.x = max(0, min(self.offset.x, self.map_width - SCREEN_WIDTH))
        self.offset.y = max(0, min(self.offset.y, self.map_height - SCREEN_HEIGHT))

    def draw_tiles(self):
        if not self.tmx_data: return
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'tiles'):
                for x, y, surf in layer.tiles():
                    pos_x = x * self.tile_width - self.offset.x
                    pos_y = y * self.tile_height - self.offset.y
                    self.display_surface.blit(surf, (pos_x, pos_y))

    def reset_panen(self):
        self.panen_sesi_ini = {'Jagung': 0, 'Tomat': 0, 'Wortel': 0}

    def run(self, dt):
        # 1. Update Semua Sprite
        self.all_sprites.update(dt)
        self.camera_follow()

        # 2. LOGIKA ALAT PLAYER (MENCANGKUL)
        # Jika player sedang menekan SPASI (flag use_tool_active menyala)
        if self.player.use_tool_active:
            # Cek apakah sedang pegang Cangkul (hoe)?
            if self.player.selected_tool == 'hoe':
                # Ambil posisi di depan muka kucing
                target_pos = self.player.get_target_pos()
                # Perintahkan SoilLayer untuk mencangkul di posisi itu
                self.soil_layer.hoe_hit(target_pos)

        # 3. LOGIKA PANEN MANUAL (Tombol H/J lama)
        keys = pygame.key.get_pressed()
        if self.import_timer > 0: self.import_timer -= 1
        if self.import_timer == 0:
            if keys[pygame.K_h]: 
                self.panen_sesi_ini['Jagung'] += 1; print("Panen Jagung!"); self.import_timer = 20
            if keys[pygame.K_j]: 
                self.panen_sesi_ini['Tomat'] += 1; print("Panen Tomat!"); self.import_timer = 20

        # --- DRAWING ---
        self.display_surface.fill('#71ddee')
        
        # A. Gambar Map (Paling Bawah)
        self.draw_tiles()

        # B. Gambar Sprite (Kucing + Tanah)
        # Kita urutkan berdasarkan posisi Y agar terlihat 3D (Kucing bisa di depan/belakang tanah)
        sorted_sprites = sorted(self.all_sprites.sprites(), key=lambda sprite: sprite.rect.centery)
        
        for sprite in sorted_sprites:
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

        # C. UI Overlay (Paling Atas)
        self.overlay.display()