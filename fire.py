from animation import Animation
from settings import *


class Fire:
    def __init__(self, manager):
        self.x, self.y = manager.player_rect.x + 30, manager.player_rect.y + 30
        self.im = pygame.image.load('data/koster.png').convert_alpha()
        self.fire_im_anim = Animation(
            [pygame.image.load(f'data/ogon{i + 1}.png').convert_alpha() for i in range(6)])
        self.rect = self.im.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.manager = manager

        self.HP = 40
        self.hp = self.HP

    def paint(self, screen, scroll):
        screen.blit(self.im, (self.x - scroll[0], self.y - scroll[1]))
        screen.blit(self.fire_im_anim.next(),
                    (self.rect.center[0] - self.fire_im_anim.width // 2 - scroll[0],
                     self.rect.center[1] - self.fire_im_anim.height - scroll[1] + 2 * 3))
        if self.rect.colliderect(self.manager.player_rect):
            self.manager.statistics[2] = max(self.manager.statistics[2], self.manager.budget)
            self.hp += self.manager.budget
            self.manager.budget = 0
            self.HP = max(self.HP, self.hp)

    def paint_hp(self):
        self.hp -= 0.02
        if self.manager.weather_manager.snow_counter > 0:
            self.hp -= 0.02
        self.manager.paint_bar(self.HP, self.hp, 200, 20, (WIDTH // 2, 20), 'red')
