from settings import *


class Footprint:
    im_arr = [pygame.image.load(f'data/sled{i + 1}.png') for i in range(4)]

    def __init__(self, x, y):
        self.im = Footprint.im_arr[random.randrange(len(Footprint.im_arr))].convert_alpha()
        self.x, self.y = (x - self.im.get_width() // 2) // 3 * 3, (y - self.im.get_height() // 2) // 3 * 3
        self.condition = 800

    def paint(self, screen, scroll, snow_counter):
        self.condition -= 1
        if snow_counter:
            self.condition -= 2
        if self.condition < self.im.get_alpha():
            self.im.set_alpha(self.im.get_alpha() - 1)
        screen.blit(self.im, (self.x - scroll[0], self.y - scroll[1]))
