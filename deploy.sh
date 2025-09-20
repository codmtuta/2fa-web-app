#!/bin/bash
# Скрипт для быстрого развертывания 2FA веб-приложения

set -e

echo "🚀 Развертывание 2FA веб-приложения..."

# Проверяем наличие необходимых файлов
if [ ! -f "web_2fa_app.py" ]; then
    echo "❌ Файл web_2fa_app.py не найден!"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ Файл requirements.txt не найден!"
    exit 1
fi

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip install -r requirements.txt

# Проверяем переменные окружения
if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  SECRET_KEY не установлен. Используется значение по умолчанию."
    echo "   Рекомендуется установить: export SECRET_KEY='your-secret-key'"
fi

# Определяем платформу развертывания
if [ ! -z "$HEROKU_APP_NAME" ]; then
    echo "🔵 Обнаружена платформа Heroku"
    echo "   Приложение: $HEROKU_APP_NAME"
    echo "   Для развертывания выполните: git push heroku main"
elif [ ! -z "$RAILWAY_PROJECT_ID" ]; then
    echo "🚂 Обнаружена платформа Railway"
    echo "   Для развертывания выполните: railway up"
elif [ ! -z "$RENDER" ]; then
    echo "🎨 Обнаружена платформа Render"
    echo "   Приложение будет развернуто автоматически"
else
    echo "🖥️  Локальное развертывание"
    
    # Проверяем наличие Gunicorn
    if ! command -v gunicorn &> /dev/null; then
        echo "📦 Установка Gunicorn..."
        pip install gunicorn
    fi
    
    # Запускаем приложение
    echo "🚀 Запуск приложения..."
    echo "   Доступно по адресу: http://localhost:5000"
    echo "   Для остановки нажмите Ctrl+C"
    
    # Определяем способ запуска
    if [ -f "gunicorn.conf.py" ]; then
        gunicorn --config gunicorn.conf.py wsgi:app
    else
        python web_2fa_app.py
    fi
fi

echo "✅ Развертывание завершено!"
