#!/bin/bash

# YouTube Telegram Bot - Автоматичний скрипт деплою
# Автор: YouTube Bot Team
# Версія: 1.0

set -e  # Зупинити виконання при помилці

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функція для виводу кольорових повідомлень
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE} $1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Перевірка операційної системи
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v apt-get >/dev/null 2>&1; then
            DISTRO="debian"
        elif command -v yum >/dev/null 2>&1; then
            DISTRO="redhat"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        print_error "Непідтримувана операційна система: $OSTYPE"
        exit 1
    fi
    print_status "Виявлено ОС: $OS ($DISTRO)"
}

# Перевірка системних вимог
check_requirements() {
    print_header "ПЕРЕВІРКА СИСТЕМНИХ ВИМОГ"
    
    # Перевірка Python
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python встановлено: $PYTHON_VERSION"
    else
        print_error "Python 3 не знайдено. Будь ласка, встановіть Python 3.9+"
        exit 1
    fi
    
    # Перевірка pip
    if command -v pip3 >/dev/null 2>&1; then
        print_success "pip3 доступний"
    else
        print_error "pip3 не знайдено"
        exit 1
    fi
    
    # Перевірка Git
    if command -v git >/dev/null 2>&1; then
        print_success "Git встановлено"
    else
        print_error "Git не знайдено. Будь ласка, встановіть Git"
        exit 1
    fi
    
    # Перевірка FFmpeg
    if command -v ffmpeg >/dev/null 2>&1; then
        print_success "FFmpeg встановлено"
    else
        print_warning "FFmpeg не знайдено. Буде встановлено автоматично"
        install_ffmpeg
    fi
}

# Встановлення FFmpeg
install_ffmpeg() {
    print_status "Встановлення FFmpeg..."
    
    if [[ "$OS" == "linux" ]]; then
        if [[ "$DISTRO" == "debian" ]]; then
            sudo apt update
            sudo apt install -y ffmpeg
        elif [[ "$DISTRO" == "redhat" ]]; then
            sudo yum install -y ffmpeg
        fi
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew >/dev/null 2>&1; then
            brew install ffmpeg
        else
            print_error "Homebrew не знайдено. Встановіть FFmpeg вручну"
            exit 1
        fi
    fi
    
    print_success "FFmpeg встановлено"
}

# Створення віртуального середовища
setup_venv() {
    print_header "НАЛАШТУВАННЯ ВІРТУАЛЬНОГО СЕРЕДОВИЩА"
    
    if [[ -d "venv" ]]; then
        print_warning "Віртуальне середовище вже існує"
        read -p "Перестворити? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
        else
            return
        fi
    fi
    
    print_status "Створення віртуального середовища..."
    python3 -m venv venv
    
    print_status "Активація віртуального середовища..."
    source venv/bin/activate
    
    print_status "Оновлення pip..."
    pip install --upgrade pip
    
    print_status "Встановлення залежностей..."
    pip install -r requirements.txt
    
    print_success "Віртуальне середовище налаштовано"
}

# Налаштування конфігурації
setup_config() {
    print_header "НАЛАШТУВАННЯ КОНФІГУРАЦІЇ"
    
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
            print_success "Створено файл .env з шаблону"
        else
            print_error "Файл .env.example не знайдено"
            exit 1
        fi
    else
        print_warning "Файл .env вже існує"
    fi
    
    print_warning "ВАЖЛИВО: Відредагуйте файл .env та вкажіть ваш BOT_TOKEN"
    print_status "Файл конфігурації: $(pwd)/.env"
    
    # Перевірка чи встановлено токен
    if grep -q "your_telegram_bot_token_here" .env; then
        print_error "Будь ласка, замініть 'your_telegram_bot_token_here' на реальний токен бота"
        print_status "Отримати токен можна у @BotFather в Telegram"
        
        read -p "Відкрити файл .env для редагування? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    fi
}

# Ініціалізація бази даних
init_database() {
    print_header "ІНІЦІАЛІЗАЦІЯ БАЗИ ДАНИХ"
    
    print_status "Створення директорій..."
    mkdir -p database downloads temp logs
    
    print_status "Ініціалізація бази даних..."
    source venv/bin/activate
    python3 -c "
import asyncio
import sys
sys.path.append('.')
from database.models.base import init_db

async def main():
    try:
        await init_db()
        print('База даних успішно ініціалізована!')
    except Exception as e:
        print(f'Помилка ініціалізації бази даних: {e}')
        sys.exit(1)

asyncio.run(main())
"
    
    print_success "База даних ініціалізована"
}

