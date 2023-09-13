from numba import njit
from animation import Animation

from settings import *


@njit(fastmath=True, cache=True)
def get_angle(pos, length_w, length_h):
    angle = math.atan2(pos[1] - HEIGHT // 2, pos[0] - WIDTH // 2)
    return angle, math.atan2(length_w * math.sin(angle), length_h * math.cos(angle))


class Indicator:
    def __init__(self, fire, screen):
        self.fire = fire
        self.screen = screen
        self.angle = 0
        self.anim = Animation([pygame.image.load(f'data/ykazatel{i + 1}.png') for i in range(6)])
        self.length_h = HEIGHT // 2 - self.anim.height * 3
        self.length_w = WIDTH // 2 - self.anim.height * 3

    def paint(self, scroll, visible):
        if visible:
            self.angle, t = get_angle((self.fire.rect.center[0] - scroll[0], self.fire.rect.center[1] - scroll[1]),
                                      self.length_w, self.length_h)
            self.screen.blit(self.anim.next(), (WIDTH // 2 + math.cos(t) * self.length_w,
                                                HEIGHT // 2 + math.sin(t) * self.length_h))
