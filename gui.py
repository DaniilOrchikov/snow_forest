import pygame

from settings import *


class Button:
    def __init__(self, x, y, text, color_1, color_2, text_size, on=False):
        self.x, self.y = x, y
        self.text = text
        self.colors = (color_1, color_2)
        self.font = pygame.font.Font(FONT, text_size)
        self.on_text = self.font.render(text, True, color_1)
        self.off_text = self.font.render(text, True, color_2)
        self.rect = self.on_text.get_rect()
        self.rect.center = (self.x, self.y)
        self.on = on

    def paint(self, screen):
        if self.on:
            screen.blit(self.on_text, (self.x - self.on_text.get_width() // 2, self.y - self.on_text.get_height() // 2))
        else:
            screen.blit(self.off_text,
                        (self.x - self.off_text.get_width() // 2, self.y - self.off_text.get_height() // 2))


class Slider:
    def __init__(self, x, y, length, step, min_value, max_value, color_1, color_2, text_size):
        self.font = pygame.font.Font(FONT, text_size)
        self.min_value = self.value = min_value
        self.max_value = max_value
        self.step = step
        self.x, self.y, self.length = x - length // 2, y - length // 2, length
        self.min_value_text = self.font.render(str(min_value), True, color_1)
        self.max_value_text = self.font.render(str(max_value), True, color_1)
        self.color_1 = color_1
        self.color_2 = color_2
        self.regulator_radius = 10
        self.rect = None

    def paint(self, screen):
        pygame.draw.line(screen, self.color_2, (self.x, self.y), (self.x + self.length, self.y), 6)
        pygame.draw.circle(screen, self.color_1, (
            self.x + self.length / (self.max_value - self.min_value) * (self.value - self.min_value), self.y),
                           self.regulator_radius)
        self.rect = pygame.Rect(self.x + self.length / (self.max_value - self.min_value) * (
                    self.value - self.min_value) - self.regulator_radius, self.y - self.regulator_radius,
                                self.regulator_radius * 2, self.regulator_radius * 2)

    # def shift(self, mouse_pos):
        # if self.rect.collidepoint(mouse_pos):

