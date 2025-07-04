#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Запуск в безголовом режиме

import sys
import traceback

try:
    # Импортируем основные модули игры
    from level import Level
    from game_manager import GameManager
    import pygame
    
    print("✅ Импорт модулей прошел успешно")
    
    # Инициализируем pygame в безголовом режиме
    pygame.init()
    pygame.mixer.init()  # Инициализируем звуковой микшер
    display = pygame.display.set_mode((900, 510), pygame.HIDDEN)
    
    print("✅ Pygame инициализирован")
    
    # Пытаемся создать GameManager (это то, что происходит при нажатии "Старт")
    print("🔄 Создаем GameManager (эмулируем нажатие 'Старт')...")
    game_manager = GameManager(display)
    
    print("✅ GameManager создан успешно!")
    
    # Проверяем, что level создан правильно
    print("🔄 Проверяем уровень...")
    level = game_manager.level
    
    # Тестируем методы, которые мы исправили
    print("🔄 Тестируем physics_arr...")
    physics_arr = level.physics_arr
    print(f"✅ physics_arr содержит {len(physics_arr)} объектов")
    
    print("🔄 Тестируем paint_shadows...")
    level.paint_shadows()
    print("✅ paint_shadows выполнен без ошибок")
    
    print("🔄 Тестируем paint...")
    level.paint()
    print("✅ paint выполнен без ошибок")
    
    print("\n🎉 Все тесты прошли успешно! Ошибка 'list index out of range' исправлена!")
    
    pygame.quit()
    
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    print("\n📋 Полная трассировка:")
    traceback.print_exc()
    sys.exit(1)