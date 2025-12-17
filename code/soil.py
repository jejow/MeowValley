import pygame
from settings import *

class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        # Kita buat gambar kotak coklat (tanah) secara manual
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill('#5d4037') # Warna Coklat Tanah
        
        # Hiasan sedikit (kotak dalam) biar terlihat seperti galian
        pygame.draw.rect(self.image, '#3e2723', (10, 10, TILE_SIZE-20, TILE_SIZE-20))
        
        self.rect = self.image.get_rect(topleft = pos)

class SoilLayer:
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group() # Grup khusus untuk tanah
        
        # Grid System: Menyimpan data tanah "x,y" agar tidak tumpang tindih
        self.grid = {} 

    def create_soil_patch(self, grid_pos):
        # grid_pos adalah posisi kotak, misal: (5, 10)
        
        # Cek apakah di kotak ini sudah ada tanah? Kalau belum, baru buat.
        if grid_pos not in self.grid:
            self.grid[grid_pos] = 'F' # F artinya Farmable (Bisa ditanami)
            
            # Hitung posisi pixel asli
            pixel_x = grid_pos[0] * TILE_SIZE
            pixel_y = grid_pos[1] * TILE_SIZE
            
            # Buat Sprite Tanah
            SoilTile((pixel_x, pixel_y), [self.all_sprites, self.soil_sprites])
            print(f"Tanah dicangkul di grid: {grid_pos}")

    def hoe_hit(self, target_pos):
        # 1. Konversi posisi target (Pixel) ke Grid (Kotak)
        # Contoh: Posisi pixel 100 dibagi TILE_SIZE (64) = Grid ke-1
        grid_x = int(target_pos[0] // TILE_SIZE)
        grid_y = int(target_pos[1] // TILE_SIZE)
        
        # 2. Perintahkan untuk buat tanah di situ
        self.create_soil_patch((grid_x, grid_y))