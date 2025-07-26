#!/usr/bin/env python3
"""
Простий тест без GUI компонентів
"""

def test_basic_imports():
    """Тестування базових імпортів"""
    try:
        print("Тестування імпортів...")
        
        # Тест telethon
        from telethon import TelegramClient
        print("✓ telethon успішно імпортовано")
        
        # Тест конфігурації
        from telegram_config import TelegramConfig
        config = TelegramConfig()
        print("✓ telegram_config успішно імпортовано та створено")
        
        # Тест методів конфігурації
        config.set_api_id("test123")
        api_id = config.get_api_id()
        if api_id == "test123":
            print("✓ Методи конфігурації працюють")
        else:
            print(f"✗ Помилка: очікувалось 'test123', отримано '{api_id}'")
            return False
        
        # Тест tkinter (без створення вікон)
        import tkinter
        print("✓ tkinter доступний")
        
        return True
        
    except Exception as e:
        print(f"✗ Помилка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск простих тестів...\n")
    
    if test_basic_imports():
        print("\n🎉 Всі базові тести пройдено!")
        print("\n📋 Структура проекту:")
        print("  - telegram_client.py - основний файл клієнта")
        print("  - telegram_config.py - файл конфігурації")
        print("  - TELEGRAM_CLIENT_README.md - документація")
        print("\n✨ Telegram клієнт готовий до використання!")
    else:
        print("\n❌ Деякі тести не пройдено")