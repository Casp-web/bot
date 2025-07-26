#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки основного функціоналу Telegram клієнта
"""

import sys
import os

# Додаємо поточну директорію до шляху
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Тестування імпортів"""
    try:
        import tkinter as tk
        print("✓ tkinter успішно імпортовано")
        
        from telethon import TelegramClient
        print("✓ telethon успішно імпортовано")
        
        from telegram_config import TelegramConfig
        print("✓ telegram_config успішно імпортовано")
        
        # Тест створення конфігурації
        config = TelegramConfig()
        print("✓ TelegramConfig успішно створено")
        
        # Тест методів конфігурації
        config.set_api_id("123456")
        api_id = config.get_api_id()
        assert api_id == "123456", f"Очікувалось '123456', отримано '{api_id}'"
        print("✓ Методи конфігурації працюють")
        
        return True
        
    except ImportError as e:
        print(f"✗ Помилка імпорту: {e}")
        return False
    except Exception as e:
        print(f"✗ Помилка: {e}")
        return False

def test_tkinter():
    """Тестування tkinter без відображення вікна"""
    try:
        import tkinter as tk
        
        # Створюємо root вікно
        root = tk.Tk()
        root.withdraw()  # Приховуємо вікно
        
        # Тестуємо створення основних віджетів
        frame = tk.Frame(root)
        label = tk.Label(frame, text="Test")
        entry = tk.Entry(frame)
        button = tk.Button(frame, text="Test Button")
        
        print("✓ Основні tkinter віджети створено успішно")
        
        # Закриваємо вікно
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ Помилка tkinter: {e}")
        return False

def test_telegram_client_class():
    """Тестування класу TelegramClientGUI без запуску GUI"""
    try:
        import tkinter as tk
        
        # Імпортуємо наш клас
        from telegram_client import TelegramClientGUI
        
        # Створюємо root але не показуємо його
        root = tk.Tk()
        root.withdraw()
        
        # Тестуємо створення екземпляру класу
        # Але не запускаємо mainloop
        app = TelegramClientGUI(root)
        
        print("✓ TelegramClientGUI успішно створено")
        
        # Тестуємо методи конфігурації
        app.config.set_api_id("test_id")
        test_id = app.config.get_api_id()
        assert test_id == "test_id", f"Очікувалось 'test_id', отримано '{test_id}'"
        
        print("✓ Методи TelegramClientGUI працюють")
        
        # Закриваємо
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ Помилка TelegramClientGUI: {e}")
        return False

def main():
    """Основна функція тестування"""
    print("🚀 Запуск тестів Telegram клієнта...\n")
    
    tests = [
        ("Тестування імпортів", test_imports),
        ("Тестування tkinter", test_tkinter),
        ("Тестування TelegramClientGUI", test_telegram_client_class),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"📋 {test_name}:")
        if test_func():
            passed += 1
            print("✅ ПРОЙДЕНО\n")
        else:
            print("❌ НЕ ПРОЙДЕНО\n")
    
    print(f"📊 Результати: {passed}/{total} тестів пройдено")
    
    if passed == total:
        print("🎉 Всі тести пройдено успішно!")
        print("\n📝 Для запуску Telegram клієнта використовуйте:")
        print("   source telegram_client_env/bin/activate")
        print("   python telegram_client.py")
        print("\n⚠️  Не забудьте отримати API credentials на https://my.telegram.org/")
    else:
        print("⚠️  Деякі тести не пройдено. Перевірте помилки вище.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)