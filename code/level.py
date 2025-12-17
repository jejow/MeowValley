import pygame 
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from soil import Plant, WaterTile
from sky import Rain, Sky
from random import randint, choice
from menu import Menu

class Level:
	def __init__(self):

		# get the display surface
		self.display_surface = pygame.display.get_surface()

		# sprite groups
		self.all_sprites = CameraGroup()
		self.collision_sprites = pygame.sprite.Group()
		self.tree_sprites = pygame.sprite.Group()
		self.interaction_sprites = pygame.sprite.Group()

		self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
		self.setup()
		self.overlay = Overlay(self.player)
		self.transition = Transition(self.reset, self.player)

		# sky
		self.rain = Rain(self.all_sprites)
		self.raining = randint(0,10) > 7
		self.soil_layer.raining = self.raining
		self.sky = Sky()

		# shop
		self.menu = Menu(self.player, self.toggle_shop)
		self.shop_active = False

		# music
		self.success = pygame.mixer.Sound('../audio/success.wav')
		self.success.set_volume(SFX_VOLUME)
		self.music = pygame.mixer.Sound('../audio/music.mp3')
		self.music.set_volume(MUSIC_VOLUME)
		self.music.play(loops = -1)

	def serialize_state(self):
		# Player
		player_state = {
			'pos': [int(self.player.rect.centerx), int(self.player.rect.centery)],
			'status': str(self.player.status),
			'tool_index': int(self.player.tool_index),
			'seed_index': int(self.player.seed_index),
			'items': dict(self.player.item_inventory),
			'seeds': dict(self.player.seed_inventory),
			'money': int(self.player.money),
		}

		# Soil & plants
		plants = []
		for plant in self.soil_layer.plant_sprites.sprites():
			try:
				gx = int(plant.soil.rect.x // TILE_SIZE)
				gy = int(plant.soil.rect.y // TILE_SIZE)
			except Exception:
				continue
			plants.append({
				'type': plant.plant_type,
				'grid': [gx, gy],
				'age': float(plant.age),
				'harvestable': bool(plant.harvestable),
			})

		soil_state = {
			'grid': self.soil_layer.grid,
			'plants': plants,
		}

		# Trees
		trees = []
		for tree in self.tree_sprites.sprites():
			try:
				trees.append(tree.serialize_state())
			except Exception:
				pass

		return {
			'player': player_state,
			'shop_active': bool(self.shop_active),
			'raining': bool(self.raining),
			'sky_start_color': list(self.sky.start_color),
			'soil': soil_state,
			'trees': trees,
		}

	def apply_state(self, state):
		if not isinstance(state, dict):
			return

		# Shop / weather / sky
		self.shop_active = bool(state.get('shop_active', False))
		self.raining = bool(state.get('raining', self.raining))
		self.soil_layer.raining = self.raining
		try:
			color = state.get('sky_start_color')
			if isinstance(color, list) and len(color) == 3:
				self.sky.start_color = [float(color[0]), float(color[1]), float(color[2])]
		except Exception:
			pass

		# Player
		player_state = state.get('player', {})
		if isinstance(player_state, dict):
			pos = player_state.get('pos')
			if isinstance(pos, (list, tuple)) and len(pos) == 2:
				cx, cy = int(pos[0]), int(pos[1])
				self.player.rect.center = (cx, cy)
				self.player.pos.x = cx
				self.player.pos.y = cy
				self.player.hitbox.center = (cx, cy)
			try:
				self.player.status = str(player_state.get('status', self.player.status))
			except Exception:
				pass
			try:
				self.player.tool_index = int(player_state.get('tool_index', self.player.tool_index))
				self.player.tool_index = max(0, min(self.player.tool_index, len(self.player.tools) - 1))
				self.player.selected_tool = self.player.tools[self.player.tool_index]
			except Exception:
				pass
			try:
				self.player.seed_index = int(player_state.get('seed_index', self.player.seed_index))
				self.player.seed_index = max(0, min(self.player.seed_index, len(self.player.seeds) - 1))
				self.player.selected_seed = self.player.seeds[self.player.seed_index]
			except Exception:
				pass
			items = player_state.get('items')
			seeds = player_state.get('seeds')
			if isinstance(items, dict):
				self.player.item_inventory = {k: int(v) for k, v in items.items()}
			if isinstance(seeds, dict):
				self.player.seed_inventory = {k: int(v) for k, v in seeds.items()}
			try:
				self.player.money = int(player_state.get('money', self.player.money))
			except Exception:
				pass
			# Never resume in sleep-transition
			self.player.sleep = False

		# Soil grid
		soil_state = state.get('soil', {})
		if isinstance(soil_state, dict):
			grid = soil_state.get('grid')
			if isinstance(grid, list) and grid:
				try:
					self.soil_layer.grid = grid
					self.soil_layer.create_hit_rects()
					self.soil_layer.create_soil_tiles()
				except Exception:
					pass

			# Clear existing water & plants sprites
			for s in self.soil_layer.water_sprites.sprites():
				s.kill()
			self.soil_layer.water_sprites.empty()
			for p in self.soil_layer.plant_sprites.sprites():
				p.kill()
			self.soil_layer.plant_sprites.empty()

			# Recreate water sprites from grid
			try:
				for y, row in enumerate(self.soil_layer.grid):
					for x, cell in enumerate(row):
						if isinstance(cell, list) and 'W' in cell:
							WaterTile((x * TILE_SIZE, y * TILE_SIZE), choice(self.soil_layer.water_surfs), [self.all_sprites, self.soil_layer.water_sprites])
			except Exception:
				pass

			# Map soil sprites by grid position
			soil_by_grid = {}
			for soil_sprite in self.soil_layer.soil_sprites.sprites():
				soil_by_grid[(int(soil_sprite.rect.x // TILE_SIZE), int(soil_sprite.rect.y // TILE_SIZE))] = soil_sprite

			# Recreate plants
			plants = soil_state.get('plants', [])
			if isinstance(plants, list):
				for plant_info in plants:
					if not isinstance(plant_info, dict):
						continue
					ptype = plant_info.get('type')
					grid_pos = plant_info.get('grid')
					if not (isinstance(ptype, str) and isinstance(grid_pos, (list, tuple)) and len(grid_pos) == 2):
						continue
					gx, gy = int(grid_pos[0]), int(grid_pos[1])
					soil_sprite = soil_by_grid.get((gx, gy))
					if soil_sprite is None:
						continue
					# Ensure grid has 'P'
					try:
						cell = self.soil_layer.grid[gy][gx]
						if isinstance(cell, list) and 'P' not in cell:
							cell.append('P')
					except Exception:
						pass

					plant = Plant(ptype, [self.all_sprites, self.soil_layer.plant_sprites, self.collision_sprites], soil_sprite, self.soil_layer.check_watered)
					try:
						plant.age = float(plant_info.get('age', 0))
						plant.age = max(0.0, min(plant.age, float(plant.max_age)))
						plant.harvestable = bool(plant_info.get('harvestable', False))
						if int(plant.age) > 0:
							plant.z = LAYERS['main']
							plant.hitbox = plant.rect.copy().inflate(-26, -plant.rect.height * 0.4)
						plant.image = plant.frames[int(plant.age)]
						plant.rect = plant.image.get_rect(midbottom=soil_sprite.rect.midbottom + pygame.math.Vector2(0, plant.y_offset))
					except Exception:
						pass

		# Trees state
		trees = state.get('trees', [])
		if isinstance(trees, list) and trees:
			index = {}
			for tree in self.tree_sprites.sprites():
				key = (getattr(tree, 'name', None), int(tree.rect.x), int(tree.rect.y))
				index[key] = tree
			for tstate in trees:
				if not isinstance(tstate, dict):
					continue
				name = tstate.get('name')
				topleft = tstate.get('topleft')
				if not (isinstance(topleft, (list, tuple)) and len(topleft) == 2):
					continue
				key = (name, int(topleft[0]), int(topleft[1]))
				tree = index.get(key)
				if tree is None:
					continue
				try:
					tree.apply_state(tstate)
				except Exception:
					pass

	def setup(self):
		tmx_data = load_pygame('../data/map.tmx')

		# house 
		for layer in ['HouseFloor', 'HouseFurnitureBottom']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x * TILE_SIZE,y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

		for layer in ['HouseWalls', 'HouseFurnitureTop']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x * TILE_SIZE,y * TILE_SIZE), surf, self.all_sprites)

		# Fence
		for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
			Generic((x * TILE_SIZE,y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

		# water 
		water_frames = import_folder('../graphics/water')
		for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
			Water((x * TILE_SIZE,y * TILE_SIZE), water_frames, self.all_sprites)

		# trees 
		for obj in tmx_data.get_layer_by_name('Trees'):
			Tree(
				pos = (obj.x, obj.y), 
				surf = obj.image, 
				groups = [self.all_sprites, self.collision_sprites, self.tree_sprites], 
				name = obj.name,
				player_add = self.player_add)

		# wildflowers 
		for obj in tmx_data.get_layer_by_name('Decoration'):
			WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

		# collion tiles
		for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
			Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)

		# Player 
		for obj in tmx_data.get_layer_by_name('Player'):
			if obj.name == 'Start':
				self.player = Player(
					pos = (obj.x,obj.y), 
					group = self.all_sprites, 
					collision_sprites = self.collision_sprites,
					tree_sprites = self.tree_sprites,
					interaction = self.interaction_sprites,
					soil_layer = self.soil_layer,
					toggle_shop = self.toggle_shop)
			
			if obj.name == 'Bed':
				Interaction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)

			if obj.name == 'Trader':
				Interaction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)


		Generic(
			pos = (0,0),
			surf = pygame.image.load('../graphics/world/ground.png').convert_alpha(),
			groups = self.all_sprites,
			z = LAYERS['ground'])

	def player_add(self,item):

		self.player.item_inventory[item] += 1
		self.success.play()

	def toggle_shop(self):

		self.shop_active = not self.shop_active

	def reset(self):
		# plants
		self.soil_layer.update_plants()

		# soil
		self.soil_layer.remove_water()
		self.raining = randint(0,10) > 7
		self.soil_layer.raining = self.raining
		if self.raining:
			self.soil_layer.water_all()

		# apples on the trees
		for tree in self.tree_sprites.sprites():
			for apple in tree.apple_sprites.sprites():
				apple.kill()
			tree.create_fruit()

		# sky
		self.sky.start_color = [255,255,255]

	def plant_collision(self):
		if self.soil_layer.plant_sprites:
			for plant in self.soil_layer.plant_sprites.sprites():
				if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
					self.player_add(plant.plant_type)
					plant.kill()
					Particle(plant.rect.topleft, plant.image, self.all_sprites, z = LAYERS['main'])
					self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')

	def run(self,dt):
		
		# drawing logic
		self.display_surface.fill('black')
		self.all_sprites.custom_draw(self.player)
		
		# updates
		if self.shop_active:
			self.menu.update()
		else:
			self.all_sprites.update(dt)
			self.plant_collision()

		# weather
		self.overlay.display()
		if self.raining and not self.shop_active:
			self.rain.update()
		self.sky.display(dt)

		# transition overlay
		if self.player.sleep:
			self.transition.play()

class CameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.offset = pygame.math.Vector2()

	def custom_draw(self, player):
		self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
		self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

		for layer in LAYERS.values():
			for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
				if sprite.z == layer:
					offset_rect = sprite.rect.copy()
					offset_rect.center -= self.offset
					self.display_surface.blit(sprite.image, offset_rect)

					# # anaytics
					# if sprite == player:
					# 	pygame.draw.rect(self.display_surface,'red',offset_rect,5)
					# 	hitbox_rect = player.hitbox.copy()
					# 	hitbox_rect.center = offset_rect.center
					# 	pygame.draw.rect(self.display_surface,'green',hitbox_rect,5)
					# 	target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
					# 	pygame.draw.circle(self.display_surface,'blue',target_pos,5)