import os
import pygame, sys
import importlib

import settings
from start_menu import StartMenu
from pause_menu import PauseMenu
import save_system

class Game:
	def __init__(self):
		pygame.init()
		# Make relative paths in the existing codebase stable
		os.chdir(os.path.dirname(os.path.abspath(__file__)))

		# Load persisted settings (resolution + volumes) before creating the window
		cfg = save_system.load_settings() or {}
		try:
			res = cfg.get('resolution')
			if isinstance(res, (list, tuple)) and len(res) == 2:
				settings.set_resolution(int(res[0]), int(res[1]))
		except Exception:
			pass
		try:
			if 'music_volume' in cfg:
				settings.MUSIC_VOLUME = float(cfg['music_volume'])
			if 'sfx_volume' in cfg:
				settings.SFX_VOLUME = float(cfg['sfx_volume'])
		except Exception:
			pass

		self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
		pygame.display.set_caption('Meow Valley')
		self.clock = pygame.time.Clock()
		self.level = None
		self.in_menu = True
		self.paused = False
		self.pause_menu = None
		self.last_game_frame = None
		self.current_save_slot = None
		self.menu = StartMenu()
		self.menu.refresh_save_state()
		self.menu.start_music()

	def _reload_gameplay_modules(self):
		# Needed because many modules use `from settings import *`.
		# Reloading re-reads the updated settings (e.g., resolution) before creating a new Level.
		module_names = [
			'sprites',
			'soil',
			'player',
			'overlay',
			'sky',
			'transition',
			'menu',
			'level',
		]
		for name in module_names:
			mod = sys.modules.get(name)
			if mod is None:
				continue
			try:
				importlib.reload(mod)
			except Exception:
				pass

	def apply_resolution(self, width: int, height: int):
		# IMPORTANT: This must happen before importing Level (which reads settings via star-imports)
		settings.set_resolution(width, height)
		self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
		self.menu.set_display_surface()
		try:
			save_system.save_settings({
				'resolution': [int(settings.SCREEN_WIDTH), int(settings.SCREEN_HEIGHT)],
				'music_volume': float(settings.MUSIC_VOLUME),
				'sfx_volume': float(settings.SFX_VOLUME),
			})
		except Exception:
			pass

	def start_game(self, saved_level_state=None):
		# Stop menu music so it doesn't overlap with in-game music
		self.menu.stop_music()
		# Lazy import so all star-imports inside the game code see the chosen resolution
		from level import Level
		self.level = Level()
		if saved_level_state is not None:
			try:
				self.level.apply_state(saved_level_state)
			except Exception:
				pass
		self.in_menu = False
		self.paused = False
		self.last_game_frame = None

	def save_current_game(self):
		if self.level is None:
			return
		if self.current_save_slot is None:
			return
		self.save_current_game_to_slot(self.current_save_slot)

	def save_current_game_to_slot(self, slot: int):
		if self.level is None:
			return
		try:
			# IMPORTANT: Settings are global (stored in savegame/config.json).
			# Do not snapshot settings into the save slot; otherwise loading a slot
			# can unexpectedly revert the user's current menu settings.
			payload = {
				'level': self.level.serialize_state(),
			}
			save_system.save_game_slot(int(slot), payload)
			self.current_save_slot = int(slot)
			self.menu.refresh_save_state()
			if self.pause_menu:
				self.pause_menu.refresh_slots()
		except Exception:
			pass

	def load_game_from_slot(self, slot: int, from_pause: bool):
		data = save_system.load_game_slot(int(slot)) or {}
		if not isinstance(data, dict):
			return

		# NOTE: We intentionally DO NOT apply per-slot settings.
		# Settings are global (stored in savegame/config.json) and should not
		# revert when the player loads a different slot.

		# Stop current gameplay music if any
		if from_pause:
			try:
				if self.level is not None and hasattr(self.level, 'music'):
					self.level.music.stop()
			except Exception:
				pass

		# Reload gameplay modules so star-import settings are refreshed
		self._reload_gameplay_modules()
		self.current_save_slot = int(slot)
		self.start_game(saved_level_state=(data.get('level') if isinstance(data, dict) else None))

	def enter_pause(self):
		if self.in_menu or self.level is None:
			return
		self.paused = True
		if self.pause_menu is None:
			self.pause_menu = PauseMenu()
		else:
			self.pause_menu.set_display_surface()
		try:
			pygame.mixer.pause()
		except:
			pass

	def resume_from_pause(self):
		self.paused = False
		try:
			pygame.mixer.unpause()
		except:
			pass

	def return_to_menu(self):
		# Ensure audio is running again for menu music
		try:
			pygame.mixer.unpause()
		except:
			pass
		try:
			if self.level is not None and hasattr(self.level, 'music'):
				self.level.music.stop()
		except:
			pass
		self.level = None
		self.paused = False
		self.in_menu = True
		self.last_game_frame = None
		# Reset menu state and start its music
		try:
			self.menu.page = 'main'
			self.menu.index = 0
		except:
			pass
		self.menu.start_music(force=True)

	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					# Best-effort save if player closes the window mid-game (only if a slot is selected)
					if not self.in_menu:
						self.save_current_game()
					self.menu.stop_music()
					pygame.quit()
					sys.exit()

				if self.in_menu:
					action = self.menu.handle_event(event)
					if action == 'start':
						self.current_save_slot = None
						self.start_game()
					elif isinstance(action, tuple) and action[0] == 'load_slot':
						slot = int(action[1])
						self.load_game_from_slot(slot, from_pause=False)
					elif isinstance(action, tuple) and action[0] == 'delete_slot':
						slot = int(action[1])
						try:
							save_system.delete_slot(slot)
						except Exception:
							pass
						self.menu.refresh_save_state()
						# keep user on load page after delete
						try:
							self.menu.page = 'load'
						except Exception:
							pass
					elif action == 'quit':
						# Persist settings on exit
						try:
							save_system.save_settings({
								'resolution': [int(settings.SCREEN_WIDTH), int(settings.SCREEN_HEIGHT)],
								'music_volume': float(settings.MUSIC_VOLUME),
								'sfx_volume': float(settings.SFX_VOLUME),
							})
						except Exception:
							pass
						self.menu.stop_music()
						pygame.quit()
						sys.exit()
					elif isinstance(action, tuple) and action[0] == 'resolution':
						w, h = action[1]
						self.apply_resolution(w, h)
				else:
					if self.paused:
						action = self.pause_menu.handle_event(event) if self.pause_menu else None
						if action == 'resume':
							self.resume_from_pause()
						elif action == 'menu':
							self.return_to_menu()
						elif isinstance(action, tuple) and action[0] == 'resolution':
							w, h = action[1]
							# Resolution changes require a Level rebuild because many modules
							# use `from settings import *`.
							saved_level_state = None
							try:
								if self.level is not None:
									saved_level_state = self.level.serialize_state()
							except Exception:
								saved_level_state = None
							try:
								if self.level is not None and hasattr(self.level, 'music'):
									self.level.music.stop()
							except Exception:
								pass
							self.apply_resolution(w, h)
							self._reload_gameplay_modules()
							self.start_game(saved_level_state=saved_level_state)
							self.enter_pause()
							self.last_game_frame = None
						elif isinstance(action, tuple) and action[0] == 'music_volume':
							try:
								if self.level is not None and hasattr(self.level, 'music'):
									self.level.music.set_volume(float(action[1]))
							except Exception:
								pass
						elif isinstance(action, tuple) and action[0] == 'save_slot':
							slot = int(action[1])
							self.save_current_game_to_slot(slot)
							if self.pause_menu:
								self.pause_menu.go_main()
						elif isinstance(action, tuple) and action[0] == 'delete_slot':
							slot = int(action[1])
							try:
								save_system.delete_slot(slot)
							except Exception:
								pass
							if self.pause_menu:
								self.pause_menu.refresh_slots()
								self.pause_menu.page = 'load'
								self.pause_menu.index = 0
						elif isinstance(action, tuple) and action[0] == 'load_slot':
							slot = int(action[1])
							self.load_game_from_slot(slot, from_pause=True)
							# Remain unpaused after loading
							self.paused = False
					else:
						if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
							# ESC is also used to close the shop menu; don't pause while shop is open
							if not (self.level and getattr(self.level, 'shop_active', False)):
								self.enter_pause()
  
			dt = self.clock.tick() / 1000
			if self.in_menu:
				self.menu.draw()
			elif self.paused:
				if self.pause_menu:
					self.pause_menu.set_display_surface()
				self.screen = pygame.display.get_surface()
				(self.pause_menu.draw(self.last_game_frame) if self.pause_menu else None)
			else:
				self.level.run(dt)
				# Keep a copy for pause background
				try:
					self.last_game_frame = self.screen.copy()
				except:
					self.last_game_frame = None
			pygame.display.update()

if __name__ == '__main__':
	game = Game()
	game.run()