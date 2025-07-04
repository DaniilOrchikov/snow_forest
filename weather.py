from animation import Animation
from settings import *
from constants import *


class Weather:
    def __init__(self, manager, screen):
        self.manager = manager
        self.screen = screen
        self.sc = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.start_time = time.time()
        self.SNOW_COUNTER = 8 * 60
        self.snow_counter = -254
        self.snow_animation = Animation([pygame.image.load(f'data/sneg{i + 1}.png').convert_alpha() for i in range(6)], SNOW_ANIMATION_STEP)

    def paint(self):
        self.sc.fill((0, 0, 0, 0))
        self.paint_snow()

    def paint_snow(self):
        # Исправлена логика проверки снега
        elapsed_time = int(time.time() - self.start_time)
        if elapsed_time % SNOW_CYCLE_DURATION == 0 and elapsed_time > 0:
            self.snow_counter = self.SNOW_COUNTER + elapsed_time // SNOW_DURATION_MULTIPLIER
        if self.snow_counter > -255:
            self.snow_counter -= 1
            im = self.snow_animation.next()
            alpha_value = (min(SNOW_ALPHA_MAX, int(self.SNOW_COUNTER - self.snow_counter)) if
                          self.snow_counter > 0 else max(SNOW_ALPHA_MIN, SNOW_ALPHA_MAX + self.snow_counter))
            im.set_alpha(alpha_value)
            for i in range(5):
                for j in range(3):
                    self.sc.blit(im, (i * self.snow_animation.width, j * self.snow_animation.height))
            self.screen.blit(self.sc, (0, 0))
