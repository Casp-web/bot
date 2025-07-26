# 🚀 Швидкий старт - Telegram Tkinter Client

## ⚡ Швидкий запуск

### 1. Встановлення залежностей
```bash
# Створення віртуального середовища
python3 -m venv telegram_env

# Активація середовища
source telegram_env/bin/activate

# Встановлення залежностей
pip install telethon
```

### 2. Отримання API ключів
1. Перейдіть на https://my.telegram.org
2. Увійдіть зі своїм номером телефону
3. Створіть новий додаток
4. Скопіюйте `api_id` та `api_hash`

### 3. Запуск клієнта
```bash
# Через launcher (рекомендовано)
python3 run_telegram_client.py

# Або напряму
python3 telegram_client.py              # Basic версія
python3 telegram_client_advanced.py     # Advanced версія
```

## 📋 Що включено

### Basic Client (`telegram_client.py`)
- ✅ Авторизація в Telegram
- ✅ Перегляд чатів
- ✅ Відправка/отримання повідомлень
- ✅ Збереження налаштувань

### Advanced Client (`telegram_client_advanced.py`)
- ✅ Всі функції Basic Client
- ✅ Пошук по чатах
- ✅ Експорт повідомлень
- ✅ Покращений інтерфейс
- ✅ Меню з додатковими опціями

## 🔧 Тестування

Запустіть тести для перевірки функціональності:
```bash
python3 test_telegram_client.py
```

## 📁 Структура файлів

```
telegram-tkinter-client/
├── telegram_client.py              # Basic клієнт
├── telegram_client_advanced.py     # Advanced клієнт
├── run_telegram_client.py          # Launcher
├── test_telegram_client.py         # Тести
├── requirements.txt                # Залежності
├── TELEGRAM_CLIENT_SETUP.md        # Детальні інструкції
├── README_TELEGRAM_CLIENT.md       # Повна документація
└── QUICK_START.md                  # Цей файл
```

## 🛠️ Вирішення проблем

### Проблема: "No module named 'tkinter'"
```bash
sudo apt install python3-tk
```

### Проблема: "externally-managed-environment"
```bash
python3 -m venv telegram_env
source telegram_env/bin/activate
pip install telethon
```

### Проблема: "No module named 'telethon'"
```bash
source telegram_env/bin/activate
pip install telethon
```

## 🎯 Наступні кроки

1. **Отримайте API ключі** з https://my.telegram.org
2. **Запустіть клієнт** через launcher
3. **Введіть дані** для авторизації
4. **Насолоджуйтесь** використанням!

## 📞 Підтримка

- 📖 Повна документація: `README_TELEGRAM_CLIENT.md`
- 🔧 Детальні інструкції: `TELEGRAM_CLIENT_SETUP.md`
- 🧪 Тестування: `test_telegram_client.py`

---

**Готово! Ваш Telegram Tkinter Client готовий до використання! 🎉**