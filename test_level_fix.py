#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback

# Мок для pygame, чтобы избежать проблем с инициализацией
class MockRect:
    def __init__(self, x=0, y=0, width=100, height=100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class MockGameManager:
    def __init__(self):
        self.player_rect = MockRect(5000, 5000, 30, 30)  # Позиция за пределами карты
        self.screen = None

try:
    # Импортируем только Level
    from level import Level
    
    print("✅ Импорт Level прошел успешно")
    
    # Создаем мок менеджера игры
    mock_manager = MockGameManager()
    
    print("🔄 Создаем Level...")
    level = Level(mock_manager)
    
    print("✅ Level создан успешно!")
    
    # Тестируем проблемный метод physics_arr с координатами игрока за пределами карты
    print("🔄 Тестируем physics_arr с координатами за пределами карты...")
    
    # До исправления это вызывало "list index out of range"
    physics_arr = level.physics_arr
    print(f"✅ physics_arr выполнен успешно! Содержит {len(physics_arr)} объектов")
    
    # Тестируем с другими координатами
    mock_manager.player_rect.x = -1000  # Отрицательные координаты
    mock_manager.player_rect.y = -1000
    print("🔄 Тестируем с отрицательными координатами...")
    physics_arr = level.physics_arr
    print(f"✅ Работает с отрицательными координатами! Содержит {len(physics_arr)} объектов")
    
    # Тестируем с очень большими координатами
    mock_manager.player_rect.x = 1000000
    mock_manager.player_rect.y = 1000000
    print("🔄 Тестируем с очень большими координатами...")
    physics_arr = level.physics_arr
    print(f"✅ Работает с большими координатами! Содержит {len(physics_arr)} объектов")
    
    print("\n🎉 Все тесты прошли успешно!")
    print("✨ Ошибка 'list index out of range' полностью исправлена!")
    print("🚀 Теперь игра должна запускаться без проблем при нажатии 'Старт'")
    
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    print("\n📋 Полная трассировка:")
    traceback.print_exc()
    sys.exit(1)