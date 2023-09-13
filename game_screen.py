from numba import njit

from settings import *
from tree import Tree


@njit(fastmath=True, cache=True)
def approximate_comparison(x, y, shift):
    for q in range(-shift, shift):
        for h in range(-shift, shift):
            if x - q == y - h:
                return True
    return False


class GameScreen:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.np_arr_scale = 24
        self.tree_arr = []
        tree_arr = [
            Tree(random.randint(self.x * WIDTH, WIDTH + self.x * WIDTH),
                 random.randint(self.y * HEIGHT, HEIGHT + self.y * HEIGHT))
            for _ in range(200)]
        tree_arr_helper = set()
        for i in tree_arr:
            if (i.x, i.y) not in tree_arr_helper:
                self.tree_arr.append(i)
                for j in range(-2, 2):
                    for q in range(-2, 2):
                        tree_arr_helper.add((i.x + j * self.np_arr_scale, i.y + q * self.np_arr_scale))

        i = 0
        while i < len(self.tree_arr) - 1:
            if approximate_comparison(self.tree_arr[i].x, self.tree_arr[i + 1].x, 48) and \
                    approximate_comparison(self.tree_arr[i].y, self.tree_arr[i + 1].y, 48):
                self.tree_arr.pop(i)
                i -= 1
            i += 1

        self.tree_arr.sort(key=lambda a: a.y)

    def paint(self, screen, scroll, manager, center=False):
        f = True
        for el in self.tree_arr:
            if center:
                if el.y + el.im.get_height() > manager.player_rect.y + manager.player_rect.height and f:
                    manager.paint_player()
                    f = False
            else:
                f = False
            el.paint(screen, scroll, manager)
        if f:
            manager.paint_player()

    def paint_shadows(self, screen, scroll):
        for el in self.tree_arr:
            el.paint_shadow(screen, scroll)