# Тестування конфігурації
test_setup() {
    print_header "ТЕСТУВАННЯ НАЛАШТУВАНЬ"
    
    source venv/bin/activate
    
    print_status "Тестування валідації URL..."
    python3 -c "
from utils.validators import URLValidator
validator = URLValidator()
test_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
if validator.is_valid_youtube_url(test_url):
    print('✅ Валідація URL працює')
else:
    print('❌ Проблема з валідацією URL')
"
    
    print_status "Перевірка імпортів..."
    python3 -c "
try:
    from bot.handlers import routers
    from downloader.services.youtube_service import YouTubeService
    from database.models.base import init_db
    print('✅ Всі модулі імпортуються коректно')
except ImportError as e:
    print(f'❌ Помилка імпорту: {e}')
    exit(1)
"
    
    print_success "Тестування завершено"
}

# Створення systemd сервісу (тільки для Linux)
create_systemd_service() {
    if [[ "$OS" != "linux" ]]; then
        return
    fi
    
    print_header "СТВОРЕННЯ SYSTEMD СЕРВІСУ"
    
    read -p "Створити systemd сервіс для автозапуску? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return
    fi
    
    SERVICE_NAME="youtube-telegram-bot"
    SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
    CURRENT_USER=$(whoami)
    CURRENT_DIR=$(pwd)
    
    print_status "Створення сервісу $SERVICE_NAME..."
    
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=YouTube Telegram Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/venv/bin
ExecStart=$CURRENT_DIR/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME
    
    print_success "Systemd сервіс створено: $SERVICE_NAME"
    print_status "Команди управління:"
    print_status "  Запуск: sudo systemctl start $SERVICE_NAME"
    print_status "  Зупинка: sudo systemctl stop $SERVICE_NAME"
    print_status "  Статус: sudo systemctl status $SERVICE_NAME"
    print_status "  Логи: sudo journalctl -u $SERVICE_NAME -f"
}

# Фінальні інструкції
show_final_instructions() {
    print_header "ДЕПЛОЙ ЗАВЕРШЕНО"
    
    print_success "YouTube Telegram Bot успішно встановлено!"
    echo
    print_status "Наступні кроки:"
    echo "1. Переконайтеся, що в файлі .env вказано правильний BOT_TOKEN"
    echo "2. Запустіть бота командою:"
    echo -e "   ${CYAN}source venv/bin/activate && python main.py${NC}"
    echo "3. Для запуску веб-панелі (в новому терміналі):"
    echo -e "   ${CYAN}source venv/bin/activate && python start_web_panel.py${NC}"
    echo "4. Веб-панель буде доступна за адресою: http://localhost:5000"
    echo "   Логін: admin, Пароль: admin123"
    echo
    print_status "Корисні файли:"
    echo "• Конфігурація: .env"
    echo "• Логи бота: logs/bot.log"
    echo "• База даних: database/bot.db"
    echo "• Завантаження: downloads/"
    echo
    print_status "Документація:"
    echo "• Повний гід: SETUP_GUIDE.md"
    echo "• Веб-панель: WEB_PANEL_GUIDE.md"
    echo "• Основна документація: README.md"
    echo
    print_warning "Не забудьте змінити пароль адміністратора веб-панелі в продакшені!"
}

# Головна функція
main() {
    print_header "YOUTUBE TELEGRAM BOT - АВТОМАТИЧНИЙ ДЕПЛОЙ"
    echo -e "${CYAN}Цей скрипт автоматично налаштує YouTube Telegram Bot${NC}"
    echo
    
    read -p "Продовжити встановлення? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_status "Встановлення скасовано"
        exit 0
    fi
    
    detect_os
    check_requirements
    setup_venv
    setup_config
    init_database
    test_setup
    create_systemd_service
    show_final_instructions
    
    print_success "Деплой завершено успішно! 🎉"
}

# Обробка помилок
trap 'print_error "Сталася помилка на рядку $LINENO. Деплой перервано."; exit 1' ERR

# Запуск головної функції
main "$@"