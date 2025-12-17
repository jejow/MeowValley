from pygame.math import Vector2
# screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 64

# audio (0.0 - 1.0)
MUSIC_VOLUME = 0.4
SFX_VOLUME = 0.3

# Available resolutions for the start menu.
AVAILABLE_RESOLUTIONS = [
	(800, 600),
	(1024, 768),
	(1280, 720),
	(1366, 768),
	(1600, 900),
	(1920, 1080),
]

# overlay positions 
def _recompute_derived():
	global OVERLAY_POSITIONS
	OVERLAY_POSITIONS = {
		'tool': (40, SCREEN_HEIGHT - 15),
		'seed': (70, SCREEN_HEIGHT - 5),
	}


def set_resolution(width: int, height: int):
	"""Update global resolution values and derived layout constants.

	Note: This project uses `from settings import *` in many modules.
	To avoid stale values, pick the resolution BEFORE importing Level.
	"""
	global SCREEN_WIDTH, SCREEN_HEIGHT
	SCREEN_WIDTH = int(width)
	SCREEN_HEIGHT = int(height)
	_recompute_derived()


_recompute_derived()

PLAYER_TOOL_OFFSET = {
	'left': Vector2(-50,40),
	'right': Vector2(50,40),
	'up': Vector2(0,-10),
	'down': Vector2(0,50)
}

LAYERS = {
	'water': 0,
	'ground': 1,
	'soil': 2,
	'soil water': 3,
	'rain floor': 4,
	'house bottom': 5,
	'ground plant': 6,
	'main': 7,
	'house top': 8,
	'fruit': 9,
	'rain drops': 10
}

APPLE_POS = {
	'Small': [(18,17), (30,37), (12,50), (30,45), (20,30), (30,10)],
	'Large': [(30,24), (60,65), (50,50), (16,40),(45,50), (42,70)]
}

GROW_SPEED = {
	'corn': 1,
	'tomato': 0.7
}

SALE_PRICES = {
	'wood': 4,
	'apple': 2,
	'corn': 10,
	'tomato': 20
}
PURCHASE_PRICES = {
	'corn': 4,
	'tomato': 5
}