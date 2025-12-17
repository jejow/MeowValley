import pygame
import sys
import math
import os
import datetime 
import random # [BARU] Untuk simulasi hasil panen
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
        self.history_open = False 
        self.level = Level()

        # ===== SETUP PATH PINTAR =====
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        def get_file_path(filename, subfolders=None):
            if subfolders:
                path1 = os.path.join(current_dir, subfolders, filename)
                root_dir = os.path.dirname(current_dir)
                path2 = os.path.join(root_dir, subfolders, filename)
                path3 = os.path.join(root_dir, 'data', subfolders, filename)
            else:
                path1 = os.path.join(current_dir, filename)
                root_dir = os.path.dirname(current_dir)
                path2 = os.path.join(root_dir, filename)
                path3 = None

            if os.path.exists(path1): return path1
            if os.path.exists(path2): return path2
            if path3 and os.path.exists(path3): return path3
            return os.path.join(current_dir, filename)

        # Cari lokasi Aset
        font_path = get_file_path('LycheeSoda.ttf', 'font')
        bg_path = get_file_path('menu_bg.png', 'graphics')
        cloud_path = get_file_path('cloud_small.png', 'graphics')
        self.history_path = get_file_path('history.txt')

        # ===== LOAD FONT =====
        if font_path and os.path.exists(font_path):
            self.title_font = pygame.font.Font(font_path, 120)
            self.menu_font = pygame.font.Font(font_path, 40)
            self.history_font = pygame.font.Font(font_path, 25) # Ukuran font riwayat disesuaikan
        else:
            self.title_font = pygame.font.SysFont(None, 100)
            self.menu_font = pygame.font.SysFont(None, 40)
            self.history_font = pygame.font.SysFont(None, 25)

        # ===== LOAD MENU =====
        self.menu = Menu(self.menu_font)

        # ===== LOAD BACKGROUND & CLOUD =====
        self.menu_bg = None
        if bg_path and os.path.exists(bg_path):
            try:
                img = pygame.image.load(bg_path).convert()
                self.menu_bg = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except: pass

        self.cloud_surf = None
        if cloud_path and os.path.exists(cloud_path):
            try:
                img = pygame.image.load(cloud_path).convert_alpha()
                self.cloud_surf = pygame.transform.scale(img, (200, 100))
            except: pass

        self.clouds = [
            {'x': SCREEN_WIDTH * 0.5, 'y': 60, 'speed': 30},
            {'x': -220, 'y': 140, 'speed': 20},
        ]

    # [BARU] Fungsi Membuat Laporan Panen ala Stardew Valley
    def create_harvest_report(self):
        # Karena kita belum menyambungkan ke Inventory asli,
        # Kita buat simulasi acak dulu agar kamu bisa lihat hasilnya di menu.
        
        crops = [
            ("Jagung", "🌽"), 
            ("Tomat", "🍅"), 
            ("Wortel", "🥕"), 
            ("Terong", "🍆"), 
            ("Labu", "🎃")
        ]
        
        # Pilih 2 tanaman acak yang "seolah-olah" dipanen sesi ini
        panen_hari_ini = random.sample(crops, 2)
        jumlah1 = random.randint(2, 10)
        jumlah2 = random.randint(1, 5)

        laporan = f"{panen_hari_ini[0][1]} {jumlah1} {panen_hari_ini[0][0]} & {panen_hari_ini[1][1]} {jumlah2} {panen_hari_ini[1][0]}"
        return laporan

    # [UPDATE] Fungsi Simpan Riwayat
    def save_history(self):
        now = datetime.datetime.now()
        date_str = now.strftime("%d/%m %H:%M") # Format: Tanggal/Bulan Jam:Menit
        
        # Ambil laporan panen
        hasil_tani = self.create_harvest_report()
        
        entry = f"[{date_str}] Panen: {hasil_tani}\n"
        
        try:
            with open(self.history_path, 'a', encoding='utf-8') as f: # Pakai utf-8 biar emoji muncul
                f.write(entry)
            print("Riwayat disimpan!")
        except Exception as e:
            print(f"Gagal menyimpan riwayat: {e}")

    # [UPDATE] Fungsi Simpan Riwayat (Ambil Data Asli Level)
    def save_history(self):
        now = datetime.datetime.now()
        date_str = now.strftime("%d/%m %H:%M") 
        
        # 1. AMBIL DATA DARI LEVEL
        tas = self.level.panen_sesi_ini
        
        # 2. Susun Kalimat Laporan dipanen?
        total_panen = tas['Jagung'] + tas['Tomat'] + tas['Wortel']
        
        if total_panen == 0:
            laporan = "Tidak ada hasil panen."
        else:
            item_list = []
            if tas['Jagung'] > 0: item_list.append(f"🌽 {tas['Jagung']} Jagung")
            if tas['Tomat'] > 0: item_list.append(f"🍅 {tas['Tomat']} Tomat")
            if tas['Wortel'] > 0: item_list.append(f"🥕 {tas['Wortel']} Wortel")
            
            laporan = " & ".join(item_list) # Gabungkan dengan tanda '&'

        entry = f"[{date_str}] {laporan}\n"
        
        try:
            with open(self.history_path, 'a', encoding='utf-8') as f:
                f.write(entry)
            print("Riwayat disimpan!")
            
            # [PENTING] Kosongkan tas setelah disimpan
            self.level.reset_panen()
            
        except Exception as e:
            print(f"Gagal menyimpan riwayat: {e}")

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Simpan riwayat jika keluar paksa (tombol X) saat sedang main
                    if self.game_active:
                        self.save_history()
                    pygame.quit()
                    sys.exit()

                # --- INPUT HANDLER ---
                if not self.game_active:
                    
                    if self.history_open:
                        if event.type == pygame.KEYDOWN:
                            if event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN]:
                                self.history_open = False 

                    else:
                        action = self.menu.input(event)
                        
                        if action in ['Start', 'Mulai Game', 'Main']: 
                            self.game_active = True
                        
                        elif action in ['Riwayat Bermain', 'History', 'Riwayat']:
                            self.history_open = True 
                        
                        elif action in ['Exit', 'Keluar']:
                            # [PENTING] Simpan riwayat saat tombol Keluar ditekan
                            # (Asumsinya kamu baru selesai main lalu balik menu dan keluar)
                            # Untuk tes sekarang, ini akan generate data acak.
                            self.save_history() 
                            pygame.quit()
                            sys.exit()
                else:
                    # Jika sedang main dan tekan ESC (opsional, tergantung level.py kamu)
                    if event.type == pygame.KEYDOWN:
                         if event.key == pygame.K_ESCAPE:
                             self.save_history() # Simpan progres sebelum balik menu
                             self.game_active = False

            # --- DRAWING ---
            if self.game_active:
                self.screen.fill('black')
                self.level.run(dt)
            else:
                # Background & Cloud
                if self.menu_bg: self.screen.blit(self.menu_bg, (0, 0))
                else: self.screen.fill('#87CEEB')

                if self.cloud_surf:
                    for cloud in self.clouds:
                        cloud['x'] += cloud['speed'] * dt
                        if cloud['x'] > SCREEN_WIDTH + 200: cloud['x'] = -300
                        self.screen.blit(self.cloud_surf, (cloud['x'], cloud['y']))

                # Judul
                current_time = pygame.time.get_ticks()
                title_offset = math.sin(current_time * 0.002) * 6
                
                title_shadow = self.title_font.render('MEOW VALLEY', True, 'Black')
                rect_shadow = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 4, 200 + title_offset + 4))
                self.screen.blit(title_shadow, rect_shadow)

                title = self.title_font.render('MEOW VALLEY', True, '#FFEB3B')
                rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200 + title_offset))
                self.screen.blit(title, rect)

                # Animasi Menu
                menu_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                menu_surf.fill((0,0,0,0))
                try: self.menu.draw(menu_surf, dt)
                except: self.menu.draw(menu_surf)
                self.screen.blit(menu_surf, (0, math.sin(current_time * 0.002) * 4))

                # --- POP-UP RIWAYAT HASIL TANI ---
                if self.history_open:
                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    overlay.set_alpha(180) 
                    overlay.fill('black')
                    self.screen.blit(overlay, (0,0))

                    # Kotak Panel Lebih Lebar untuk menampung teks panjang
                    panel_w, panel_h = 800, 500
                    panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
                    panel_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    
                    # Desain Kayu (Coklat)
                    pygame.draw.rect(self.screen, '#d4a373', panel_rect, border_radius=15) 
                    pygame.draw.rect(self.screen, '#8c5e3c', panel_rect, 8, border_radius=15) 

                    # Judul Jurnal
                    hist_title = self.menu_font.render("JURNAL HASIL PANEN", True, '#5c190b')
                    hist_title_rect = hist_title.get_rect(center=(SCREEN_WIDTH//2, panel_rect.top + 60))
                    self.screen.blit(hist_title, hist_title_rect)

                    # Garis Pembatas
                    pygame.draw.line(self.screen, '#8c5e3c', (panel_rect.left+50, panel_rect.top+90), (panel_rect.right-50, panel_rect.top+90), 4)

                    # Tampilkan Data
                    history_data = self.get_history_list()
                    start_y = panel_rect.top + 120
                    
                    for i, line in enumerate(history_data):
                        # Ganti warna teks jadi hitam kecoklatan biar estetik
                        text_surf = self.history_font.render(line, True, '#3d2b1f')
                        text_rect = text_surf.get_rect(midleft=(panel_rect.left + 80, start_y + i * 50))
                        self.screen.blit(text_surf, text_rect)
                    
                    close_surf = self.history_font.render("- TEKAN ESC UNTUK TUTUP -", True, '#5c190b')
                    close_rect = close_surf.get_rect(center=(SCREEN_WIDTH//2, panel_rect.bottom - 50))
                    self.screen.blit(close_surf, close_rect)

            pygame.display.update()

if __name__ == '__main__':
    Game().run()