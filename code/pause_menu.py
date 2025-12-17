import os

import pygame

import settings
import save_system


class PauseMenu:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()
		self.title_font = pygame.font.Font(self._abs('../font/LycheeSoda.ttf'), 64)
		self.font = pygame.font.Font(self._abs('../font/LycheeSoda.ttf'), 34)
		self.page = 'main'  # 'main' | 'settings' | 'save' | 'load' | 'confirm_save' | 'confirm_delete'
		self.main_options = ['Lanjutkan', 'Save Game', 'Load Game', 'Pengaturan', 'Kembali ke Menu']
		self.settings_options = ['Resolusi', 'Volume Music', 'Volume SFX', 'Kembali']
		self.slot_options = []
		self.confirm_options = ['Ya', 'Tidak']
		self._confirm_slot = None
		self.index = 0
		self.spacing = 52

		# resolution selector (for settings page)
		self.resolutions = list(settings.AVAILABLE_RESOLUTIONS)
		current = (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
		self.res_index = self.resolutions.index(current) if current in self.resolutions else 0
		self.refresh_slots()

	def refresh_slots(self):
		self.slot_options = [save_system.format_slot_label(i) for i in save_system.list_slots()] + ['Kembali']
		self.index = max(0, min(self.index, len(self._current_options()) - 1))

	def _current_options(self):
		if self.page == 'main':
			return self.main_options
		if self.page == 'settings':
			return self.settings_options
		if self.page in ('save', 'load'):
			return self.slot_options
		return self.confirm_options

	def go_main(self):
		self.page = 'main'
		self.index = 0
		self._confirm_slot = None

	@staticmethod
	def _abs(relative_path: str) -> str:
		base_dir = os.path.dirname(os.path.abspath(__file__))
		return os.path.normpath(os.path.join(base_dir, relative_path))

	def set_display_surface(self):
		self.display_surface = pygame.display.get_surface()

	def handle_event(self, event):
		if event.type != pygame.KEYDOWN:
			return None

		if event.key == pygame.K_ESCAPE:
			if self.page == 'main':
				return 'resume'
			if self.page in ('confirm_save', 'confirm_delete'):
				# back to originating page
				self.page = 'save' if self.page == 'confirm_save' else 'load'
				self.index = 0
				self._confirm_slot = None
				return None
			# back from save/load/settings page
			self.go_main()
			return None

		options = self._current_options()

		# Delete slot shortcut on save/load pages
		if self.page in ('save', 'load') and event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
			current_opt = options[self.index]
			if current_opt != 'Kembali':
				slot = self.index + 1
				if save_system.slot_exists(slot):
					self.page = 'confirm_delete'
					self._confirm_slot = slot
					self.index = 0
			return None

		# Settings page adjustments
		if self.page == 'settings':
			current_opt = options[self.index]
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

			if current_opt == 'Volume Music' and event.key in (pygame.K_a, pygame.K_LEFT):
				settings.MUSIC_VOLUME = max(0.0, settings.MUSIC_VOLUME - 0.1)
				try:
					pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)
				except Exception:
					pass
				try:
					save_system.save_settings({
						'resolution': [int(settings.SCREEN_WIDTH), int(settings.SCREEN_HEIGHT)],
						'music_volume': float(settings.MUSIC_VOLUME),
						'sfx_volume': float(settings.SFX_VOLUME),
					})
				except Exception:
					pass
				return ('music_volume', float(settings.MUSIC_VOLUME))

			if current_opt == 'Volume Music' and event.key in (pygame.K_d, pygame.K_RIGHT):
				settings.MUSIC_VOLUME = min(1.0, settings.MUSIC_VOLUME + 0.1)
				try:
					pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)
				except Exception:
					pass
				try:
					save_system.save_settings({
						'resolution': [int(settings.SCREEN_WIDTH), int(settings.SCREEN_HEIGHT)],
						'music_volume': float(settings.MUSIC_VOLUME),
						'sfx_volume': float(settings.SFX_VOLUME),
					})
				except Exception:
					pass
				return ('music_volume', float(settings.MUSIC_VOLUME))

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

		if event.key in (pygame.K_w, pygame.K_UP):
			self.index = (self.index - 1) % len(options)
			return None

		if event.key in (pygame.K_s, pygame.K_DOWN):
			self.index = (self.index + 1) % len(options)
			return None

		if event.key == pygame.K_RETURN:
			current_opt = options[self.index]
			if self.page == 'main':
				if current_opt == 'Lanjutkan':
					return 'resume'
				if current_opt == 'Kembali ke Menu':
					return 'menu'
				if current_opt == 'Save Game':
					self.refresh_slots()
					self.page = 'save'
					self.index = 0
					return None
				if current_opt == 'Load Game':
					self.refresh_slots()
					self.page = 'load'
					self.index = 0
					return None
				if current_opt == 'Pengaturan':
					current = (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
					self.res_index = self.resolutions.index(current) if current in self.resolutions else 0
					self.page = 'settings'
					self.index = 0
					return None
			else:
				if self.page == 'settings':
					if current_opt == 'Kembali':
						self.go_main()
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
						except Exception:
							pass
						try:
							save_system.save_settings({
								'resolution': [int(settings.SCREEN_WIDTH), int(settings.SCREEN_HEIGHT)],
								'music_volume': float(settings.MUSIC_VOLUME),
								'sfx_volume': float(settings.SFX_VOLUME),
							})
						except Exception:
							pass
						return ('music_volume', float(settings.MUSIC_VOLUME))
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
				if self.page in ('save', 'load'):
					if current_opt == 'Kembali':
						self.go_main()
						return None
					slot = self.index + 1
					if self.page == 'save':
						if save_system.slot_exists(slot):
							self.page = 'confirm_save'
							self._confirm_slot = slot
							self.index = 0
							return None
						return ('save_slot', slot)
					if self.page == 'load':
						if save_system.slot_exists(slot):
							return ('load_slot', slot)
						return None
				if self.page == 'confirm_save':
					if current_opt == 'Ya' and self._confirm_slot is not None:
						return ('save_slot', int(self._confirm_slot))
					# Tidak
					self.page = 'save'
					self.index = 0
					self._confirm_slot = None
					return None
				if self.page == 'confirm_delete':
					if current_opt == 'Ya' and self._confirm_slot is not None:
						return ('delete_slot', int(self._confirm_slot))
					# Tidak
					self.page = 'load'
					self.index = 0
					self._confirm_slot = None
					return None

		return None

	@staticmethod
	def _pct(value: float) -> int:
		return int(max(0.0, min(1.0, float(value))) * 100)

	def _resolution_label(self):
		w, h = self.resolutions[self.res_index]
		return f'Resolusi: {w}x{h}'

	def _music_label(self):
		return f'Volume Music: {self._pct(settings.MUSIC_VOLUME)}%'

	def _sfx_label(self):
		return f'Volume SFX: {self._pct(settings.SFX_VOLUME)}%'

	def draw(self, background_surf: pygame.Surface | None = None):
		if background_surf is not None:
			self.display_surface.blit(background_surf, (0, 0))
		else:
			self.display_surface.fill('black')

		w, h = self.display_surface.get_size()
		overlay = pygame.Surface((w, h), flags=pygame.SRCALPHA)
		overlay.fill((0, 0, 0, 160))
		self.display_surface.blit(overlay, (0, 0))

		title = 'PAUSE' if self.page != 'settings' else 'PENGATURAN'
		title_surf = self.title_font.render(title, True, 'White')
		title_rect = title_surf.get_rect(center=(w // 2, 150))
		self.display_surface.blit(title_surf, title_rect)

		if self.page == 'main':
			hint_text = 'ESC untuk lanjut'
		elif self.page == 'settings':
			hint_text = 'ESC kembali | A/D ubah nilai'
		elif self.page in ('save', 'load'):
			hint_text = 'ESC kembali | DEL hapus slot'
		else:
			hint_text = 'ESC kembali'
		hint_surf = self.font.render(hint_text, True, 'White')
		hint_rect = hint_surf.get_rect(center=(w // 2, 220))
		self.display_surface.blit(hint_surf, hint_rect)

		start_y = 320
		options = self._current_options()
		if self.page == 'confirm_save' and self._confirm_slot is not None:
			msg = f'Timpa Slot {int(self._confirm_slot)}?'
			msg_surf = self.font.render(msg, True, 'White')
			msg_rect = msg_surf.get_rect(center=(w // 2, 280))
			self.display_surface.blit(msg_surf, msg_rect)
			start_y = 340
		if self.page == 'confirm_delete' and self._confirm_slot is not None:
			msg = f'Hapus Slot {int(self._confirm_slot)}?'
			msg_surf = self.font.render(msg, True, 'White')
			msg_rect = msg_surf.get_rect(center=(w // 2, 280))
			self.display_surface.blit(msg_surf, msg_rect)
			start_y = 340
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
			rect = surf.get_rect(center=(w // 2, start_y + i * self.spacing))
			self.display_surface.blit(surf, rect)
