# Meow Valley

Meow Valley adalah game **farming / life-sim** sederhana berbasis **Python + Pygame**, dengan map dari **Tiled (.tmx)**. Pemain bisa bergerak di dunia, bercocok tanam, menyiram, memanen, menebang pohon, jual/beli di trader, serta menyimpan permainan menggunakan slot.

## Fitur

- Start menu: **Mulai**, **Load**, **Pengaturan**, **Keluar**
- Pengaturan: **Resolusi**, **Volume Music**, **Volume SFX** (tersimpan global)
- Gameplay:
  - Gerak 4 arah
  - Tool: **hoe**, **axe**, **water**
  - Seed: **corn**, **tomato**
  - Tanam → siram → tumbuh → panen
  - Interaksi dengan **Bed** (tidur / ganti hari) dan **Trader** (shop)
- Pause menu (ESC): **Resume**, **Save/Load slot**, **Pengaturan**, **Kembali ke Menu**

## Teknologi

- Python 3
- [Pygame](https://www.pygame.org/)
- [PyTMX](https://github.com/bitcraft/pytmx) (loader TMX untuk map Tiled)

## Struktur Folder (Ringkas)

- `code/` — source code game (entrypoint: `main.py`)
- `data/` — map Tiled (`map.tmx`) + tilesets
- `graphics/` — sprite/tiles/animasi
- `audio/` — musik & sfx
- `font/` — font
- `savegame/` — config & save slot
- `AssetPack/` — asset pack pihak ketiga (raw assets)

## Cara Menjalankan

> Catatan: game akan menyesuaikan working directory ke folder `code/`, jadi aman dijalankan dari root project.

### 1) Install dependencies

Buka terminal di folder project, lalu jalankan:

```bash
pip install pygame pytmx
```

Jika kamu menggunakan virtualenv (disarankan):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install pygame pytmx
```

### 2) Jalankan game

Dari root project:

```bash
python code/main.py
```

Atau dari folder `code/`:

```bash
cd code
python main.py
```

## Kontrol

### Gameplay

- **Gerak:** Arrow keys (↑ ↓ ← →)
- **Pakai tool:** `SPACE`
- **Ganti tool (hoe/axe/water):** `Q`
- **Pakai seed (tanam):** `Left Ctrl`
- **Ganti seed (corn/tomato):** `E`
- **Interaksi:** `ENTER`
  - Dekat **Trader** → buka/tutup shop
  - Dekat **Bed** → tidur (ganti hari / grow tanaman / reset cuaca & buah)
- **Pause:** `ESC`
  - Catatan: saat shop sedang terbuka, `ESC` dipakai untuk menutup shop (tidak membuka pause).

### Start Menu

- Navigasi: `W/S` atau `↑/↓`
- Pilih: `ENTER`
- Kembali: `ESC` (dari halaman Pengaturan/Load)

- Halaman **Pengaturan**:
  - Ubah nilai: `A/D` atau `←/→`

- Halaman **Load**:
  - Hapus slot: `DELETE` atau `BACKSPACE` (akan muncul konfirmasi)

### Shop (Trader)

- Navigasi item: `↑/↓`
- Aksi (buy/sell): `SPACE`
- Tutup shop: `ESC`

### Pause Menu

- Buka: `ESC`
- Navigasi: `W/S` atau `↑/↓`
- Pilih: `ENTER`
- Kembali: `ESC`

- Di halaman **Save/Load**:
  - Hapus slot: `DELETE` / `BACKSPACE`
  - Save ke slot yang sudah terisi akan meminta konfirmasi overwrite.

## Save & Config

### Lokasi file

- Setting global: `savegame/config.json`
- Save slot: `savegame/save_slot_1.json` s/d `savegame/save_slot_5.json`

### Catatan penting

- **Settings itu global** (resolusi & volume). Loading slot **tidak** mengubah setting.
- Sistem save punya dukungan migrasi dari format/letak lama (jika ada file save lama di `code/`, akan dipindah/dianggap kompatibel).

## Troubleshooting

- **Error: `ModuleNotFoundError: No module named 'pygame'`**
  - Jalankan `pip install pygame`

- **Error: `ModuleNotFoundError: No module named 'pytmx'`**
  - Jalankan `pip install pytmx`

- **Tidak ada suara / audio error**
  - Pastikan device audio aktif.
  - Coba ubah volume di menu, lalu restart game.

- **Font tidak muncul / file asset tidak ketemu**
  - Pastikan struktur folder tidak berubah (terutama `font/`, `graphics/`, `audio/`, `data/`).

## Lisensi

Lihat file `LICENSE` untuk lisensi repository ini. Untuk asset pihak ketiga di `AssetPack/`, ikuti lisensi masing-masing asset pack.