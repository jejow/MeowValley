import pygame
from pytmx.util_pygame import load_pygame
from settings import *
from player import Player
import os

class Level:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()

		# ===== LOAD MAP =====
		base_path = os.path.dirname(__file__)
		tmx_path = os.path.join(base_path, '..', 'data', 'map.tmx')
		self.tmx_data = load_pygame(tmx_path)

		self.tile_width = self.tmx_data.tilewidth
		self.tile_height = self.tmx_data.tileheight

		self.map_width = self.tmx_data.width * self.tile_width
		self.map_height = self.tmx_data.height * self.tile_height

		# ===== SPRITES =====
		self.all_sprites = pygame.sprite.Group()

		self.player = Player((400, 300))
		self.all_sprites.add(self.player)

		# ===== CAMERA =====
		self.offset = pygame.math.Vector2()

	def camera_follow(self):
		self.offset.x = self.player.rect.centerx - SCREEN_WIDTH / 2
		self.offset.y = self.player.rect.centery - SCREEN_HEIGHT / 2

		# ===== BATAS MAP =====
		self.offset.x = max(0, min(self.offset.x, self.map_width - SCREEN_WIDTH))
		self.offset.y = max(0, min(self.offset.y, self.map_height - SCREEN_HEIGHT))

	def draw_tiles(self):
		for layer in self.tmx_data.visible_layers:
			if hasattr(layer, 'tiles'):
				for x, y, surf in layer.tiles():
					pos_x = x * self.tile_width - self.offset.x
					pos_y = y * self.tile_height - self.offset.y
					self.display_surface.blit(surf, (pos_x, pos_y))

	def run(self, dt):
		self.all_sprites.update(dt)
		self.camera_follow()

		self.display_surface.fill('#71ddee')

		# draw map
		self.draw_tiles()

		# draw player
		for sprite in self.all_sprites:
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image, offset_pos)
