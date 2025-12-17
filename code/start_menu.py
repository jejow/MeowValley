import os

import pygame

import settings
import save_system


class StartMenu:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()
		self.title_font = pygame.font.Font(self._abs('../font/LycheeSoda.ttf'), 72)
		self.font = pygame.font.Font(self._abs('../font/LycheeSoda.ttf'), 34)

		# background tile
		try:
			self.bg_tile = pygame.image.load(self._abs('../graphics/world/ground.png')).convert()
		except:
			self.bg_tile = None

		# menu music
		self.music_path = self._abs('../audio/bg.mp3')
		self._music_started = False

		# menu pages
		self.page = 'main'  # 'main' | 'settings' | 'load' | 'confirm_delete'
		self.main_options = ['Mulai Game', 'Load Game', 'Pengaturan', 'Keluar']
		self.settings_options = ['Resolusi', 'Volume Music', 'Volume SFX', 'Kembali']
		self.load_options = []
		self.confirm_options = ['Ya', 'Tidak']
		self._confirm_slot = None
		self.index = 0
		self.spacing = 52

		# resolution selector
		self.resolutions = list(settings.AVAILABLE_RESOLUTIONS)
		current = (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
		self.res_index = self.resolutions.index(current) if current in self.resolutions else 0

	def refresh_save_state(self):
		self.load_options = [save_system.format_slot_label(i) for i in save_system.list_slots()] + ['Kembali']
		self.index = max(0, min(self.index, len(self._current_options()) - 1))

	@staticmethod
	def _abs(relative_path: str) -> str:
		base_dir = os.path.dirname(os.path.abspath(__file__))
		return os.path.normpath(os.path.join(base_dir, relative_path))

	def set_display_surface(self):
		self.display_surface = pygame.display.get_surface()

	def _resolution_label(self):
		w, h = self.resolutions[self.res_index]
		return f'Resolusi: {w}x{h}'

	@staticmethod
	def _pct(value: float) -> int:
		return int(max(0.0, min(1.0, float(value))) * 100)

	def _music_label(self):
		return f'Volume Music: {self._pct(settings.MUSIC_VOLUME)}%'

	def _sfx_label(self):
		return f'Volume SFX: {self._pct(settings.SFX_VOLUME)}%'

	def _current_options(self):
		if self.page == 'main':
			return self.main_options
		if self.page == 'settings':
			return self.settings_options
		if self.page == 'load':
			return self.load_options
		return self.confirm_options

	def start_music(self, force: bool = False):
		try:
			if pygame.mixer.get_init() is None:
				pygame.mixer.init()
			if force:
				try:
					pygame.mixer.music.stop()
				except:
					pass
			else:
				# If music is already playing, don't restart it every time
				try:
					if pygame.mixer.music.get_busy():
						self._music_started = True
						return
				except:
					pass
			pygame.mixer.music.load(self.music_path)
			pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)
			pygame.mixer.music.play(-1)
			self._music_started = True
		except:
			self._music_started = False

	def stop_music(self, fade_ms: int = 400):
		try:
			if self._music_started:
				pygame.mixer.music.fadeout(int(fade_ms))
		except:
			pass
		finally:
			# Allow restarting later (e.g., returning from gameplay)
			self._music_started = False

	def handle_event(self, event):
		if event.type != pygame.KEYDOWN:
			return None

		# ESC goes back from subpages
		if event.key == pygame.K_ESCAPE:
			if self.page in ('settings', 'load'):
				self.page = 'main'
				self.index = 0
				return None
			if self.page == 'confirm_delete':
				self.page = 'load'
				self.index = 0
				self._confirm_slot = None
				return None

		options = self._current_options()

		if event.key in (pygame.K_w, pygame.K_UP):
			self.index = (self.index - 1) % len(options)
			return None

		if event.key in (pygame.K_s, pygame.K_DOWN):
			self.index = (self.index + 1) % len(options)
			return None

		current_opt = options[self.index]

		# Delete slot shortcut on load page
		if self.page == 'load' and event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
			if current_opt != 'Kembali':
				slot = self.index + 1
				if save_system.slot_exists(slot):
					self.page = 'confirm_delete'
					self._confirm_slot = slot
					self.index = 0
			return None
		if self.page == 'settings':
			# Resolution
			if current_opt == 'Resolusi' and event.key in (pygame.K_a, pygame.K_LEFT):
				self.res_index = (self.res_index - 1) % len(self.resolutions)
				try:
					save_system.save_settings({
						'resolution': list(self.resolutions[self.res_index]),
						'music_volume': float(settings.MUSIC_VOLUME),
						'sfx_volume': float(settings.SFX_VOLUME),
					})
				except Exception:
					pass
				return ('resolution', self.resolutions[self.res_index])

			if current_opt == 'Resolusi' and event.key in (pygame.K_d, pygame.K_RIGHT):
				self.res_index = (self.res_index + 1) % len(self.resolutions)
				try:
					save_system.save_settings({
						'resolution': list(self.resolutions[self.res_index]),
						'music_volume': float(settings.MUSIC_VOLUME),
						'sfx_volume': float(settings.SFX_VOLUME),
					})
				except Exception:
					pass
				return ('resolution', self.resolutions[self.res_index])

			# Music volume
			if current_opt == 'Volume Music' and event.key in (pygame.K_a, pygame.K_LEFT):
				settings.MUSIC_VOLUME = max(0.0, settings.MUSIC_VOLUME - 0.1)
				try:
					pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)
				except:
					pass
				try:
					save_system.save_settings({
						'resolution': [int(settings.SCREEN_WIDTH), int(settings.SCREEN_HEIGHT)],
						'music_volume': float(settings.MUSIC_VOLUME),
						'sfx_volume': float(settings.SFX_VOLUME),
					})
				except Exception:
					pass
				return None

			if current_opt == 'Volume Music' and event.key in (pygame.K_d, pygame.K_RIGHT):
				settings.MUSIC_VOLUME = min(1.0, settings.MUSIC_VOLUME + 0.1)
				try:
					pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)
				except:
					pass
				try:
					save_system.save_settings({
						'resolution': [int(settings.SCREEN_WIDTH), int(settings.SCREEN_HEIGHT)],
						'music_volume': float(settings.MUSIC_VOLUME),
						'sfx_volume': float(settings.SFX_VOLUME),
					})
				except Exception:
					pass
				return None

			# SFX volume (applies to newly created sounds)
			if current_opt == 'Volume SFX' and event.key in (pygame.K_a, pygame.K_LEFT):
				settings.SFX_VOLUME = max(0.0, settings.SFX_VOLUME - 0.1)
				try:
					save_system.save_settings({
						'resolution': [int(settings.SCREEN_WIDTH), int(settings.SCREEN_HEIGHT)],
						'music_volume': float(settings.MUSIC_VOLUME),
						'sfx_volume': float(settings.SFX_VOLUME),
					})
				except Exception:
					pass
				return None

			if current_opt == 'Volume SFX' and event.key in (pygame.K_d, pygame.K_RIGHT):
				settings.SFX_VOLUME = min(1.0, settings.SFX_VOLUME + 0.1)
				try:
					save_system.save_settings({
						'resolution': [int(settings.SCREEN_WIDTH), int(settings.SCREEN_HEIGHT)],
						'music_volume': float(settings.MUSIC_VOLUME),
						'sfx_volume': float(settings.SFX_VOLUME),
					})
				except Exception:
					pass
				return None

		if event.key == pygame.K_RETURN:
			if self.page == 'main':
				if current_opt == 'Mulai Game':
					return 'start'
				if current_opt == 'Load Game':
					self.refresh_save_state()
					self.page = 'load'
					self.index = 0
					return None
				if current_opt == 'Keluar':
					return 'quit'
				if current_opt == 'Pengaturan':
					self.page = 'settings'
					self.index = 0
					return None
			elif self.page == 'settings':
				if current_opt == 'Kembali':
					self.page = 'main'
					self.index = 0
					return None
				if current_opt == 'Resolusi':
					self.res_index = (self.res_index + 1) % len(self.resolutions)
					try:
						save_system.save_settings({
							'resolution': list(self.resolutions[self.res_index]),
							'music_volume': float(settings.MUSIC_VOLUME),
							'sfx_volume': float(settings.SFX_VOLUME),
						})
					except Exception:
						pass
					return ('resolution', self.resolutions[self.res_index])
				if current_opt == 'Volume Music':
					settings.MUSIC_VOLUME = min(1.0, settings.MUSIC_VOLUME + 0.1)
					try:
						pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)
					except:
						pass
					try:
						save_system.save_settings({
							'resolution': [int(settings.SCREEN_WIDTH), int(settings.SCREEN_HEIGHT)],
							'music_volume': float(settings.MUSIC_VOLUME),
							'sfx_volume': float(settings.SFX_VOLUME),
						})
					except Exception:
						pass
					return None
				if current_opt == 'Volume SFX':
					settings.SFX_VOLUME = min(1.0, settings.SFX_VOLUME + 0.1)
					try:
						save_system.save_settings({
							'resolution': [int(settings.SCREEN_WIDTH), int(settings.SCREEN_HEIGHT)],
							'music_volume': float(settings.MUSIC_VOLUME),
							'sfx_volume': float(settings.SFX_VOLUME),
						})
					except Exception:
						pass
					return None
			else:
				if self.page == 'load':
					# load page
					if current_opt == 'Kembali':
						self.page = 'main'
						self.index = 0
						return None
					# Slot selection
					slot = self.index + 1
					if save_system.slot_exists(slot):
						return ('load_slot', slot)
					return None
				# confirm delete
				if self.page == 'confirm_delete':
					if current_opt == 'Ya' and self._confirm_slot is not None:
						return ('delete_slot', int(self._confirm_slot))
					# Tidak
					self.page = 'load'
					self.index = 0
					self._confirm_slot = None
					return None

		return None

	def draw(self):
		# background
		if self.bg_tile is None:
			self.display_surface.fill('#71ddee')
		else:
			tw, th = self.bg_tile.get_size()
			for y in range(0, settings.SCREEN_HEIGHT, th):
				for x in range(0, settings.SCREEN_WIDTH, tw):
					self.display_surface.blit(self.bg_tile, (x, y))

		# title
		title_surf = self.title_font.render('MEOW VALLEY', True, 'Black')
		title_rect = title_surf.get_rect(center=(settings.SCREEN_WIDTH // 2, 140))
		self.display_surface.blit(title_surf, title_rect)

		# menu entries
		start_y = 280
		options = self._current_options()
		if self.page == 'confirm_delete' and self._confirm_slot is not None:
			msg = f'Hapus Slot {int(self._confirm_slot)}?'
			msg_surf = self.font.render(msg, True, 'White')
			msg_rect = msg_surf.get_rect(center=(settings.SCREEN_WIDTH // 2, 260))
			self.display_surface.blit(msg_surf, msg_rect)
			start_y = 320
		for i, opt in enumerate(options):
			if self.page == 'settings':
				if opt == 'Resolusi':
					label = self._resolution_label()
				elif opt == 'Volume Music':
					label = self._music_label()
				elif opt == 'Volume SFX':
					label = self._sfx_label()
				else:
					label = opt
			else:
				label = opt
			color = '#FFEB3B' if i == self.index else 'White'
			surf = self.font.render(label, True, color)
			rect = surf.get_rect(center=(settings.SCREEN_WIDTH // 2, start_y + i * self.spacing))
			self.display_surface.blit(surf, rect)
