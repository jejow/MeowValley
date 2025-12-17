import pygame
import os
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group): # [UPDATE] Tambah parameter group
        super().__init__(group)     # [UPDATE] Masukkan ke group sprite

        # ===== LOAD ASSETS =====
        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 6

        # Setup Image Awal (Pakai animasi idle pertama)
        if self.animations['idle']:
            self.image = self.animations['idle'][0]
        else:
            # Fallback jika gambar benar-benar tidak ketemu (Kotak Merah)
            self.image = pygame.Surface((32, 64))
            self.image.fill('red')
            
        self.rect = self.image.get_rect(center=pos)

        # ===== MOVEMENT =====
        self.direction = pygame.math.Vector2()
        self.speed = 200 

        # ===== STATUS =====
        self.status = 'idle'
        self.facing_right = True

        # ===== SYSTEM ALAT (TOOLS) =====
        self.tools = ['hoe', 'axe', 'water', 'sword']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        # ===== SYSTEM BENIH (SEEDS) =====
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        # ===== TIMERS =====
        self.timers = {
            'tool_switch': 0,
            'seed_switch': 0,
            'tool_use': 0 # [BARU] Timer durasi pakai alat
        }

        # [BARU] Flag status sedang pakai alat
        self.use_tool_active = False 

    def import_assets(self):
        self.animations = {
            'idle': [],
            'walk': []
        }

        # --- SMART PATH FINDER (GPS PINTAR) ---
        current_dir = os.path.dirname(os.path.abspath(__file__)) 
        
        possible_paths = [
            os.path.join(current_dir, 'graphics', 'player'),
            os.path.join(current_dir, '..', 'graphics', 'player'),
            os.path.join(current_dir, '..', 'graphics', 'character'),
            os.path.join(current_dir, '..', 'data', 'graphics', 'player')
        ]

        player_path = None
        for path in possible_paths:
            if os.path.exists(path):
                player_path = path
                print(f"DEBUG: Gambar Player ditemukan di: {player_path}")
                break
        
        if not player_path:
            print("ERROR FATAL: Folder gambar player tidak ditemukan!")
            dummy = pygame.Surface((32, 64))
            dummy.fill('red')
            self.animations['idle'].append(dummy)
            self.animations['walk'].append(dummy)
            return

        # LOAD GAMBAR
        try:
            path = os.path.join(player_path, '0.png')
            if os.path.exists(path):
                self.animations['idle'].append(pygame.image.load(path).convert_alpha())
        except: pass

        for i in range(1, 4):
            path = os.path.join(player_path, f'{i}.png')
            if os.path.exists(path):
                try:
                    self.animations['walk'].append(pygame.image.load(path).convert_alpha())
                except: pass
            
        if not self.animations['walk']:
            self.animations['walk'] = self.animations['idle']

    def update_timers(self, dt):
        for timer in self.timers:
            if self.timers[timer] > 0:
                self.timers[timer] -= dt
        
        # [BARU] Reset status pakai alat jika timer habis
        if self.timers['tool_use'] <= 0:
            self.use_tool_active = False

    # [BARU] HITUNG POSISI TARUH TANAH/CANGKUL
    def get_target_pos(self):
        offset = pygame.math.Vector2()
        
        if self.status == 'idle':
            if self.facing_right: offset.x = 1
            else: offset.x = -1
        else:
            if self.direction.x != 0: offset.x = self.direction.x
            if self.direction.y != 0: offset.y = self.direction.y

        # Target = Posisi Player + (Arah * Jarak 40px)
        return self.rect.center + offset * 40

    def input(self):
        keys = pygame.key.get_pressed()
        
        # [UPDATE] Hanya bisa gerak jika TIDAK sedang pakai alat
        if not self.use_tool_active:
            self.direction.update(0, 0)

            # MOVEMENT
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.facing_right = True
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.facing_right = False

            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.direction.y = 1
            elif keys[pygame.K_w] or keys[pygame.K_UP]:
                self.direction.y = -1

            # SWITCH ALAT (Q)
            if keys[pygame.K_q] and self.timers['tool_switch'] <= 0:
                self.tool_index = (self.tool_index + 1) % len(self.tools)
                self.selected_tool = self.tools[self.tool_index]
                self.timers['tool_switch'] = 0.3
                print(f"Alat: {self.selected_tool}")

            # SWITCH BENIH (E)
            if keys[pygame.K_e] and self.timers['seed_switch'] <= 0:
                self.seed_index = (self.seed_index + 1) % len(self.seeds)
                self.selected_seed = self.seeds[self.seed_index]
                self.timers['seed_switch'] = 0.3
                print(f"Benih: {self.selected_seed}")

            # [BARU] PAKAI ALAT / MENCANGKUL (SPASI)
            if keys[pygame.K_SPACE] and self.timers['tool_use'] <= 0:
                self.timers['tool_use'] = 0.5 # Durasi animasi mencangkul
                self.use_tool_active = True   # Kunci gerakan
                self.direction = pygame.math.Vector2() # Stop jalan
                self.frame_index = 0 # Reset animasi

        # STATUS UPDATE
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
            self.status = 'walk'
        else:
            self.status = 'idle'

    def move(self, dt):
        self.rect.center += self.direction * self.speed * dt

    def animate(self, dt):
        animation = self.animations[self.status]
        if not animation: return

        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]

        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)

        self.image = image

    def update(self, dt):
        self.input()
        self.update_timers(dt)
        self.move(dt)
        self.animate(dt)