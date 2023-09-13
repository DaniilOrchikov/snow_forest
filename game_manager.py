from numba import njit

from indicator import Indicator
from level import Level
from settings import *
from fire import Fire
from footprint import Footprint
from weather import Weather


@njit(fastmath=True, cache=True)
def approximate_comparison(x, y, shift):
    for q in range(-shift, shift):
        for h in range(-shift, shift):
            if x - q == y - h:
                return True
    return False


def physics(rect, move, physics_map):
    collisions = {'right': False, 'left': False, 'top': False, 'bottom': False}
    if move[0] != 0:
        rect.x += move[0]
        collision_tile = collision_test(rect, physics_map)
        if collision_tile:
            if move[0] > 0:
                collisions['right'] = True
                rect.right = collision_tile.rect.left
            else:
                collisions['left'] = True
                rect.left = collision_tile.rect.right
    if move[1] != 0:
        rect.y += move[1]
        collision_tile = collision_test(rect, physics_map)
        if collision_tile:
            if move[1] > 0:
                collisions['bottom'] = True
                rect.bottom = collision_tile.rect.top
            else:
                collisions['top'] = True
                rect.top = collision_tile.rect.bottom
    return collisions


def interaction(rect, physics_map):
    physics_map.sort(key=lambda a: (a.rect.x - rect.center[0]) ** 2 + (a.rect.y - rect.center[1]) ** 2)
    for i in physics_map:
        if i.rect_for_interaction.colliderect(rect) and i.hp > 0:
            return i
    return None


