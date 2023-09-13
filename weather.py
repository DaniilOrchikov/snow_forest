from animation import Animation
from settings import *


class Weather:
    def __init__(self, manager, screen):
        self.manager = manager
        self.screen = screen
        self.sc = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.start_time = time.time()
        self.SNOW_COUNTER = 8 * 60
        self.snow_counter = -254
        self.snow_animation = Animation([pygame.image.load(f'data/sneg{i + 1}.png').convert_alpha() for i in range(6)])

    def paint(self):
        self.sc.fill((0, 0, 0, 0))
        self.paint_snow()

    def paint_snow(self):
        if not int(time.time() - self.start_time + 1) % 150:
            self.snow_counter = self.SNOW_COUNTER + (time.time() - self.start_time) // 75
        if self.snow_counter > -255:
            self.snow_counter -= 1
            im = self.snow_animation.next()
            im.set_alpha(
                (min(255, int(self.SNOW_COUNTER - self.snow_counter)) if
                 self.snow_counter > 0 else 255 + self.snow_counter))
            for i in range(5):
                for j in range(3):
                    self.sc.blit(im, (i * self.snow_animation.width, j * self.snow_animation.height))
            self.screen.blit(self.sc, (0, 0))
