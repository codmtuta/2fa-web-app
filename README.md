# 🔐 2FA Generator - Telegram Bot & Web App

Полнофункциональное приложение для генерации 2FA кодов с поддержкой Telegram бота и веб-интерфейса. Аналог BrowserScan 2FA для Telegram.

## 🚀 Возможности

### Telegram Bot
- ✅ **Web App интеграция** - кнопка "Open" в списке чатов
- ✅ **Генерация TOTP кодов** в реальном времени
- ✅ **Управление ключами** через команды
- ✅ **Автоматическое определение** секретных ключей
- ✅ **Демонстрационный режим** с тестовым ключом

### Web Application
- ✅ **Современный интерфейс** с адаптивным дизайном
- ✅ **Множественные ключи** (до 10 на сессию)
- ✅ **Автообновление кодов** каждые 30 секунд
- ✅ **QR-коды** для добавления в аутентификаторы
- ✅ **Валидация кодов** в реальном времени
- ✅ **Экспорт/импорт** ключей

### Безопасность
- ✅ **Локальное хранение** ключей
- ✅ **HTTPS** для всех соединений
- ✅ **CORS** настройки для Telegram
- ✅ **Валидация** секретных ключей

## 📱 Telegram Web App Setup

### Шаг 1: Создание бота
1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Введите имя и username для бота
4. Получите токен бота

### Шаг 2: Настройка Web App
1. Отправьте команду `/setmenubutton` боту @BotFather
2. Выберите вашего бота
3. Введите текст кнопки: "🌐 2FA Web App"
4. Введите URL вашего сайта: `https://your-app-name.onrender.com`

### Шаг 3: Настройка переменных окружения
Создайте файл `.env` на основе `env.example`:

```bash
# Настройки Telegram бота
TELEGRAM_BOT_TOKEN=your_bot_token_here
WEB_APP_URL=https://your-app-name.onrender.com

# Основные настройки
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this-in-production
PORT=5000

# Настройки безопасности
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Strict

# CORS настройки
CORS_ORIGINS=https://your-app-name.onrender.com
```

## 🚀 Быстрый старт

### Локальный запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск веб-приложения
python web_2fa_app.py

# Запуск Telegram бота (в отдельном терминале)
python telegram_2fa_bot.py
```

### Развертывание на Render

1. **Подключите репозиторий** к Render
2. **Создайте Web Service** с настройками:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python web_2fa_app.py`
3. **Добавьте переменные окружения** из `.env`
4. **Деплой** приложения

## 🎯 Использование

### Telegram Bot команды

- `/start` - Главное меню с кнопкой Web App
- `/demo` - Демонстрация с тестовым ключом
- `/add <ключ>` - Добавить секретный ключ
- `/list` - Показать сохраненные ключи
- `/generate <номер>` - Сгенерировать код
- `/remove <номер>` - Удалить ключ
- `/web` - Открыть веб-версию

### Web App функции

- **Добавление ключей** через интерфейс
- **Генерация кодов** в реальном времени
- **QR-коды** для импорта в аутентификаторы
- **Валидация кодов** перед использованием
- **Управление множественными ключами**

## 🔧 API Endpoints

### Основные endpoints

- `POST /api/generate` - Генерация 2FA кода
- `POST /api/validate` - Валидация кода
- `POST /api/add_key` - Добавление ключа
- `POST /api/remove_key` - Удаление ключа
- `GET /api/get_keys` - Получение всех ключей
- `GET /api/demo` - Демонстрационный режим

### Примеры использования

```javascript
// Генерация кода
fetch('/api/generate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        secret_key: 'JBSWY3DPEHPK3PXP',
        session_id: 'user123'
    })
});

// Добавление ключа
fetch('/api/add_key', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        secret_key: 'JBSWY3DPEHPK3PXP',
        name: 'My Account',
        session_id: 'user123'
    })
});
```

## 📁 Структура проекта

```
├── telegram_2fa_bot.py      # Telegram бот
├── web_2fa_app.py          # Веб-приложение Flask
├── totp_generator.py       # Генератор TOTP кодов
├── secure_storage.py       # Безопасное хранение
├── login_generator.py      # Генератор логинов
├── templates/
│   ├── 2fa_web.html       # Веб-интерфейс
│   └── index.html         # Главная страница
├── static/
│   └── style.css          # Стили
├── requirements.txt        # Зависимости Python
├── env.example           # Пример переменных окружения
└── README.md             # Документация
```

## 🛠️ Требования

- Python 3.8+
- Flask
- python-telegram-bot
- pyotp
- qrcode

## 🔒 Безопасность

- Все ключи хранятся локально в сессии
- HTTPS обязательно для Telegram Web App
- CORS настроен для работы с Telegram
- Валидация всех входных данных

## 📞 Поддержка

При возникновении проблем:

1. Проверьте настройки в BotFather
2. Убедитесь в доступности сайта по HTTPS
3. Проверьте переменные окружения
4. Посмотрите логи приложения

## 🎉 Готово!

Теперь у вас есть полнофункциональный 2FA генератор с:
- **Telegram ботом** с кнопкой "Open"
- **Веб-приложением** с современным интерфейсом
- **Полной интеграцией** между ботом и сайтом

Удачного использования! 🚀