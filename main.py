import sys

from menu_manager import MenuManager
from settings import *
from game_manager import GameManager


def start(display):
    game_manager = GameManager(display)
    start_time = time.time()
    return game_manager, start_time


def save_stats(game_manager):
    with open('statistics.txt', 'r') as f:
        file = f.read()[:-1].split('\n')
        t = list(map(int, file[0].split(':')))
        t = t[-1] + t[1] * 60 + t[0] * 3600
        file = list(map(int, file[1:]))
    with open('statistics.txt', 'w') as f:
        t = max(t, game_manager.statistics[0])
        t = f'{int(t) // 3600 % 60:02}:' + \
            f'{int(t) // 60 % 60:02}:' + \
            f'{int(t) % 60:02}'
        f.write(t + '\n')
        for i, el in enumerate(game_manager.statistics[1:]):
            if el >= file[i]:
                f.write(str(el) + '\n')
            else:
                f.write(str(file[i]) + '\n')


def main():
    pygame.init()

    display = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    menu_manager = MenuManager(display)
    pygame.mouse.set_visible(False)
    game_manager = None
    start_time = None

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return
            args = menu_manager.event_controller(event, start, display)
            if args is not None:
                if len(args) == 2 and args[0] not in ['p_t'] and isinstance(args, tuple):
                    game_manager, start_time = args
                    break
                elif args == 'exit':
                    return
                elif args[0] == 'p_t':
                    start_time += args[1]
                elif args == 'ex':
                    save_stats(game_manager)
                elif args == 'rest':
                    game_manager, start_time = start(display)
                    break

        display.fill('white')
        if menu_manager.condition == 'in_game':
            game_manager.paint()
            game_manager.paint_interface(clock, start_time)

            if game_manager.fire.hp < 0:  # проигрыш
                save_stats(game_manager)
                game_manager, start_time = start(display)

        menu_manager.paint()

        clock.tick(FPS)
        pygame.display.flip()


if __name__ == '__main__':
    main()
    pygame.quit()
    sys.exit()
