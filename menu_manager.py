from gui import Button, Slider
from settings import *


def menu_movement(arr, up=True):
    if up:
        arr[1] -= 1
        if arr[1] < 0:
            arr[1] = len(arr[0]) - 1
    else:
        arr[1] += 1
        if arr[1] > len(arr[0]) - 1:
            arr[1] = 0
    return arr


def setting_cursor(arr):
    for i in range(len(arr[0])):
        arr[0][i].on = False
    arr[0][arr[1]].on = True


class MenuManager:
    def __init__(self, screen):
        self.statistics_text = None
        self.screen = screen
        self.condition = 'menu'

        self.font_h1 = pygame.font.Font(FONT, 40)
        self.font_h2 = pygame.font.Font(FONT, 30)

        self.menu_buttons = [[Button(WIDTH // 2, HEIGHT // 2 - 150, 'Старт', (0, 103, 155), (0, 203, 255), 50, True),
                              Button(WIDTH // 2, HEIGHT // 2 - 50, 'Настройки карты', (0, 103, 155), (0, 203, 255), 50,
                                     True),
                              Button(WIDTH // 2, HEIGHT // 2 + 50, 'Статистика', (0, 103, 155), (0, 203, 255), 50),
                              Button(WIDTH // 2, HEIGHT // 2 + 150, 'Выйти', (0, 103, 155), (0, 203, 255), 50)],
                             0]
        self.stop_buttons = [
            [Button(WIDTH // 2, HEIGHT // 2 - 110, 'Продолжить', (0, 103, 155), (0, 203, 255), 50, True),
             Button(WIDTH // 2, HEIGHT // 2 - 10, 'Перезапустить', (0, 103, 155), (0, 203, 255), 50),
             Button(WIDTH // 2, HEIGHT // 2 + 90, 'Выйти в меню', (0, 103, 155), (0, 203, 255), 50)],
            0]
        self.statistics_button = Button(WIDTH // 2, HEIGHT - 50, 'Назад', (0, 103, 155), (0, 203, 255), 50, True)
        self.settings_manager = {
            'level_length_slider': Slider(WIDTH // 2, 200, 300, 20, 30, 300, (0, 103, 155), (0, 203, 255), 30)}
        self.pause_time = 0

    def event_controller(self, event, func, display):
        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_RETURN:
                    if self.condition == 'menu':
                        match self.menu_buttons[0][self.menu_buttons[1]].text:
                            case 'Старт':
                                self.condition = 'in_game'
                                return func(display)
                            case 'Настройки карты':
                                self.condition = 'settings'
                            case 'Статистика':
                                self.condition = 'statistics'
                                with open('statistics.txt', 'r') as f:
                                    self.statistics_text = f.read().split('\n')
                            case 'Выйти':
                                return 'exit'
                    elif self.condition == 'statistics':
                        self.condition = 'menu'
                    elif self.condition == 'stop':
                        match self.stop_buttons[0][self.stop_buttons[1]].text:
                            case 'Продолжить':
                                self.condition = 'in_game'
                                return 'p_t', time.time() - self.pause_time
                            case 'Выйти в меню':
                                self.condition = 'menu'
                                self.stop_buttons[1] = 0
                                return 'ex'
                            case 'Перезапустить':
                                self.stop_buttons[1] = 0
                                self.condition = 'in_game'
                                return 'rest'
                case pygame.K_UP:
                    if self.condition == 'menu':
                        self.menu_buttons = menu_movement(self.menu_buttons)
                    elif self.condition == 'stop':
                        self.stop_buttons = menu_movement(self.stop_buttons)
                case pygame.K_DOWN:
                    if self.condition == 'menu':
                        self.menu_buttons = menu_movement(self.menu_buttons, False)
                    elif self.condition == 'stop':
                        self.stop_buttons = menu_movement(self.stop_buttons, False)
                case pygame.K_ESCAPE:
                    if self.condition == 'in_game':
                        self.pause_time = time.time()
                        self.condition = 'stop'
                    elif self.condition == 'stop':
                        self.condition = 'in_game'
                        return 'p_t', time.time() - self.pause_time

        if self.condition == 'menu':
            setting_cursor(self.menu_buttons)
        elif self.condition == 'stop':
            setting_cursor(self.stop_buttons)

    def paint(self):
        match self.condition:
            case 'menu':
                for i in self.menu_buttons[0]:
                    i.paint(self.screen)
            case 'statistics':
                self.paint_statistics()
                self.statistics_button.paint(self.screen)
            case 'stop':
                for i in self.stop_buttons[0]:
                    i.paint(self.screen)
            case 'settings':
                for i in self.settings_manager:
                    self.settings_manager[i].paint(self.screen)

    def paint_statistics(self):
        text = self.font_h1.render('Максимальные показатели:', True, (0, 103, 155))
        self.screen.blit(text, (10, 20))
        dis = 8
        for i, text in enumerate(['Время',
                                  'Уровень костра',
                                  'Количество набранных бревен за один заход',
                                  'Количество срубленных деревьев']):
            text = self.font_h2.render(text, True, (0, 103, 155))
            self.screen.blit(text, (20, (dis + text.get_height()) * i + 70))
            text1 = self.font_h2.render(self.statistics_text[i], True, (0, 203, 255))
            self.screen.blit(text1, (750, (dis + text.get_height()) * i + 70))
