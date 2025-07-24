# 🚀 Повний гід по налаштуванню YouTube Telegram Bot

## 📋 Зміст
1. [Системні вимоги](#системні-вимоги)
2. [Встановлення](#встановлення)
3. [Налаштування Telegram Bot](#налаштування-telegram-bot)
4. [Конфігурація YouTube](#конфігурація-youtube)
5. [Запуск проекту](#запуск-проекту)
6. [Веб-панель](#веб-панель)
7. [Вирішення проблем](#вирішення-проблем)

## 🖥️ Системні вимоги

### Операційна система
- Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- macOS 11+
- Windows 10+ (з WSL2)

### Програмне забезпечення
- **Python 3.9+** (рекомендовано 3.11+)
- **FFmpeg** (для обробки аудіо/відео)
- **Git** (для клонування репозиторію)
- **SQLite** (входить в Python)

## 📥 Встановлення

### 1. Клонування репозиторію
```bash
git clone https://github.com/Casp-web/bot.git
cd bot
git checkout cursor/youtube-595b
```

### 2. Встановлення Python залежностей
```bash
# Створення віртуального середовища
python3 -m venv venv

# Активація віртуального середовища
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Встановлення залежностей
pip install -r requirements.txt
```

### 3. Встановлення FFmpeg

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS:
```bash
brew install ffmpeg
```

#### Windows:
1. Завантажте FFmpeg з https://ffmpeg.org/download.html
2. Розпакуйте та додайте до PATH

## 🤖 Налаштування Telegram Bot

### 1. Створення бота в BotFather
1. Відкрийте Telegram та знайдіть `@BotFather`
2. Надішліть команду `/newbot`
3. Введіть назву вашого бота (наприклад: "My YouTube Downloader")
4. Введіть username бота (має закінчуватися на `bot`)
5. Скопіюйте отриманий токен

### 2. Налаштування конфігурації
```bash
# Копіюйте шаблон конфігурації
cp .env.example .env

# Відредагуйте файл .env
nano .env
```

Заповніть файл `.env`:
```env
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
BOT_NAME=YouTubeDownloaderBot

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./database/bot.db

# Redis Configuration (опціонально)
REDIS_URL=redis://localhost:6379/0

# Download Configuration
MAX_FILE_SIZE_MB=50
DOWNLOAD_PATH=./downloads
TEMP_PATH=./temp

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=./logs/bot.log

# YouTube Configuration
MAX_DURATION_MINUTES=60
QUALITY_VIDEO=720p
QUALITY_AUDIO=128kbps

# Rate Limiting
MAX_DOWNLOADS_PER_USER_HOUR=10
MAX_CONCURRENT_DOWNLOADS=5
```

## 🎬 Конфігурація YouTube

### Проблема з YouTube блокуванням
YouTube може блокувати запити від ботів. Для вирішення цієї проблеми:

#### Метод 1: Використання cookies (рекомендовано)
1. Встановіть розширення для браузера для експорту cookies
2. Увійдіть в свій YouTube акаунт
3. Експортуйте cookies в файл `cookies.txt`
4. Помістіть файл в корінь проекту

#### Метод 2: Альтернативні налаштування
Бот автоматично спробує альтернативні методи доступу до YouTube.

### Тестування YouTube функціональності
```bash
# Активуйте віртуальне середовище
source venv/bin/activate

# Запустіть тест
python test_youtube_urls.py
```

## 🚀 Запуск проекту

### 1. Ініціалізація бази даних
```bash
source venv/bin/activate
python -c "
import asyncio
from database.models.base import init_db
asyncio.run(init_db())
print('База даних ініціалізована!')
"
```

### 2. Запуск Telegram бота
```bash
source venv/bin/activate
python main.py
```

### 3. Запуск веб-панелі (опціонально)
У новому терміналі:
```bash
source venv/bin/activate
python start_web_panel.py
```

Веб-панель буде доступна за адресою: http://localhost:5000
- **Логін:** admin
- **Пароль:** admin123

## 🌐 Веб-панель

### Функції веб-панелі:
- 📊 **Dashboard** - статистика в реальному часі
- ⚙️ **Конфігурація** - налаштування бота
- 👥 **Користувачі** - управління користувачами
- 📥 **Завантаження** - моніторинг завантажень
- 📋 **Логи** - перегляд логів з фільтрацією

### Зміна пароля адміністратора:
```python
# В файлі web_panel/app.py знайдіть:
users = {
    'admin': generate_password_hash('admin123')  # Змініть пароль тут
}
```

## 🔧 Вирішення проблем

### Проблема: "ModuleNotFoundError"
```bash
# Переконайтеся, що віртуальне середовище активовано
source venv/bin/activate

# Переустановіть залежності
pip install -r requirements.txt
```

### Проблема: "FFmpeg not found"
```bash
# Перевірте чи встановлено FFmpeg
ffmpeg -version

# Якщо не встановлено - встановіть згідно інструкцій вище
```

### Проблема: "YouTube Sign in to confirm you're not a bot"
1. Використайте cookies (див. розділ "Конфігурація YouTube")
2. Спробуйте інше відео для тестування
3. Перевірте чи оновлено yt-dlp:
   ```bash
   pip install --upgrade yt-dlp
   ```

### Проблема: "Database locked"
```bash
# Зупиніть всі процеси бота
pkill -f "python main.py"

# Видаліть файл блокування
rm -f database/bot.db-journal

# Перезапустіть бота
python main.py
```

### Проблема: "Permission denied" для директорій
```bash
# Створіть необхідні директорії з правильними правами
mkdir -p downloads temp logs
chmod 755 downloads temp logs
```

## 📊 Моніторинг та логи

### Перегляд логів бота:
```bash
tail -f logs/bot.log
```

### Перегляд логів веб-панелі:
```bash
tail -f web_panel.log
```

### Очищення старих файлів:
```bash
# Очистити завантаження старше 7 днів
find downloads/ -type f -mtime +7 -delete

# Очистити тимчасові файли
rm -rf temp/*
```

## 🔄 Оновлення проекту

```bash
# Зупиніть бота
pkill -f "python main.py"

# Оновіть код
git pull origin cursor/youtube-595b

# Оновіть залежності
source venv/bin/activate
pip install -r requirements.txt

# Перезапустіть бота
python main.py
```

## 🛡️ Безпека

### Рекомендації:
1. **Змініть пароль веб-панелі** в продакшені
2. **Обмежте доступ до веб-панелі** через firewall
3. **Регулярно оновлюйте** залежності
4. **Використовуйте HTTPS** для веб-панелі в продакшені
5. **Створіть backup** бази даних

### Backup бази даних:
```bash
# Створення backup
cp database/bot.db database/bot_backup_$(date +%Y%m%d_%H%M%S).db

# Відновлення з backup
cp database/bot_backup_YYYYMMDD_HHMMSS.db database/bot.db
```

## 📞 Підтримка

### При виникненні проблем:
1. Перевірте логи: `tail -f logs/bot.log`
2. Запустіть тести: `python test_youtube_urls.py`
3. Перевірте конфігурацію: `cat .env`
4. Створіть issue на GitHub з детальним описом проблеми

### Корисні команди:
```bash
# Перевірка статусу процесів
ps aux | grep python

# Перевірка використання диску
df -h
du -sh downloads/ temp/ logs/

# Перевірка мережевих підключень
netstat -tulpn | grep :5000
```

---

## ✅ Чекліст запуску

- [ ] Python 3.9+ встановлено
- [ ] FFmpeg встановлено
- [ ] Репозиторій клоновано
- [ ] Віртуальне середовище створено
- [ ] Залежності встановлено
- [ ] Telegram бот створено в BotFather
- [ ] Файл .env налаштовано
- [ ] База даних ініціалізована
- [ ] Тести пройшли успішно
- [ ] Бот запущено
- [ ] Веб-панель працює (опціонально)

**🎉 Вітаємо! Ваш YouTube Telegram Bot готовий до роботи!**