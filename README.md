# Telegram YouTube Downloader Bot

Цей проект складається з двох мікросервісів:

1. **Telegram Bot** (`bot/`) – взаємодіє з користувачем, надає клавіатуру вибору й відправляє файли.
2. **Downloader Service** (`services/downloader/`) – FastAPI-сервіс, що завантажує відео/аудіо з YouTube за допомогою `yt-dlp`.

## Швидкий старт

### Вимоги
* Python 3.10+
* `ffmpeg` – потрібен для конвертації аудіо.

### Встановлення
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Запуск Downloader Service
```bash
uvicorn services.downloader.app:app --host 0.0.0.0 --port 8000
```

### Запуск Telegram-бота

1. Задайте токен бота та адресу сервісу:**
```bash
export TELEGRAM_TOKEN="<YOUR_TOKEN>"
export DOWNLOADER_SERVICE_URL="http://localhost:8000"
python -m bot.main
```

Тепер надішліть боту посилання на YouTube – він запропонує завантажити аудіо чи відео, покаже прогрес й відправить файл.

## Архітектура

```
┌────────────┐            HTTP POST               ┌────────────────────┐
│Telegram API│◀──────────────────────────────────▶│Downloader Service  │
└────────────┘                                    └────────────────────┘
        ▲                                                  ▲
        │                                                  │
   Polling JSON                                            │
        │                                                  │
┌────────────┐                                    YouTube (yt-dlp)
│ Telegram   │
│ Bot        │
└────────────┘
```

* Додаткові мікросервіси (наприклад, кешування, аналітика) легко додаються, не торкаючи інших компонентів.