def roll(a, b, dx=1, dy=1):
    shape = a.shape[:-2] + ((a.shape[-2] - b.shape[-2]) // dy + 1,) + ((a.shape[-1] - b.shape[-1]) // dx + 1,) + b.shape
    strides = a.strides[:-2] + (a.strides[-2] * dy,) + (a.strides[-1] * dx,) + a.strides[-2:]
    return np.lib.stride_tricks.as_strided(a, shape=(shape[0], shape[1], shape[2], shape[3]), strides=strides).reshape(
        (shape[0], shape[1], shape[2] * shape[3]))


class GameManager:
    def __init__(self, screen):
        self.statistics = ['time', 'fire_level', 0, 0]

        self.screen = screen
        self.level = Level(self)
        self.sounds = {'axe': [pygame.mixer.Sound(f'music/axe/{i + 1}.ogg') for i in range(5)]}
        self.icons = {'log': pygame.image.load('data/icons/log.png').convert_alpha(),
                      'time': pygame.image.load('data/icons/time.png').convert_alpha(), }
        self.fps_font = pygame.font.Font(FONT, 26)
        self.interface_font = pygame.font.Font(FONT, 45)

        self.weather_manager = Weather(self, self.screen)

        self.np_arr_scale = 24
        self.player_im_arr = [pygame.image.load(f'data/player{i + 1}.png').convert_alpha() for i in range(3)]
        self.player_im_counter = 0
        self.player_is_go = False
        self.player_is_right = True
        self.player_rect = self.player_im_arr[0].get_rect()
        # self.player_rect.x = WIDTH * SCALE // 2 - 30
        # self.player_rect.y = HEIGHT * SCALE // 2 - 30
        self.player_rect.x = self.level.level_center[0] * WIDTH + WIDTH // 2 - 30
        self.player_rect.y = self.level.level_center[1] * HEIGHT + HEIGHT // 2 - 30
        self.scroll = [self.player_rect.x - WIDTH // 2, self.player_rect.y - HEIGHT // 2]
        self.player_collision_rect = pygame.Rect(self.player_rect.x + 1 * 3, self.player_rect.y + 6 * 3, 4 * 3, 3 * 3)
        self.budget = 0
        self.PLAYER_STAMINA = 120
        self.player_stamina = self.PLAYER_STAMINA
        self.shift = False
        self.fire = Fire(self)
        self.indicator = Indicator(self.fire, self.screen)
        # self.tree_arr = []
        # tree_arr = [
        #     Tree(random.randint(20, WIDTH * SCALE // self.np_arr_scale * self.np_arr_scale - 20),
        #          random.randint(20, WIDTH * SCALE // self.np_arr_scale * self.np_arr_scale - 20))
        #     for _ in range(10000)]
        # tree_arr_helper = set()
        # for i in tree_arr:
        #     if (i.x, i.y) not in tree_arr_helper:
        #         self.tree_arr.append(i)
        #         for j in range(-2, 2):
        #             for q in range(-2, 2):
        #                 tree_arr_helper.add((i.x + j * self.np_arr_scale, i.y + q * self.np_arr_scale))
        #
        # i = 0
        # while i < len(self.tree_arr) - 1:
        #     if approximate_comparison(self.tree_arr[i].x, self.tree_arr[i + 1].x, 48) and \
        #             approximate_comparison(self.tree_arr[i].y, self.tree_arr[i + 1].y, 48):
        #         self.tree_arr.pop(i)
        #         i -= 1
        #     i += 1
        # i = 0
        # while i < len(self.tree_arr):
        #     if approximate_comparison(self.tree_arr[i].x, WIDTH * SCALE // 2, 80) and \
        #             approximate_comparison(self.tree_arr[i].y, HEIGHT * SCALE // 2, 80):
        #         self.tree_arr.pop(i)
        #         i -= 1
        #     i += 1
        # self.tree_arr.sort(key=lambda a: a.y)
        # self.tree_arr_np = np.empty(shape=(HEIGHT * SCALE // self.np_arr_scale,
        #                                    (WIDTH * SCALE) // self.np_arr_scale), dtype=object)
        # for i in self.tree_arr:
        #     try:
        #         self.tree_arr_np[i.y // self.np_arr_scale, i.x // self.np_arr_scale] = i
        #     except IndexError:
        #         pass
        #
        # self.cut_tree_arr = roll(self.tree_arr_np,
        #                          np.array([[0 for _ in range(int((WIDTH * 1.2) // self.np_arr_scale))] for _ in
        #                                    range(int((HEIGHT * 1.4) // self.np_arr_scale))]))

        self.footprint_arr = []
        self.fps_counter = 0
        self.fps_counter_2 = 0

    def paint_string(self, text, x, y, color, font, centering=True, dop_im=None):
        text = font.render(text, True, color)
        if dop_im is not None:
            self.screen.blit(dop_im, (x, y))
            self.screen.blit(text, (x + dop_im.get_width() + 10, y - 12))
        else:
            if centering:
                self.screen.blit(text, (x - text.get_width() // 2, y - 12))
            else:
                self.screen.blit(text, (x, y - 12))

    def paint_player(self):
        if self.player_is_go:
            self.player_im_counter += 1
        self.player_im_counter %= len(self.player_im_arr) * 10
        im = self.player_im_arr[self.player_im_counter // 10]
        if self.player_is_right:
            im = pygame.transform.flip(im, True, False)
        self.screen.blit(im, (self.player_rect.x - self.scroll[0], self.player_rect.y - self.scroll[1]))

    def movement(self):
        keys = pygame.key.get_pressed()
        move = [0, 0]
        if keys[pygame.K_LSHIFT] and int(self.player_stamina) == self.PLAYER_STAMINA:
            self.player_stamina = self.PLAYER_STAMINA
            self.shift = True
        if self.player_stamina > 0 and self.shift:
            self.player_stamina -= 1.2
            speed = SHIFT_SPEED
            self.shift = True
        else:
            self.shift = False
            speed = SPEED
        if self.player_stamina < self.PLAYER_STAMINA and not self.shift:
            self.player_stamina += 0.4
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move[1] += -speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move[1] += speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move[0] += -speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move[0] += speed
        if not move[0] and not move[1]:
            self.player_is_go = False
            self.player_im_counter = 0
        else:
            self.player_is_go = True
            if move[0] in (SPEED, SHIFT_SPEED):
                self.player_is_right = True
            elif move[0] in (-SPEED, -SHIFT_SPEED):
                self.player_is_right = False
        # physics(
        #     self.player_collision_rect, move,
        #     [i for i in self.cut_tree_arr[(self.player_rect.y - int(HEIGHT * 0.7)) // self.np_arr_scale,
        #                                   (self.player_rect.x - int(WIDTH * 0.6)) // self.np_arr_scale]
        #      if i is not None])
        physics(
            self.player_collision_rect, move, self.level.physics_arr)
        self.player_rect.x = self.player_collision_rect.x - 1 * 3
        self.player_rect.y = self.player_collision_rect.y - 7 * 3

    def interaction_controller(self):
        if self.fps_counter_2 > 0:
            self.fps_counter_2 -= 1
        else:
            self.fps_counter_2 = 0
        # tree = interaction(self.player_rect,
        #                    [i for i in self.cut_tree_arr[(self.player_rect.y - int(HEIGHT * 0.7)) // self.np_arr_scale,
        #                                                  (self.player_rect.x - int(WIDTH * 0.6)) // self.np_arr_scale]
        #                     if i is not None])
        tree = interaction(self.player_rect, self.level.physics_arr)
        if tree is not None:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e] and not self.fps_counter_2:
                self.fps_counter_2 = 50
                tree.hp -= 1
                self.sounds['axe'][random.randrange(len(self.sounds['axe']))].play()

    def paint_bar(self, MAX_VALUE, value, width, height, pos, color):
        pygame.draw.line(self.screen, (0, 0, 0),
                         (WIDTH // 2 - width // 2 - 3, pos[1]),
                         (WIDTH // 2 + width // 2 + 3, pos[1]), height + 6)
        pygame.draw.line(self.screen, color,
                         (WIDTH // 2 - width // 2, pos[1]),
                         (WIDTH // 2 - width // 2 + width / MAX_VALUE * value, pos[1]), height)

    def paint_interface(self, clock, start_time):
        self.paint_string(str(int(clock.get_fps())), WIDTH - 35, 10, (0, 103, 155), self.fps_font)
        self.paint_string(f'{int(time.time() - start_time) // 3600 % 60:02}:'
                          f'{int(time.time() - start_time) // 60 % 60:02}:'
                          f'{int(time.time() - start_time) % 60:02}',
                          10, 10, (0, 203, 255), self.interface_font, False, self.icons['time'])
        self.statistics[0] = time.time() - start_time
        self.paint_string(str(self.budget), 10, 50, (0, 203, 255), self.interface_font, False, self.icons['log'])
        self.paint_bar(self.PLAYER_STAMINA, self.player_stamina, 200, 20, (WIDTH // 2, 50), 'blue')
        self.paint_string(f'{round(self.fire.hp)}/{round(self.fire.HP)}', WIDTH // 2, 16, 'white', self.fps_font)

    def paint(self):
        self.statistics[1] = round(self.fire.HP)
        self.fps_counter += 1
        self.fps_counter %= 60
        if self.fps_counter % 20 == 0 and self.player_is_go:
            self.footprint_arr.append(
                Footprint(self.player_collision_rect.center[0], self.player_collision_rect.center[1]))
        self.movement()
        self.interaction_controller()
        self.scroll[0] += round((self.player_rect.x - self.scroll[0] - WIDTH // 2) / 20, 3)
        self.scroll[1] += round((self.player_rect.y - self.scroll[1] - HEIGHT // 2) / 20, 3)
        # for i, el in sorted(enumerate(self.tree_arr), reverse=True):
        #     if el.hp <= 0:
        #         self.tree_arr.pop(i)
        # self.tree_arr.sort(key=lambda a: a.y)
        # l, r = bin_search_range(self.tree_arr, self.player_rect.y - int(HEIGHT * 0.7),
        #                         self.player_rect.y + int(HEIGHT * 0.6))
        # cut_tree_arr = self.tree_arr[l:r]
        # cut_tree_arr.sort(key=lambda a: a.x)
        # l, r = bin_search_range(cut_tree_arr, self.player_rect.x - int(WIDTH * 0.6),
        #                         self.player_rect.x + int(WIDTH * 0.6), True)
        # cut_tree_arr = cut_tree_arr[l:r]
        # cut_tree_arr.sort(key=lambda a: a.y)
        # for i in self.cut_tree_arr[(self.player_rect.y - int(HEIGHT * 0.7)) // self.np_arr_scale,
        #                            (self.player_rect.x - int(WIDTH * 0.6)) // self.np_arr_scale]:
        #     if i is not None:
        #         i.paint_shadow(self.screen, self.scroll)
        self.level.paint_shadows()
        for i, el in sorted(enumerate(self.footprint_arr), reverse=True):
            el.paint(self.screen, self.scroll, self.weather_manager.snow_counter > 0)
            if el.condition <= 0:
                self.footprint_arr.pop(i)
        # f = False
        # for el in self.cut_tree_arr[(self.player_rect.y - int(HEIGHT * 0.7)) // self.np_arr_scale,
        #                             (self.player_rect.x - int(WIDTH * 0.6)) // self.np_arr_scale]:
        #     if el is not None:
        #         if el.y + el.im.get_height() > self.player_rect.y + self.player_rect.height + 3 and not f:
        #             self.paint_player()
        #             f = True
        #         el.paint(self.screen, self.scroll, self)
        self.level.paint()

        self.fire.paint(self.screen, self.scroll)
        pygame.gfxdraw.polygon(self.screen, ((-1, -1), (WIDTH + 1, 0), (WIDTH + 1, HEIGHT + 1), (0, HEIGHT + 1)),
                               (0, 0, 0))
        self.weather_manager.paint()
        self.fire.paint_hp()
        self.indicator.paint(self.scroll, math.sqrt(
            (self.fire.x - self.player_rect.x) ** 2 + (self.fire.y - self.player_rect.y) ** 2) > HEIGHT // 2)


def collision_test(rect, map):
    for tile in map:
        if tile is not None:
            if tile.rect.colliderect(rect):
                return tile
    return None
