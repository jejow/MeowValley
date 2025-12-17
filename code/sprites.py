import pygame
from settings import *
from random import randint, choice, shuffle
from timer import Timer

class Generic(pygame.sprite.Sprite):
	def __init__(self, pos, surf, groups, z = LAYERS['main']):
		# NOTE: `Sprite.groups()` order is not guaranteed.
		# Many game objects need a stable reference to the primary render group.
		if isinstance(groups, (list, tuple)) and len(groups) > 0:
			self.draw_group = groups[0]
		else:
			self.draw_group = groups
		super().__init__(groups)
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.z = z
		self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)

class Interaction(Generic):
	def __init__(self, pos, size, groups, name):
		surf = pygame.Surface(size)
		super().__init__(pos, surf, groups)
		self.name = name

class Water(Generic):
	def __init__(self, pos, frames, groups):

		#animation setup
		self.frames = frames
		self.frame_index = 0

		# sprite setup
		super().__init__(
				pos = pos, 
				surf = self.frames[self.frame_index], 
				groups = groups, 
				z = LAYERS['water']) 

	def animate(self,dt):
		self.frame_index += 5 * dt
		if self.frame_index >= len(self.frames):
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]

	def update(self,dt):
		self.animate(dt)

class WildFlower(Generic):
	def __init__(self, pos, surf, groups):
		super().__init__(pos, surf, groups)
		self.hitbox = self.rect.copy().inflate(-20,-self.rect.height * 0.9)

class Particle(Generic):
	def __init__(self, pos, surf, groups, z, duration = 200):
		super().__init__(pos, surf, groups, z)
		self.start_time = pygame.time.get_ticks()
		self.duration = duration

		# white surface 
		mask_surf = pygame.mask.from_surface(self.image)
		new_surf = mask_surf.to_surface()
		new_surf.set_colorkey((0,0,0))
		self.image = new_surf

	def update(self,dt):
		current_time = pygame.time.get_ticks()
		if current_time - self.start_time > self.duration:
			self.kill()

class Tree(Generic):
	def __init__(self, pos, surf, groups, name, player_add):
		super().__init__(pos, surf, groups)
		self.name = name

		# tree attributes
		self.health = 5
		self.alive = True
		stump_path = f'../graphics/stumps/{"small" if name == "Small" else "large"}.png'
		self.stump_surf = pygame.image.load(stump_path).convert_alpha()

		# apples
		try:
			self.apple_surf = pygame.image.load('../graphics/fruit/apple.png').convert_alpha()
		except:
			self.apple_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
			pygame.draw.circle(self.apple_surf, (220, 0, 0), (8, 8), 7)
		self.apple_pos = APPLE_POS[name]
		self.apple_sprites = pygame.sprite.Group()
		self.create_fruit()

		self.player_add = player_add

		# sounds
		self.axe_sound = pygame.mixer.Sound('../audio/axe.mp3')
		self.axe_sound.set_volume(SFX_VOLUME)

	def damage(self):
		
		# damaging the tree
		self.health -= 1

		# play sound
		self.axe_sound.play()

		# remove an apple
		if len(self.apple_sprites.sprites()) > 0:
			random_apple = choice(self.apple_sprites.sprites())
			Particle(
				pos = random_apple.rect.topleft,
				surf = random_apple.image, 
				groups = self.draw_group, 
				z = LAYERS['fruit'])
			self.player_add('apple')
			random_apple.kill()

	def check_death(self):
		if self.health <= 0:
			Particle(self.rect.topleft, self.image, self.draw_group, LAYERS['fruit'], 300)
			self.image = self.stump_surf
			self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
			self.hitbox = self.rect.copy().inflate(-10,-self.rect.height * 0.6)
			self.alive = False
			self.player_add('wood')

	def update(self,dt):
		if self.alive:
			self.check_death()

	def create_fruit(self):
		# Clear any existing apples first (prevents stacking across respawns)
		for apple in self.apple_sprites.sprites():
			apple.kill()
		self.apple_sprites.empty()

		placed_rects = []

		# Shuffle spawn points so distribution looks more natural
		spawn_points = list(self.apple_pos)
		shuffle(spawn_points)

		# Prevent apples from overlapping/merging visually
		pad = max(4, min(self.apple_surf.get_width(), self.apple_surf.get_height()) // 3)

		# Cap apple count so trees don't look cluttered
		max_apples = 3 if len(spawn_points) >= 6 else 2
		created = 0

		for pos in spawn_points:
			if created >= max_apples:
				break
			x = pos[0] + self.rect.left
			y = pos[1] + self.rect.top
			candidate_rect = self.apple_surf.get_rect(topleft=(x, y)).inflate(pad * 2, pad * 2)

			if any(candidate_rect.colliderect(r) for r in placed_rects):
				continue

			Generic(
				pos=(x, y),
				surf=self.apple_surf,
				groups=[self.apple_sprites, self.draw_group],
				z=LAYERS['fruit'])
			placed_rects.append(candidate_rect)
			created += 1

		# Guarantee at least one apple so players can always see them
		if created == 0 and spawn_points:
			pos = spawn_points[0]
			x = pos[0] + self.rect.left
			y = pos[1] + self.rect.top
			Generic(
				pos=(x, y),
				surf=self.apple_surf,
				groups=[self.apple_sprites, self.draw_group],
				z=LAYERS['fruit'])

	def serialize_state(self):
		apples = []
		for apple in self.apple_sprites.sprites():
			apples.append([
				int(apple.rect.x - self.rect.x),
				int(apple.rect.y - self.rect.y),
			])
		return {
			'name': getattr(self, 'name', None),
			'topleft': [int(self.rect.x), int(self.rect.y)],
			'health': int(self.health),
			'alive': bool(self.alive),
			'apples': apples,
		}

	def apply_state(self, state):
		try:
			self.health = int(state.get('health', self.health))
		except Exception:
			pass
		try:
			self.alive = bool(state.get('alive', self.alive))
		except Exception:
			pass

		# Ensure correct stump appearance if dead
		if self.health <= 0 or not self.alive:
			self.check_death()

		# Restore apples exactly
		for apple in self.apple_sprites.sprites():
			apple.kill()
		self.apple_sprites.empty()

		apples = state.get('apples', [])
		if isinstance(apples, list) and apples:
			for rel in apples:
				if not (isinstance(rel, (list, tuple)) and len(rel) == 2):
					continue
				x = int(self.rect.x + int(rel[0]))
				y = int(self.rect.y + int(rel[1]))
				Generic(
					pos=(x, y),
					surf=self.apple_surf,
					groups=[self.apple_sprites, self.draw_group],
					z=LAYERS['fruit'])
		else:
			# Fallback: regenerate
			self.create_fruit()