from game_screen import GameScreen
from settings import *


class Level:
    def __init__(self, manager):
        self.screen = manager.screen
        self.manager = manager
        self.level = [[None for _ in range(101)] for _ in range(101)]
        self.level_center = len(self.level) // 2, len(self.level[0]) // 2
        self.set_of_screen_pos = set()
        for i in range(-1, 2):
            for j in range(-1, 2):
                self.create_screen((self.level_center[0] + i, self.level_center[1] + j))

        i = 0
        while i < len(self.level[self.level_center[0]][self.level_center[1]].tree_arr):
            tree = self.level[self.level_center[0]][self.level_center[1]].tree_arr[i]
            if math.sqrt(((tree.x + tree.im.get_width() // 2) - (self.level_center[0] * WIDTH + WIDTH // 2)) ** 2 +
                ((tree.y + tree.im.get_height() // 2) - (self.level_center[1] * HEIGHT + HEIGHT // 2)) ** 2) < 200:
                self.level[self.level_center[0]][self.level_center[1]].tree_arr.pop(i)
                i -= 1
            i += 1
        self.level[self.level_center[0]][self.level_center[1]].tree_arr.sort(key=lambda a: a.y)

    def create_screen(self, pos: tuple):
        self.level[pos[1]][pos[0]] = GameScreen(*pos)
        self.set_of_screen_pos.add(pos)

    def paint_shadows(self):
        player_pos = self.manager.player_rect.x // WIDTH, self.manager.player_rect.y // HEIGHT
        for i in range(-1, 2):
            for j in range(-1, 2):
                pos = (player_pos[0] + i, player_pos[1] + j)
                if pos not in self.set_of_screen_pos:
                    self.create_screen(pos)
                self.level[pos[1]][pos[0]].paint_shadows(self.screen, self.manager.scroll)

    def paint(self):
        player_pos = self.manager.player_rect.x // WIDTH, self.manager.player_rect.y // HEIGHT
        for i in range(-1, 2):
            for j in range(-1, 2):
                pos = (player_pos[0] + i, player_pos[1] + j)
                if pos not in self.set_of_screen_pos:
                    self.create_screen(pos)
                self.level[pos[1]][pos[0]].paint(self.screen, self.manager.scroll, self.manager, (i, j) == (0, 0))

    @property
    def physics_arr(self):
        arr = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                game_screen = self.level[self.manager.player_rect.y // HEIGHT + i][
                    self.manager.player_rect.x // WIDTH + j]
                if game_screen is not None:
                    for tree in game_screen.tree_arr:
                        arr.append(tree)
        return arr
