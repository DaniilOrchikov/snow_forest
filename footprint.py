from settings import *


class Footprint:
    im_arr = None

    @classmethod
    def load_images(cls):
        """Загружает изображения следов. Должен быть вызван после инициализации pygame.display."""
        if cls.im_arr is None:
            cls.im_arr = [pygame.image.load(f'data/sled{i + 1}.png') for i in range(4)]

    def __init__(self, x, y):
        # Убеждаемся что изображения загружены
        Footprint.load_images()
        
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
