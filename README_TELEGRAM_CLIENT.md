# Telegram Tkinter Client

Простий Telegram клієнт, створений на Python з використанням tkinter та бібліотеки Telethon.

## 📋 Зміст

- [Опис](#опис)
- [Функції](#функції)
- [Встановлення](#встановлення)
- [Налаштування](#налаштування)
- [Використання](#використання)
- [Файли проекту](#файли-проекту)
- [Скріншоти](#скріншоти)
- [Розробка](#розробка)

## 📖 Опис

Цей проект містить два варіанти Telegram клієнта:

1. **Basic Client** (`telegram_client.py`) - простий клієнт з базовим функціоналом
2. **Advanced Client** (`telegram_client_advanced.py`) - розширений клієнт з додатковими можливостями

## ✨ Функції

### Basic Client
- ✅ Авторизація в Telegram
- ✅ Перегляд списку чатів
- ✅ Читання та відправка повідомлень
- ✅ Отримання повідомлень в реальному часі
- ✅ Збереження налаштувань

### Advanced Client
- ✅ Всі функції Basic Client
- ✅ Пошук по чатах
- ✅ Експорт повідомлень
- ✅ Покращений інтерфейс з TreeView
- ✅ Меню з додатковими опціями
- ✅ Налаштування
- ✅ Інформація про чат

## 🚀 Встановлення

### 1. Клонування репозиторію
```bash
git clone <repository-url>
cd telegram-tkinter-client
```

### 2. Встановлення залежностей
```bash
pip install -r requirements.txt
```

### 3. Отримання API ключів
1. Перейдіть на https://my.telegram.org
2. Увійдіть зі своїм номером телефону
3. Перейдіть до "API development tools"
4. Створіть новий додаток:
   - **App title**: Будь-яка назва (наприклад, "My Tkinter Client")
   - **Short name**: Коротка назва (наприклад, "tkclient")
   - **Platform**: Desktop
   - **Description**: Опис додатку
5. Скопіюйте `api_id` та `api_hash`

## ⚙️ Налаштування

### Запуск через Launcher (рекомендовано)
```bash
python run_telegram_client.py
```

### Прямий запуск
```bash
# Basic Client
python telegram_client.py

# Advanced Client
python telegram_client_advanced.py
```

## 📱 Використання

### 1. Авторизація
- Введіть API ID, API Hash та номер телефону
- Натисніть "Login"
- Введіть код підтвердження з Telegram

### 2. Робота з чатами
- Після авторизації завантажиться список чатів
- Виберіть чат для перегляду повідомлень
- У Advanced Client можна використовувати пошук

### 3. Відправка повідомлень
- Виберіть чат
- Введіть повідомлення
- Натисніть "Send" або Enter

### 4. Додаткові функції (Advanced Client)
- **Пошук**: Введіть назву чату в поле пошуку
- **Експорт**: File → Export Messages
- **Налаштування**: File → Settings
- **Очищення**: Chat → Clear Messages

## 📁 Файли проекту

```
telegram-tkinter-client/
├── telegram_client.py              # Basic клієнт
├── telegram_client_advanced.py     # Advanced клієнт
├── run_telegram_client.py          # Launcher
├── requirements.txt                # Залежності
├── TELEGRAM_CLIENT_SETUP.md        # Інструкції налаштування
├── README_TELEGRAM_CLIENT.md       # Цей файл
├── telegram_config.json            # Налаштування (створюється автоматично)
└── session_name.session            # Сесія Telegram (створюється автоматично)
```

## 🖼️ Скріншоти

### Basic Client
```
┌─────────────────────────────────────────────────────────┐
│                    Telegram Client                      │
├─────────────────────────────────────────────────────────┤
│ Login:                                                  │
│ API ID: [123456]  API Hash: [********]  Phone: [+380...]│
│ [Login] [Logout]                           Not connected│
├─────────────────────────────────────────────────────────┤
│ Chats:                    │ Messages:                   │
│ ┌─────────────────────┐   │ ┌─────────────────────────┐ │
│ │ • Chat 1            │   │ │ [12:30] User: Hello!    │ │
│ │ • Chat 2            │   │ │ [12:31] Me: Hi there!   │ │
│ │ • Chat 3            │   │ │                         │ │
│ └─────────────────────┘   │ └─────────────────────────┘ │
│                           │ [Message: ________] [Send]  │
└─────────────────────────────────────────────────────────┘
```

### Advanced Client
```
┌─────────────────────────────────────────────────────────────────┐
│ File  Chat  Help                                                │
├─────────────────────────────────────────────────────────────────┤
│                    Telegram Login                               │
│ API ID: [123456]  API Hash: [********]  Phone: [+380...]        │
│ [Login] [Logout]                                   Connected    │
├─────────────────────────────────────────────────────────────────┤
│ Search:                    │ Chat Info:                         │
│ [Search chats...]          │ Chat: John Doe (User)              │
│                            │                                     │
│ Chats:                     │ Messages:                           │
│ ┌─────────────────────┐   │ ┌─────────────────────────────────┐ │
│ │ Name        │ Type  │   │ │ [2024-01-15 12:30] John: Hello! │ │
│ │ John Doe    │ User  │   │ │ [2024-01-15 12:31] Me: Hi!      │ │
│ │ Group Chat  │ Chat  │   │ │                                 │ │
│ └─────────────────────┘   │ └─────────────────────────────────┘ │
│                           │ [Message: ________] [Send]          │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Розробка

### Структура коду

#### Основні класи
- `TelegramTkinterClient` - базовий клієнт
- `AdvancedTelegramClient` - розширений клієнт

#### Ключові методи
- `login()` - авторизація
- `load_chats()` - завантаження чатів
- `load_messages()` - завантаження повідомлень
- `send_message()` - відправка повідомлень

### Додавання нових функцій

1. **Підтримка медіафайлів**:
```python
async def download_media(self, message):
    if message.media:
        path = await self.client.download_media(message.media)
        return path
```

2. **Пошук по повідомленнях**:
```python
def search_messages(self, query):
    results = [msg for msg in self.messages if query.lower() in msg['text'].lower()]
    return results
```

3. **Теми інтерфейсу**:
```python
def apply_theme(self, theme_name):
    if theme_name == "dark":
        self.root.configure(bg='black')
        # Apply dark theme styles
```

## 🛡️ Безпека

⚠️ **Важливі застереження:**

- Не передавайте API ключі третім особам
- Файл `telegram_config.json` містить конфіденційні дані
- Файл `session_name.session` містить дані авторизації
- Використовуйте віртуальне середовище для ізоляції залежностей

## 📝 Ліцензія

Цей проект розповсюджується під ліцензією MIT.

## 🤝 Внесок

Вітаються внески! Будь ласка:

1. Форкніть репозиторій
2. Створіть гілку для нової функції
3. Зробіть коміт змін
4. Відправте Pull Request

## 📞 Підтримка

Якщо у вас виникли питання або проблеми:

1. Перевірте [TELEGRAM_CLIENT_SETUP.md](TELEGRAM_CLIENT_SETUP.md)
2. Створіть Issue в репозиторії
3. Перевірте, чи всі залежності встановлені

## 🔄 Оновлення

Для оновлення клієнта:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

---

**Насолоджуйтесь використанням Telegram Tkinter Client!** 🚀