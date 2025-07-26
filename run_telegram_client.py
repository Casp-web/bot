#!/usr/bin/env python3
"""
Скрипт запуску Telegram клієнта
"""
import sys
import subprocess
import os

def check_and_install_dependencies():
    """Перевірка та встановлення залежностей"""
    try:
        import telethon
        print("✓ Telethon вже встановлено")
        return True
    except ImportError:
        print("⚠️  Telethon не встановлено. Встановлюємо...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "telethon", "--break-system-packages"])
            print("✓ Telethon успішно встановлено")
            return True
        except subprocess.CalledProcessError:
            print("❌ Помилка встановлення telethon")
            return False

def check_tkinter():
    """Перевірка tkinter"""
    try:
        import tkinter
        print("✓ tkinter доступний")
        return True
    except ImportError:
        print("❌ tkinter не доступний. Встановіть python3-tk")
        return False

def main():
    """Основна функція"""
    print("🚀 Запуск Telegram клієнта...\n")
    
    # Перевірка tkinter
    if not check_tkinter():
        print("Для встановлення tkinter виконайте:")
        print("sudo apt install python3-tk")
        return False
    
    # Перевірка та встановлення telethon
    if not check_and_install_dependencies():
        return False
    
    # Перевірка наявності файлів
    required_files = ['telegram_client.py', 'telegram_config.py']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Файл {file} не знайдено")
            return False
    
    print("✓ Всі файли знайдено")
    
    # Запуск клієнта
    try:
        print("\n🎯 Запускаємо Telegram клієнт...")
        print("📝 Інструкції:")
        print("   1. Отримайте API credentials на https://my.telegram.org/")
        print("   2. Створіть нову програму в 'API Development tools'")
        print("   3. Скопіюйте API ID та API Hash")
        print("   4. Введіть їх у програмі та натисніть Connect")
        print("\n🚀 Запуск...")
        
        import telegram_client
        telegram_client.main()
        
    except KeyboardInterrupt:
        print("\n👋 Програма зупинена користувачем")
    except Exception as e:
        print(f"\n❌ Помилка запуску: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)