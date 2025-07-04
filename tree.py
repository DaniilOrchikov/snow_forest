from settings import *
from constants import *


class Tree:
    im_arr = [pygame.image.load(f'data/tree_{i}.png') for i in range(6)]
    shadow_im_arr = [pygame.image.load(f'data/tree_shadow_{i}.png') for i in range(6)]
    stump_im_arr = [pygame.image.load(f'data/stump_{i}.png') for i in range(6)]

    def __init__(self, x, y):
        rand_ind = random.randrange(0, 6)
        self.im = Tree.im_arr[rand_ind].convert_alpha()
        self.stump_im = Tree.stump_im_arr[rand_ind].convert_alpha()
        self.shadow_im = Tree.shadow_im_arr[rand_ind].convert_alpha()
        self.x, self.y = x, y
        self.hp = random.randint(TREE_HP_MIN, TREE_HP_MAX)
        self.budget = self.hp + rand_ind % 3 + 1
        self.rect = pygame.Rect(
            self.x + self.im.get_width() // 2 - TREE_COLLISION_WIDTH // 2,
            self.y + self.im.get_height() - TREE_COLLISION_HEIGHT, 
            TREE_COLLISION_WIDTH, 
            TREE_COLLISION_HEIGHT
        )
        self.rect_for_interaction = pygame.Rect(
            self.x + self.im.get_width() // 2 - TREE_INTERACTION_WIDTH // 2,
            self.y + self.im.get_height() - TREE_INTERACTION_HEIGHT, 
            TREE_INTERACTION_WIDTH, 
            TREE_INTERACTION_HEIGHT
        )

    def paint_shadow(self, screen, scroll):
        if self.hp > 0:
            screen.blit(self.shadow_im, (self.x - scroll[0], self.y - scroll[1] + self.im.get_height() - 3))
        else:
            pass

    def paint(self, screen, scroll, manager):
        if self.hp > 0:
            screen.blit(self.im, (self.x - scroll[0], self.y - scroll[1]))
        else:
            # Проверяем, что еще не обработали это дерево
            if self.budget > 0:
                manager.statistics[3] += 1
                manager.budget += self.budget
                self.budget = 0
            screen.blit(self.stump_im, (self.rect_for_interaction.center[0] - scroll[0] - 3,
                                        self.rect_for_interaction.y - scroll[1] + 3))
        # pygame.draw.rect(screen, 'red',
        #                  (self.rect_for_interaction.x - scroll[0], self.rect_for_interaction.y - scroll[1],
        #                   self.rect_for_interaction.width, self.rect_for_interaction.height))
