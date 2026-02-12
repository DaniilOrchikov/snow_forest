import pygame
import random
import time
import numpy as np
import pygame.gfxdraw
import math
import builtins as __builtin__
import traceback

WIDTH, HEIGHT = 300 * 3, 170 * 3
FPS = 60
SCALE = 10
SPEED = 1
SHIFT_SPEED = 3
MAP_TREE_COUNT = 200
DAY_CYCLE_SECONDS = 120
FIRE_LIGHT_RADIUS = 230
PLAYER_LIGHT_RADIUS = 180
PLAYER_LIGHT_DURATION = 10


def print(*args, **kwargs):
    args = list(args)
    args.append('------------- ')
    args.append(f'File "{traceback.StackSummary.extract(traceback.walk_stack(None))[1][0]}", line '
                f'{int(traceback.StackSummary.extract(traceback.walk_stack(None))[1][1])}')
    return __builtin__.print(*args, **kwargs)


FONT = 'LEngineer-Regular.otf'
