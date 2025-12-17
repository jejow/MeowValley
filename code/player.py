import pygame
import os

class Player(pygame.sprite.Sprite):
	def __init__(self, pos):
		super().__init__()

		# ===== LOAD ASSETS =====
		self.import_assets()
		self.frame_index = 0
		self.animation_speed = 6

		self.image = self.animations['idle'][0]
		self.rect = self.image.get_rect(center=pos)

		# ===== MOVEMENT =====
		self.direction = pygame.math.Vector2()
		self.speed = 180

		# ===== STATUS =====
		self.status = 'idle'
		self.facing_right = True

	def import_assets(self):
		self.animations = {
			'idle': [],
			'walk': []
		}

		base_path = os.path.dirname(__file__)
		player_path = os.path.join(base_path, 'graphics', 'player')

		print("DEBUG PLAYER PATH:", player_path)

		# idle → 0.png
		self.animations['idle'].append(
			pygame.image.load(
				os.path.join(player_path, '0.png')
			).convert_alpha()
		)

		# walk → 1.png, 2.png, 3.png
		for i in range(1, 4):
			self.animations['walk'].append(
				pygame.image.load(
					os.path.join(player_path, f'{i}.png')
				).convert_alpha()
			)

	def input(self):
		keys = pygame.key.get_pressed()
		self.direction.update(0, 0)

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

		if self.direction.length() > 0:
			self.direction = self.direction.normalize()
			self.status = 'walk'
		else:
			self.status = 'idle'

	def move(self, dt):
		self.rect.center += self.direction * self.speed * dt

	def animate(self, dt):
		animation = self.animations[self.status]

		self.frame_index += self.animation_speed * dt
		if self.frame_index >= len(animation):
			self.frame_index = 0

		image = animation[int(self.frame_index)]

		if not self.facing_right:
			image = pygame.transform.flip(image, True, False)

		self.image = image

	def update(self, dt):
		self.input()
		self.move(dt)
		self.animate(dt)
