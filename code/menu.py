import pygame
from settings import *

class Menu:
    def __init__(self, font):
        self.font = font
        self.options = ['Mulai Game', 'Keluar']
        self.index = 0
        self.start_y = 340
        self.spacing = 60

    def input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.index = (self.index - 1) % len(self.options)
            elif event.key == pygame.K_s:
                self.index = (self.index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.index]
        return None

    def draw(self, surface):
        for i, text in enumerate(self.options):
            color = '#FFEB3B' if i == self.index else 'white'
            surf = self.font.render(text, True, color)
            rect = surf.get_rect(
                center=(SCREEN_WIDTH // 2, self.start_y + i * self.spacing)
            )
            surface.blit(surf, rect)
